import argparse
from os.path import join, basename
from os import makedirs
from tqdm import tqdm
import numpy as np
from pydub import AudioSegment
from glob import glob


def normalize_audios(input_path, output_path, target_dbfs):

    makedirs(output_path, exist_ok=True)

    for audio_file in tqdm(glob(input_path + '/*.wav', recursive=True)):

        filename = basename(audio_file)
        dest_file = join(output_path, filename)

        sound = AudioSegment.from_file(audio_file)
        change_in_dBFS = target_dbfs - sound.dBFS
        normalized_sound = sound.apply_gain(change_in_dBFS)
        normalized_sound.export(dest_file, format=dest_file[-3:])


def calculate_mean_dbfs(input_path):

    dbfs_list = []
    for audio_file in glob(input_path + '/*.wav', recursive=True):
        dbfs_list.append(AudioSegment.from_file(audio_file).dBFS)

    target_dbfs = np.array(dbfs_list).mean()
    return target_dbfs


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--base_dir', default='./')
    parser.add_argument('-i', '--input', default='input')
    parser.add_argument('-o', '--output', default='output')
    args = parser.parse_args()

    input_dir = join(args.base_dir, args.input)
    output_dir = join(args.base_dir, args.output)
    print('Calculating mean dBfs...')
    mean_dbfs = calculate_mean_dbfs(input_dir)
    print("Mean DBFS:", mean_dbfs)
    print('Normalizing audios...')
    normalize_audios(input_dir, output_dir, mean_dbfs)


if __name__ == "__main__":
    main()
