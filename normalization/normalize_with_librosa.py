import argparse
from os.path import join, basename, dirname, exists
from os import makedirs
from tqdm import tqdm
import numpy as np
from glob import glob
import librosa
import soundfile as sf

def normalize_audios(input_path, output_path, force=False):

    makedirs(output_path, exist_ok=True)

    for input_filepath in tqdm(glob(input_path + '/*.wav', recursive=True)):
        folder = dirname(input_filepath).split("/")[2]
        filename = basename(input_filepath)
        output_filepath = join(output_path, folder, filename)

        if (not(exists(dirname(output_filepath))) and (force)):
            makedirs(dirname(output_filepath))

        if force:
            waveform, sr = librosa.load(input_filepath)
            norm_waveform = librosa.util.normalize(waveform)
            sf.write(output_filepath, norm_waveform, sr, 'PCM_16')

        else:
            print("norm {} {}".format(input_filepath, output_filepath))


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--base_dir', default='./')
    parser.add_argument('-i', '--input', default='input')
    parser.add_argument('-o', '--output', default='output')
    parser.add_argument('-f', '--force', action='store_true', default=False)
    args = parser.parse_args()

    input_dir = join(args.base_dir, args.input)
    output_dir = join(args.base_dir, args.output)

    print('Normalizing audios...')
    normalize_audios(input_dir, output_dir, args.force)


if __name__ == "__main__":
    main()
