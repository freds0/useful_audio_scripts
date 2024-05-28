import argparse
import librosa
import soundfile as sf
import numpy as np
from tqdm import tqdm
import os

def segment_wav(input_file, output_dir, duration):

    filename = os.path.basename(input_file)
    y, sr = librosa.load(input_file, sr=None)

    segment_size = int(duration * sr)
    num_segments = int(len(y) // segment_size)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for i in tqdm(range(num_segments)):
        start_sample = i * segment_size
        end_sample = (i + 1) * segment_size
        segment = y[start_sample:end_sample]
   
        output_file = os.path.join(output_dir, f'{filename}-{i:04d}.wav')
        sf.write(output_file, segment, sr, subtype='PCM_16')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True, help="Input filepath")
    parser.add_argument('--output_dir', default="output", help="Output folder")
    parser.add_argument('--duration', type=float, default=15.0, help='Maximum duration in seconds for each segment')
    args = parser.parse_args()

    segment_wav(args.input, args.output_dir, args.duration)


if __name__ == "__main__":
    main()