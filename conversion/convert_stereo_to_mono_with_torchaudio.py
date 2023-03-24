import argparse
import torch
import torchaudio
from os import makedirs
from os.path import join, exists, isdir, getsize, dirname, basename
from tqdm import tqdm
from glob import glob

def execute_conversion(input_filepath, output_filepath, force=False):

    waveform, sample_rate = torchaudio.load(input_filepath)
    if force:
        waveform_mono = torch.mean(waveform, dim=0).unsqueeze(0)
        torchaudio.save(output_filepath, waveform_mono, sample_rate, encoding="PCM_S", bits_per_sample=16, format='wav')
    
    else:
        print("conv %s %s"%(input_filepath, output_filepath))


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--base_dir', default='./')
    parser.add_argument('--input', default='input')    
    parser.add_argument('--output', default='output')  
    parser.add_argument('--force', action='store_true', default=False)
    args = parser.parse_args()

    input_folder = join(args.base_dir, args.input)    
    output_folder = join(args.base_dir, args.output)

    if (args.force and not exists(output_folder)):
        makedirs(output_folder)

    for input_filepath in tqdm(sorted(glob(input_folder + '/*.wav'))):
        output_filepath = join(output_folder, basename(input_filepath))
        execute_conversion(input_filepath, output_filepath, args.force)


if __name__ == "__main__":
    main()

