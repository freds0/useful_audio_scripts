#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pydub
import argparse
import subprocess
from os import listdir, makedirs
from os.path import isfile, join, basename
from tqdm import tqdm
from glob import glob

def convert_file(input_filepath, output_filepath, tool = 'pydub', force = False):    
    if not force:
        command_line = "conv {} {}" .format(input_filepath, output_filepath)
        print(command_line)

    elif tool == 'lame':
        command_line = "lame {} {}" .format(input_filepath, output_filepath)
        subprocess.call(command_line, shell=True)

    elif tool == 'pydub':
        '''
        y = np.int16(sound)
        song = pydub.AudioSegment(y.tobytes(), frame_rate=22050)
        song.export(output_mp3_filepath, format="mp3", bitrate="128k")
        '''
        sound = pydub.AudioSegment.from_wav(input_filepath)
        sound.export(output_filepath, format="mp3")
        
       
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', default='input', help='Input folder')
    parser.add_argument('-o', '--output', default='output', help='Output folder')
    parser.add_argument('-t', '--tool', default='pydub', help='Available tools: pydub or lame', type=str)
    parser.add_argument('-f', '--force', action='store_true', default=False)
    args = parser.parse_args()

    makedirs(args.output, exist_ok = True)    
    for input_filepath in tqdm(glob(join(args.input, '*.wav'))):
        output_filepath = join(args.output, basename(input_filepath).replace('.wav', '.mp3'))
        convert_file(input_filepath, output_filepath, tool=args.tool, force=args.force)


if __name__ == "__main__":
    main()
