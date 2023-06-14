#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import torchaudio
from os import makedirs
from os.path import join, basename
from tqdm import tqdm
from glob import glob

def convert_file(input_filepath, output_filepath, target_sr,  force):
    # Read data
    waveform, orig_sr = torchaudio.load(input_filepath)
    original_sr = int(orig_sr)

    if not force:
        print(f"conv {input_filepath} {orig_sr} {output_filepath} {target_sr}")

    else:
        # Convert data        
        fn_resample = torchaudio.transforms.Resample(orig_freq=orig_sr, new_freq=target_sr, resampling_method='sinc_interp_hann')
        target_waveform = fn_resample(waveform)
        torchaudio.save(output_filepath, target_waveform, target_sr, encoding="PCM_S", bits_per_sample=16, format='wav')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', default='input', help='Input folder')
    parser.add_argument('-o', '--output', default='output', help='Output folder')
    parser.add_argument('-s', '--sr', default=44100, type=int)
    parser.add_argument('-f', '--force', action='store_true', default=False)
    args = parser.parse_args()

    makedirs(args.output, exist_ok = True)    
    for input_filepath in tqdm(glob(join(args.input, '*.mp3'))):
        output_filepath = join(args.output, basename(input_filepath))
        convert_file(input_filepath, output_filepath, args.sr, args.force)


if __name__ == "__main__":
    main()
