from os.path import join, basename
from os import makedirs
import tqdm
from glob import glob
import torchaudio
import argparse

def voice_detector(input_filepath, output_filepath):
    waveform, sr = torchaudio.load(input_filepath)
    trimmed_waveform = torchaudio.functional.vad(waveform, sr)
    print(input_filepath)
    print(sum(trimmed_waveform.squeeze()).item())
    #torchaudio.save(output_filepath, trimmed_waveform, sr)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, default='input',
                        help='Dataset root dir')
    parser.add_argument('-o', '--output', type=str, default='output',
                        help='Output Dataset dir')

    args = parser.parse_args()

    makedirs(args.output, exist_ok=True)

    for input_filepath in glob(join(args.input, "*.wav")):
        output_filepath = join(args.output, basename(input_filepath))
        voice_detector(input_filepath, output_filepath)


if __name__ == "__main__":

    main()
