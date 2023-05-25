#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
from glob import glob
from os import makedirs
from os.path import join, basename
from tqdm import tqdm
import librosa
import soundfile as sf

def convert_file(input_filepath, output_filepath, target_sr = 44100, force = False):
    # Read data
    data, orig_sr = librosa.load(input_filepath, sr=None)
    orig_sr = int(orig_sr)

    if orig_sr < target_sr:
        print(f"Original sr {orig_sr} is lower then target sr {target_sr}")

    elif orig_sr == target_sr:
        print(f"Original sr {orig_sr} is equal to target sr {target_sr}")

    elif not force:
        print(f"conv {input_filepath} {orig_sr} {output_filepath} {target_sr}")

    else:
        # Convert data
        converted_data = librosa.resample(y = data, orig_sr = orig_sr, target_sr = target_sr)
        sf.write(output_filepath, converted_data, target_sr)            


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', default='input')
    parser.add_argument('-o', '--output', default='output', help='Output folder')
    parser.add_argument('-s', '--sr', default=44100, type=int)
    parser.add_argument('-f', '--force', action='store_true', default=False)
    args = parser.parse_args()

    makedirs(args.output, exist_ok = True)    
    for input_filepath in tqdm(glob(join(args.input, '*.wav'))):
        output_filepath = join(args.output, basename(input_filepath))
        convert_file(input_filepath, output_filepath, args.sr, args.force)


if __name__ == "__main__":
    main()
