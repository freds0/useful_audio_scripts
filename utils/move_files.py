import argparse
import glob
from os import makedirs
from os.path import join, exists, basename, dirname
import tqdm
import numpy as np
from shutil import move

def move_file(input_filepath, output_filepath, force=False):
    if force:
        move(input_filepath, output_filepath)
    else:
        print("mv {} {}\n".format(input_filepath, output_filepath))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--base_dir', default='./')
    parser.add_argument('-i', '--input', default='input', help='Input folder')
    parser.add_argument('-o', '--output', default='output', help='Output folder')
    parser.add_argument('-f', '--force', action='store_true', default=False)
    args = parser.parse_args()

    input_dir = join(args.base_dir, args.input)

    for input_filepath in tqdm.tqdm(sorted(glob.glob(input_dir + "/**/*.wav"))):
        output_dir = join(args.base_dir, args.output)
        folder = dirname(input_filepath).split("/")[2]
        output_dir = join(output_dir, 'DAMP-RADTTS_' + folder)
        if (not(exists(output_dir)) and (args.force)):
            makedirs(output_dir)

        filename = basename(input_filepath)
        output_filepath = join(output_dir, filename)
        move_file(input_filepath, output_filepath, args.force)


if __name__ == "__main__":
    main()
