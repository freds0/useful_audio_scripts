#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pydub
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
        audio = pydub.AudioSegment.from_file(input_filepath, format="flac")
        audio.export(output_filepath, format="wav")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', default='input', help='Input folder')
    parser.add_argument('-o', '--output', default='output', help='Output folder')
    parser.add_argument('-f', '--force', action='store_true', default=False)
    args = parser.parse_args()

    makedirs(args.output, exist_ok=True)
    for input_filepath in tqdm(glob(join(args.input, '*.flac'))):
        output_filepath = join(args.output, splitext(basename(input_filepath))[0] + '.wav')
        convert_file(input_filepath, output_filepath, force=args.force)

if __name__ == "__main__":
    main()
