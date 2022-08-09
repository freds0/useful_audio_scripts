import argparse
import torchaudio
import os
from os import makedirs
from os.path import join, exists, isdir, getsize, dirname, basename
from tqdm import tqdm
from glob import glob

def execute(filepath, target_sample_rate, input_folder, output_folder, force):

    filename = basename(filepath)
    folder = dirname(filepath)
    new_folder = folder.replace(input_folder, output_folder)
    output_filepath = join(new_folder, filename)

    waveform, sample_rate = torchaudio.load(filepath)

    if not exists(new_folder) and (force):
        makedirs(new_folder)

    if force:
        fn_resample = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=target_sample_rate, resampling_method='sinc_interpolation')
        target_waveform = fn_resample(waveform)
        torchaudio.save(output_filepath, target_waveform, target_sample_rate, encoding="PCM_S", bits_per_sample=16, format='wav')
    
    else:
        print("conv %s %d %s %d"% (filepath, sample_rate, output_filepath, int(target_sample_rate)))



def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--base_dir', default='./')
    parser.add_argument('--input', default='input')    
    parser.add_argument('--output', default='output')  
    parser.add_argument('--sr', default='24000')
    parser.add_argument('--force', action='store_true', default=False)
    args = parser.parse_args()

    input_folder = join(args.base_dir, args.input)
    output_folder = join(args.base_dir, args.output)

    for filepath in tqdm(sorted(glob(input_folder + '/**/*.wav'))):
        execute(filepath, int(args.sr), input_folder, output_folder, args.force)


if __name__ == "__main__":
    main()

