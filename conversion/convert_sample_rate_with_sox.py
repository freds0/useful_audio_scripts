#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
from glob import glob
import subprocess
from os import makedirs
from os.path import join, basename
from tqdm import tqdm

number_bits = 16
encoding = "signed-integer"
number_channels = 1

def convert_file(input_filepath, output_filepath, sr = 44100, force = False):
        command_line = "sox %s -V0 -c %d -r %d -b %d -e %s %s"% (input_filepath, int(number_channels), int(sr), number_bits, encoding, output_filepath)
        if force:
            subprocess.call(command_line, shell=True)
        else:
            print(command_line)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', default='input', help='Input folder')
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
