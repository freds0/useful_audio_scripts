import argparse
import torch
import torchaudio
from os import makedirs
from os.path import join, exists, isdir, getsize, dirname, basename
from tqdm import tqdm
from glob import glob

def execute(input_filepath, output_filepath, force=False):

    waveform, sample_rate = torchaudio.load(input_filepath)

    if (force and (not exists(dirname(output_filepath)))):
        makedirs(dirname(output_filepath))

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

    output_folder = join(args.base_dir, args.output)

    for input_filepath in tqdm(sorted(glob(input_folder + '/*.wav'))):
        filename = basename(input_filepath)
        output_filepath = os.path.join(output_folder, filename)
        execute(input_filepath, output_filepath, args.force)


if __name__ == "__main__":
    main()

