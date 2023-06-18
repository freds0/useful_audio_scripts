#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Adapted from https://gist.github.com/keithito/771cfc1a1ab69d1957914e377e65b6bd from Keith Ito: kito@kito.us
#
import argparse
import sys
from glob import glob
from os import listdir, makedirs
from os.path import isfile, join, basename
from collections import OrderedDict
from scipy.io.wavfile import write
import librosa
import pydub
import numpy as np
from tqdm import tqdm 

class Segment:
    '''
    Linked segments lists
    '''
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.next = None
        self.gap = 0 # gap between segments (current and next)

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


def segment_wav(audio_data, threshold_db):
    '''
    Segment audio file and return a segment linked list
    '''
    # Find gaps at a fine resolution:
    parts = librosa.effects.split(audio_data, top_db=threshold_db, frame_length=1024, hop_length=256)

    # Build up a linked list of segments:
    head = None
    for start, end in parts:
        segment = Segment(start, end)
        if head is None:
            head = segment
        else:
            prev.set_next(segment)
        prev = segment
    return head


def find_best_merge(segments, sample_rate, max_duration, max_gap_duration):
    '''
    Find small segments that can be merged by analyzing max_duration and max_gap_duration
    '''
    best = None
    best_score = 0
    s = segments
    while s.next is not None:
        gap_duration = s.gap / sample_rate
        merged_duration = (s.next.end - s.start) / sample_rate
        if gap_duration <= max_gap_duration and merged_duration <= max_duration:
            score = max_gap_duration - gap_duration
            if score > best_score:
                best = s
                best_score = score
        s = s.next
    return best


def find_segments(filename, wav, sample_rate, min_duration, max_duration, max_gap_duration, threshold_db, output_dir):
    '''
    Given an audio file, creates the best possible segment list
    '''
    # Segment audio file
    segments = segment_wav(wav, threshold_db)
    # Merge until we can't merge any more
    while True:
        best = find_best_merge(segments, sample_rate, max_duration, max_gap_duration)
        if best is None:
            break
        best.merge_from(best.next)

    # Convert to list
    result = []
    s = segments
    while s is not None:
        result.append(s)
        # Create a errors file
        if (s.duration(sample_rate) < min_duration and s.duration(sample_rate) > max_duration):
                with open(join(output_dir, "errors.txt"), "a") as f:
                        f.write(filename+"\n")
        # Extend the end by 0.2 sec as we sometimes lose the ends of words ending in unvoiced sounds.
        s.end += int(0.2 * sample_rate)
        s = s.next

    return result


def load_filenames(input_dir):
    '''
    Given an folder, creates a wav file alphabetical order dict
    '''
    mappings = OrderedDict()
    for filepath in sorted(glob(input_dir + "/*.wav")):
        filename = basename(filepath).split('.')[0]
        mappings[filename] = filepath
    return mappings


def build_segments(input_dir, output_dir, min_duration, max_duration, max_gap_duration, threshold_db, args_filename, args_filename_id):
    '''
    Build best segments of wav files
    '''
    # Initializes variables
    total_duration, mean_duration_seg, max_duration_seg, min_duration_seg = 0, 0, 0, 999
    all_segments = []
    init_filename_id = args_filename_id if args_filename_id else 1
    filenames = load_filenames(input_dir)
    for i, (file_id, filename) in enumerate(tqdm(filenames.items())):
        print(f'Loading {file_id}: {filename} ({i+1} of {len(filename)})')
        wav, sample_rate = librosa.load(filename, sr=None)
        audio_duration = len(wav) / sample_rate / 60
        print(f' -> Loaded {audio_duration} min of audio. Splitting...')

        # Find best segments
        segments = find_segments(filename, wav, sample_rate, min_duration, max_duration, max_gap_duration, threshold_db, output_dir)
        duration = sum((s.duration(sample_rate) for s in segments))
        total_duration += duration

        # Create records for the segments
        output_filename = args_filename if args_filename else file_id
        output_filename_id = init_filename_id
        for s in segments:
            all_segments.append(s)
            s.set_filename_and_id(filename, '%s-%04d' % (output_filename, output_filename_id))
            output_filename_id += 1

        print(' -> Segmented into %d parts (%.1f min, %.2f sec avg)' % (len(segments), duration / 60, duration / len(segments)))

        # Write segments to disk:
        for s in segments:
            segment_wav = (wav[s.start:s.end] * 32767).astype(np.int16)
            out_path = join(output_dir, f'{s.id}.wav')
            write(out_path, sample_rate, segment_wav)

            duration += len(segment_wav) / sample_rate
            duration_segment = len(segment_wav) / sample_rate
            
            if duration_segment > max_duration_seg:
                max_duration_seg = duration_segment
            elif duration_segment < min_duration_seg:
                min_duration_seg = duration_segment

            mean_duration_seg += duration_segment

        mean_duration_seg /= len(segments)

        print(' -> Wrote %d segment wav files' % len(segments))
        print(' -> Progress: %d segments, %.2f hours, %.2f sec avg' % (
            len(all_segments), total_duration / 3600, total_duration / len(all_segments)))

    print('Writing metadata for %d segments (%.2f hours)' % (len(all_segments), total_duration / 3600))
    with open(join(output_dir, 'segments.csv'), 'w') as f:
        for s in all_segments:
            f.write('%s|%s|%d|%d\n' % (s.id, s.filename, s.start, s.end))
 
    print('Min: %d' %(min_duration_seg))
    print('Mean: %f' %(mean_duration_seg))
    print('Max: %d' %(max_duration_seg))

def convert_mp3_to_wav(input_mp3, output_wav):
        '''
        Convert mp3 folder files to wav
        '''
        mp3files = [f for f in listdir(input_mp3) if isfile(input_mp3, f)]
        makedirs(output_wav, exist_ok=True)
        for mp3 in mp3files:
            sound = pydub.AudioSegment.from_mp3(join(input_mp3, mp3))
            filename = mp3.split('.')[0]
            sound.export(join(output_wav, f'{filename}.wav'), format="wav")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default='input', help='Input wav folder')
    parser.add_argument('--output', default='output', help='Output wav folder')
    parser.add_argument('--input_mp3', default=None, help='Input mp3 folder')
    parser.add_argument('--min_duration', type=float, default=5.0, help='Minimum duration of a segment in seconds')
    parser.add_argument('--max_duration', type=float, default=15.0, help='Maximum duration of a segment in seconds')
    parser.add_argument('--max_gap_duration', type=float, default=3.0, help='Maximum duration of a gap between segments in seconds')
    parser.add_argument('--output_filename', type=str, default='', help='Default output filename')
    parser.add_argument('--output_filename_id', type=int, default=1, help='Sequencial number used for id filename.')
    parser.add_argument('--threshold_db', type=float, default=28.0, help='The threshold (in decibels) below reference to consider as silence: ')
    args = parser.parse_args()

    makedirs(args.output, exist_ok=True)

    #convert_mp3_to_wav(args.input_mp3, args.output)
    build_segments(args.input, args.output, args.min_duration, args.max_duration, args.max_gap_duration, args.threshold_db, args.output_filename, args.output_filename_id)


if __name__ == "__main__":
    main()
