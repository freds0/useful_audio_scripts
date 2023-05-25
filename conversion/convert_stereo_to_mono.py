#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
from glob import glob
from os import makedirs
from os.path import join, basename
import torchaudio
import torch
from tqdm import tqdm

def convert_stereo_to_mono(input_filepath, output_filepath, force):
    if force:
        waveform, sr = torchaudio.load(input_filepath)
        mono_waveform = torch.mean(waveform, dim=0, keepdim=True)
        torchaudio.save(output_filepath, mono_waveform, sr, encoding="PCM_S", bits_per_sample=16)
    else:
        print(f"conv {input_filepath} {output_filepath}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', default='input', help='Input folder')
    parser.add_argument('-o', '--output', default='output', help='Output folder')
    parser.add_argument('-f', '--force', action='store_true', default=False)
    args = parser.parse_args()

    makedirs(args.output, exist_ok = True)    
    for input_filepath in tqdm(glob(join(args.input, '*.wav'))):
        output_filepath = join(args.output, basename(input_filepath))
        convert_stereo_to_mono(input_filepath, output_filepath, args.force)


if __name__ == "__main__":
    main()
