#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import torch
import torchaudio
from os import path
from tqdm import tqdm
from glob import glob
from torchmetrics.audio import ShortTimeObjectiveIntelligibility as stoi
from torchmetrics.audio import ScaleInvariantSignalDistortionRatio as si_sdr
from torchmetrics.audio import PerceptualEvaluationSpeechQuality as pesq
from torchaudio.transforms import Resample


'''
pip install torchmetrics[audio]
pip install pesq pystoi

'''

#device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
device = "cpu"
target_sr = 16000

# Initialize metrics
stoi_metric = stoi(target_sr)
pesq_metric = pesq(target_sr, 'wb')
si_sdr_metric = si_sdr()

def audio_quality(clean_path, noisy_path):   
    clean_waveform, sr = torchaudio.load(clean_path)
    noisy_waveform, _ = torchaudio.load(noisy_path)

    if clean_waveform.shape[0] == 2:
        clean_waveform = torch.mean(clean_waveform, dim=0, keepdim=True)
    if noisy_waveform.shape[0] == 2:
        noisy_waveform = torch.mean(noisy_waveform, dim=0, keepdim=True)

    if sr != target_sr:
        fn_resample = Resample(orig_freq=sr, new_freq=target_sr)
        clean_waveform = fn_resample(clean_waveform)
        noisy_waveform = fn_resample(noisy_waveform)

    stoi_hyp = stoi_metric(noisy_waveform.to(device), clean_waveform.to(device)).item()
    pesq_hyp = pesq_metric(noisy_waveform.to(device), clean_waveform.to(device)).item()
    si_sdr_hyp = si_sdr_metric(noisy_waveform.to(device), clean_waveform.to(device)).item()

    return stoi_hyp, pesq_hyp, si_sdr_hyp

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clean', default='clean', help='Clean audio folder')
    parser.add_argument('-n', '--noisy', default='noisy', help='Noisy audio folder')
    parser.add_argument('-o', '--output', default='output_quality.csv', help='Output filepath')
    args = parser.parse_args()

    #clean_files = glob(path.join(args.clean, '*.wav'))
    #noisy_files = {path.basename(f): f for f in glob(path.join(args.noisy, '*.wav'))}

    with open(args.output, 'w') as f:
        f.write("filepath,stoi,pesq,si-sdr\n")

    stoi_hyp, pesq_hyp, si_sdr_hyp = audio_quality(args.clean, args.noisy)
    filename = args.clean
    line = f"{filename},{stoi_hyp},{pesq_hyp},{si_sdr_hyp}\n"
    with open(args.output, 'a') as f:
        f.write(line)

if __name__ == "__main__":
    main()

