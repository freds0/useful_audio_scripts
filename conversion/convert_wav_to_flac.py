#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import subprocess
from os import listdir, makedirs
from os.path import isfile, join, basename, splitext
from tqdm import tqdm
from glob import glob

def convert_file(input_filepath, output_filepath, force=False):
    if not force:
        command_line = "conv {} {}".format(input_filepath, output_filepath)
        print(command_line)
    else:
        # Use subprocess to call the "flac" command-line tool to convert WAV to FLAC
        subprocess.run(["flac", input_filepath, "-o", output_filepath])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', default='input', help='Input folder')
    parser.add_argument('-o', '--output', default='output', help='Output folder')
    parser.add_argument('-f', '--force', action='store_true', default=False)
    args = parser.parse_args()

    makedirs(args.output, exist_ok=True)
    for input_filepath in tqdm(glob(join(args.input, '*.wav'))):  # Change '*.flac' to '*.wav' to process WAV files
        output_filepath = join(args.output, splitext(basename(input_filepath))[0] + '.flac')  # Change '.wav' to '.flac' for output files
        convert_file(input_filepath, output_filepath, force=args.force)

if __name__ == "__main__":
    main()
