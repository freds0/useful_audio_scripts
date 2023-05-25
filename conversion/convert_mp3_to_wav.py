#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import subprocess
from glob import glob
from os import makedirs
from os.path import join, basename
from tqdm import tqdm

def convert_file(input_filepath, output_filepath, target_sr = 44100, force = False):
    command_line = "ffmpeg -i {} -ar {}  {}" .format(input_filepath, target_sr, output_filepath)  
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
    for input_filepath in tqdm(glob(join(args.input, '*.mp3'))):
        output_filepath = join(args.output, basename(input_filepath).replace('.mp3', '.wav'))
        convert_file(input_filepath, output_filepath, args.sr, args.force)


if __name__ == "__main__":
    main()
