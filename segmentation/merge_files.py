# import required libraries
from pydub import AudioSegment
from pydub.playback import play
import argparse
from glob import glob
import os
import numpy as np


def merge_audio_files(wavs_dir, output_file, gap):

    merged_audio_data = 0
    silence = 0    
    for filepath in sorted(glob(wavs_dir + '/*.wav'), key=os.path.basename):
        audio_data = AudioSegment.from_file(filepath)           
        # Combine the two audio files 
        merged_audio_data = merged_audio_data + silence + audio_data
        silence = AudioSegment.silent(duration=gap)

    # Increase the volume by 10 decibels 
    merged_audio_data += 5

    # Export louder audio file 
    merged_audio_data.export(out_f = output_file, format = "wav")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--base_dir', default='./')
    parser.add_argument('-i', '--input', default='input')
    parser.add_argument('-o', '--output', default='output.wav')
    parser.add_argument('-g', '--gap', default=50)
    args = parser.parse_args()
    merge_audio_files(args.input, args.output, int(args.gap))

if __name__ == "__main__":
    main()
