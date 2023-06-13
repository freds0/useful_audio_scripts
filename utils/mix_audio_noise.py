#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import torch
import torchaudio
import torchaudio.functional as F
from random import choice, randrange
from os import makedirs
from os.path import join, basename
from tqdm import tqdm
from glob import glob

def mix_file(input_clean_filepath, input_noise_filepath, output_filepath, force):
    # Read data
    clean_audio, sr = torchaudio.load(input_clean_filepath)
    noise_audio, _ = torchaudio.load(input_noise_filepath)

    if not force:
        print(f"mix {input_clean_filepath} {input_noise_filepath} {output_filepath}")

    else:
        end = randrange(noise_audio.shape[1] - clean_audio.shape[1])
        begin = randrange(end)
        noise_audio = noise_audio[:, begin : begin + clean_audio.shape[1]]

        snr_dbs = torch.randint(low=-10, high=20, size=(1,))
        mixed_audio= F.add_noise(clean_audio, noise_audio, snr_dbs)

        torchaudio.save(output_filepath, mixed_audio, sr, encoding="PCM_S", bits_per_sample=16, format='wav')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_clean', default='clean', help='Input clean wavs folder')
    parser.add_argument('-n', '--input_noise', default='noise', help='Input noise wavs folder')
    parser.add_argument('-o', '--output', default='output', help='Output folder')
    parser.add_argument('-f', '--force', action='store_true', default=False)
    args = parser.parse_args()

    noise_list = glob(join(args.input_noise, '*.wav'))

    makedirs(args.output, exist_ok = True)    
    for input_clean_filepath in tqdm(glob(join(args.input_clean, '*.wav'))):
        output_filepath = join(args.output, basename(input_clean_filepath))
        input_noise_filepath = choice(noise_list)
        mix_file(input_clean_filepath, input_noise_filepath, output_filepath, args.force)


if __name__ == "__main__":
    main()
