import argparse
import glob
import os
from os import makedirs
from os.path import join, exists, basename
import soundfile as sf
import librosa
from pydub.effects import normalize
from pydub import AudioSegment
import tqdm

def normalize_audio(input_filepath, output_filepath):

    #waveform, sr = sf.read(input_filepath)
    waveform = AudioSegment.from_wav(input_filepath)
    waveform = normalize(waveform)
    waveform.export(output_filepath, format="wav")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base_dir', default='./')
    parser.add_argument('--input', default='input', help='Input folder')
    parser.add_argument('--output', default='output', help='Output folder')
    args = parser.parse_args()

    path_orig = join(args.base_dir,args.input)
    path_dest = join(args.base_dir,args.output)

    if not(exists(path_dest)):
        makedirs(path_dest)

    for audio_filepath in tqdm.tqdm(sorted(glob.glob(path_orig + "/*.wav"))):
        filename = basename(audio_filepath)
        output_filepath = join(path_dest, filename)

        normalize_audio(audio_filepath, output_filepath)


if __name__ == "__main__":
    main()
