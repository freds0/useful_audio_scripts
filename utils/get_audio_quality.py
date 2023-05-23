import argparse
from os.path import join, basename
import torch
import torchaudio

from torchaudio.prototype.pipelines import SQUIM_OBJECTIVE
#from torchaudio.prototype.pipelines import SQUIM_SUBJECTIVE

import torchaudio.functional as F
from glob import glob


def get_audio_quality(input_filepath, metric='all'):
    waveform, sr = torchaudio.load(input_filepath)

    if sr != 16000:
        waveform = F.resample(waveform, sr, 16000)

    snr_dbs = [0, 10]
    objective_model = SQUIM_OBJECTIVE.get_model()

    stoi_hyp, pesq_hyp, si_sdr_hyp = objective_model(waveform)
    print(f"Estimated metrics for distorted speech {basename(input_filepath)} at {snr_dbs[0]}dB are\n")
    print(f"STOI: {stoi_hyp[0]} (0 (worst)- 1 (best))") 
    print(f"PESQ: {pesq_hyp[0]} (-0.5 (worst) - 4.5 (best))")
    print(f"SI-SDR: {si_sdr_hyp[0]} ( value < 0 = low quality, value approx 0 = medium quality, value > 0 = high quality)\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', type=str, required=True, help='input audio folder')
    parser.add_argument('--metric', '-m', type=str, default='all', help='all, stoi, pesq or si-sdr')
    args = parser.parse_args()

    for input_file in glob(join(args.input, '*.wav')):
        get_audio_quality(input_file, args.metric)

if __name__ == "__main__":
    main()