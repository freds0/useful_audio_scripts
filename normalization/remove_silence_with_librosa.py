import argparse
from glob import glob
from os import makedirs
from os.path import join, exists, basename, dirname
import librosa
import torchaudio
from tqdm import tqdm
import numpy as np

def remove_silence(input_filepath, output_filepath, top_db = 10):

    waveform, sr = torchaudio.load(input_filepath)
    trimmed_waveform, index = librosa.effects.trim(waveform, top_db=top_db)
    torchaudio.save(output_filepath, trimmed_waveform, sr, encoding="PCM_S", bits_per_sample=16)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--base_dir', default='./')
    parser.add_argument('-i', '--input', default='input', help='Input folder')
    parser.add_argument('-o', '--output', default='output', help='Output folder')
    parser.add_argument('-t', '--top_db', default=40, help='Top db')
    args = parser.parse_args()

    input_dir = join(args.base_dir, args.input)
    output_dir = join(args.base_dir, args.output)

    if not(exists(output_dir)):
        makedirs(output_dir)

    for input_filepath in tqdm(sorted(glob(input_dir + "/*.wav"))):
        filename = basename(input_filepath)
        output_filepath = join(output_dir, filename)
        remove_silence(input_filepath, output_filepath, int(args.top_db))


if __name__ == "__main__":
    main()
