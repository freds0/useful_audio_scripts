#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import torchaudio
from os import makedirs
from os.path import join, basename
from tqdm import tqdm
from glob import glob

def convert_file(input_filepath, output_filepath, force):
    # Read data
    waveform, sr = torchaudio.load(input_filepath)

    if not force:
        print(f"conv {input_filepath} {output_filepath}")

    else:
        torchaudio.save(output_filepath, waveform, int(sr), encoding="PCM_S", bits_per_sample=16, format='wav')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', default='input', help='Input folder')
    parser.add_argument('-o', '--output', default='output', help='Output folder')
    parser.add_argument('-f', '--force', action='store_true', default=False)
    args = parser.parse_args()
    
    if args.force:
        makedirs(args.output, exist_ok=True)
    for input_filepath in tqdm(glob(join(args.input, '*.ogg'))): 
        output_filepath = join(args.output, basename(input_filepath))
        output_filepath = output_filepath.replace('.ogg', '.wav')
        convert_file(input_filepath, output_filepath, args.force)

if __name__ == "__main__":
    main()
