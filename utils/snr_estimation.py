import argparse
import glob
import torch
import torchaudio
import numpy as np
import os
from os import makedirs
from torchmetrics.functional.audio import signal_noise_ratio
from os.path import join, basename
import tqdm


torch.set_num_threads(1)

model, _ = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                          model='silero_vad',
                          force_reload=True)

def int2float(sound):
    abs_max = np.abs(sound).max()
    print(abs_max)
    sound = sound.astype('float32')
    if abs_max > 0:
        sound *= 1/abs_max
    sound = sound.squeeze()
    return sound


def calculate_snr(noisy_waveform, clean_waveform):
    return signal_noise_ratio(noisy_waveform, clean_waveform)


def resample(waveform, sr, target_sr=16000):
    fn_resample = torchaudio.transforms.Resample(orig_freq=sr, new_freq=target_sr, resampling_method='sinc_interpolation')
    target_waveform = fn_resample(waveform)
    return target_waveform


def read_audio(filepath):
    audio, sr = torchaudio.load(filepath)
    if sr != 16000:
        audio = resample(audio, sr, target_sr=16000)

    return audio.squeeze()


def save_audio(audio, filepath):
    audio = audio.unsqueeze(0)
    torchaudio.save(filepath, audio, 16000, encoding="PCM_S", bits_per_sample=16, format='wav') 


def get_noise(filepath, speech_prob_threshold=0.3, window_size_samples=512):
    '''
    https://github.com/snakers4/silero-vad/blob/master/examples/colab_record_example.ipynb

    Silero Restriction: window_size_samples mininum equal to 512
    '''
    audio = read_audio(filepath)
    noise = torch.tensor([])
    for i in range(0, len(audio), window_size_samples):

        if len(audio[i: i+ window_size_samples]) < window_size_samples:
            break

        speech_prob = model(audio[i: i+ window_size_samples], 16000).item()
        
        if speech_prob < speech_prob_threshold:
            noise = torch.cat((noise, audio[i:i+window_size_samples]), dim=0)

    model.reset_states()

    return noise


def get_snr_estimation(filepath):

    noise = get_noise(filepath, speech_prob_threshold=0.3)
    silence = torch.zeros(len(noise))
    save_audio(noise, "tmp.wav")
    snr = calculate_snr(noise, silence)
    return snr


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base_dir', default='./')
    parser.add_argument('--input', default='sample.wav')
    args = parser.parse_args()
    filepath = join(args.base_dir, args.input)
    snr = get_snr_estimation(filepath)
    print(snr)


if __name__ == "__main__":
  main()
