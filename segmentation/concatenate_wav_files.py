import os
import argparse
import pandas as pd
import numpy as np
from scipy.io.wavfile import read, write
import torchaudio
import tqdm
import csv
import torch
import librosa

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

class Segment:
    '''
    Linked segments lists
    '''
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.next = None
        self.gap = 0  # gap between segments (current and next)

    def set_next(self, next):
        self.next = next
        self.gap = next.start - self.end

    def set_filename_and_id(self, filename, id):
        self.filename = filename
        self.id = id

    def merge_from(self, next):
        # merge two segments (current and next)
        self.next = next.next
        self.gap = next.gap
        self.end = next.end

    def duration(self, sample_rate):
        return (self.end - self.start - 1) / sample_rate


def load_segments(filename):
    '''
    Read segments from csv file and recreate a segments list
    '''
    df = pd.read_csv(filename, sep='|', header=None, quoting=csv.QUOTE_NONE)
    total = 0
    head = None
    for index, row in tqdm.tqdm(df.iterrows(), total=len(df[0])):
        # Build up a linked list of segments:
        segment = Segment(df.iloc[index, 2], df.iloc[index, 3])
        segment.set_filename_and_id(df.iloc[index, 1], df.iloc[index, 0])
        if head is None:
            head = segment
        else:
            prev.set_next(segment)
        prev = segment
        total += 1
    return head, total

def concatenate_wav_files(input_folder, output_folder, max_duration, sampling_rate=24000):
    '''
    Concatenate WAV files from input_folder up to max_duration and save segments to output_folder
    '''
    wav_files = [f for f in os.listdir(input_folder) if f.endswith('.flac')]
    wav_files.sort()

    segments = []
    current_duration = 0
    segment_id = 0
    concat_id = 0

    for wav_file in tqdm.tqdm(wav_files):
        file_path = os.path.join(input_folder, wav_file)
        #sr, wav_data = read(file_path)
        wav_data, sr = librosa.load(file_path, sr=None)
        #wav_data, sr = torchaudio.load(file_path)
        assert sr == sampling_rate, f"Sample rate mismatch: {sr} != {sampling_rate}"
        #wav_duration = wav_data.shape[1] / sr
        wav_duration = len(wav_data) / sr

        if current_duration + wav_duration <= max_duration:
            segments.append((file_path, segment_id, wav_duration))
            current_duration += wav_duration
        else:
            output_filepath = os.path.join(output_folder, f'concatenated-{concat_id}')
            write_segment_files(segments, output_filepath, sr)
            segments = [(file_path, segment_id, wav_duration)]
            current_duration = wav_duration
            concat_id += 1
        segment_id += 1

    if segments:
        output_filepath = os.path.join(output_folder, f'concatenated-{concat_id}')
        write_segment_files(segments, output_filepath, sr)

def write_segment_files(segments, output_filepath, sampling_rate):
    '''
    Write segment WAV files and corresponding CSV file
    '''
    os.makedirs(os.path.dirname(output_filepath), exist_ok=True)

    csv_data = []
    start_time = 0
    concatenated_audio_data = None
    for file_path, segment_id, duration in segments:
        #sr, wav_data = read(file_path)
        wav_data, sr = librosa.load(file_path, sr=None)
        #wav_data, sr = torchaudio.load(file_path)
        assert sr == sampling_rate, f"Sample rate mismatch: {sr} != {sampling_rate}"    
        segment_wav = (wav_data * 32767).astype(np.int16)
        #segment_wav = wav_data * 32767
        #segment_wav = segment_wav.clamp(-32768, 32767)
        #segment_wav = segment_wav.to(torch.int16)

        if concatenated_audio_data is None:
            concatenated_audio_data = segment_wav#.to(device)
        else:
            #concatenated_audio_data = torch.cat([concatenated_audio_data, segment_wav.to(device)], axis=1)
            concatenated_audio_data = np.concatenate([concatenated_audio_data, segment_wav])

        #write(os.path.join(output_folder, f'{segment_id}.wav'), sampling_rate, segment_wav)
        filename = os.path.basename(file_path)
        out_filename = os.path.basename(output_filepath + ".wav")
        csv_data.append((segment_id, filename, out_filename, start_time * sr, (start_time + duration)*sr))
        start_time += duration

    with open(output_filepath + '.csv', 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter='|', quoting=csv.QUOTE_NONE)
        writer.writerows(csv_data)

    #torchaudio.save(output_filepath + '.wav', concatenated_audio_data.to('cpu'), sampling_rate)
    #write(output_filepath + '.wav', sampling_rate, concatenated_audio_data.to('cpu').numpy())
    write(output_filepath + '.wav', sampling_rate, concatenated_audio_data)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_folder', required=True, help='Input folder containing WAV files')
    parser.add_argument('--output_folder', required=True, help='Output folder to save concatenated segments')
    parser.add_argument('--max_duration', type=float, default=600.0, help='Maximum duration in seconds for each segment')
    parser.add_argument('--sampling_rate', type=int, default=48000, help='Sampling rate')
    args = parser.parse_args()

    concatenate_wav_files(args.input_folder, args.output_folder, args.max_duration, args.sampling_rate)


if __name__ == "__main__":
    main()

