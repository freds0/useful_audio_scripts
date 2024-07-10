#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import torch
import torchaudio
from os import makedirs
from os.path import join, basename
from tqdm import tqdm
from glob import glob
from torchaudio.prototype.pipelines import SQUIM_OBJECTIVE

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

objective_model = SQUIM_OBJECTIVE.get_model().to(device)
target_sr = 16000

def audio_quality(input_filepath):   
    waveform, sr = torchaudio.load(input_filepath)
    if waveform.shape[0] == 2:
        waveform = torch.mean(waveform, dim=0, keepdim=True)
    if sr != 16000:
        fn_resample = torchaudio.transforms.Resample(orig_freq=sr, new_freq=target_sr, resampling_method='sinc_interp_hann')
        waveform = fn_resample(waveform)

    with torch.no_grad():
        stoi_hyp, pesq_hyp, si_sdr_hyp = objective_model(waveform[:1600].to(device))

    return stoi_hyp[0], pesq_hyp[0], si_sdr_hyp[0]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', default='input', help='Input folder')
    parser.add_argument('-o', '--output', default='output_quality.csv', help='Output filepath')
    args = parser.parse_args()

    with open(args.output, 'w') as f:
        f.write("filepath,stoi,pesq,si-sdr\n")

    for input_filepath in tqdm(glob(join(args.input, '*.wav'))):
        stoi_hyp, pesq_hyp, si_sdr_hyp = audio_quality(input_filepath)

        line = f"{input_filepath},{stoi_hyp},{pesq_hyp},{si_sdr_hyp}\n"
        with open(args.output, 'a') as f:
            f.write(line)


if __name__ == "__main__":
    main()
