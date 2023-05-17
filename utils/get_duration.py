import argparse
import soundfile as sf
from os.path import isfile, join, dirname
import glob
import os
import tqdm

def get_seconds(x):
    f = sf.SoundFile(x)
    t = len(f) / f.samplerate
    return t


def calculate(input_dir):
    total = 0
    for filepath in tqdm.tqdm(glob.glob(input_dir + '/*.wav')):
        total += get_seconds(filepath)

    print('Total (sec): {}'.format(total))
    print('Hours: {}'.format(total/3600))
    print('Minutes: {}'.format(total%3600/60))
    print('Secondes: {}'.format( (total%3600)%60))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir',  help='Input folder')
    args = parser.parse_args()
    calculate(args.input_dir)


if __name__ == "__main__":
    main()

