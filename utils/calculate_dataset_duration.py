import argparse
import soundfile as sf
from os.path import isfile, join, dirname
import pandas as pd
import os
import csv
import tqdm

def get_seconds(x):   
    f = sf.SoundFile(x)
    t = len(f) / f.samplerate
    return t


def calculate(args):
    metadata = os.path.join(args.base_dir, args.csv_file)
    df = pd.read_csv(metadata, sep = '|', header=None, quoting=csv.QUOTE_NONE)
    total = 0
    for index, row in tqdm.tqdm(df.iterrows(), total=len(df[0])):
        path_file = 'wavs/' + row[0] + '.wav'
        temp = get_seconds(path_file)
        total += temp

    print('Total (sec): {}'.format(total))
    print('Hours: {}'.format(total/3600))
    print('Minutes: {}'.format(total%3600/60))
    print('Secondes: {}'.format( (total%3600)%60))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base_dir', default='./')
    parser.add_argument('--csv_file', default='metadata.csv', help='Name of csv file')
    args = parser.parse_args()
    calculate(args)


if __name__ == "__main__":
    main()
