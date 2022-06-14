import argparse
from glob import glob
import os
from os import makedirs
from os.path import join, exists, dirname, basename
from tqdm import tqdm

number_bits = 16
encoding = "signed-integer"
number_channels = 1

def convert_wavs(filepath, output_folder, sr = 22050, force = False):
        folder = dirname(filepath)
        filename = basename(filepath)
        output_filepath = join(output_folder, filename)
        if not exists(output_folder) and (force):
            makedirs(output_folder)
        if force:
            os.system("sox %s -V0 -c %d -r %d -b %d -e %s %s"% (filepath, int(number_channels), int(sr), number_bits, encoding, output_filepath))
        else:
            print("sox %s -V0 -c %d -r %d -b %d -e %s %s"% (filepath, int(number_channels), int(sr), number_bits, encoding, output_filepath))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--base_dir', default='./')
    parser.add_argument('-i', '--input', default='input', help='Input folder')
    parser.add_argument('-o', '--output', default='output', help='Output folder')
    parser.add_argument('-s', '--sr', default='22050')
    parser.add_argument('-f', '--force', action='store_true', default=False)

    args = parser.parse_args()
    output_folder = join(args.base_dir, args.output)
    for filepath in tqdm(sorted(glob(join(args.base_dir, args.input + '/*.wav')))):
        convert_wavs(filepath, output_folder, args.sr, args.force)


if __name__ == "__main__":
    main()
