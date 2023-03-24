import argparse
import torchaudio
from os import makedirs
from os.path import join, exists, basename
from tqdm import tqdm
from glob import glob

def execute_conversion(input_filepath, output_filepath, target_sr,  force):

    waveform, sr = torchaudio.load(input_filepath)
    if force:
        fn_resample = torchaudio.transforms.Resample(orig_freq=sr, new_freq=target_sr, resampling_method='sinc_interpolation')
        target_waveform = fn_resample(waveform)
        torchaudio.save(output_filepath, target_waveform, target_sr, encoding="PCM_S", bits_per_sample=16, format='wav')
    
    else:
        print("conv %s %d %s %d"% (input_filepath, sr, output_filepath, target_sr))


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--base_dir', default='./')
    parser.add_argument('--input', default='input')    
    parser.add_argument('--output', default='output')  
    parser.add_argument('--target_sr', default='24000')
    parser.add_argument('--force', action='store_true', default=False)
    args = parser.parse_args()

    input_folder = join(args.base_dir, args.input)
    output_folder = join(args.base_dir, args.output)

    if not exists(output_folder) and (args.force):
        makedirs(output_folder)
        
    for input_filepath in tqdm(glob(input_folder + '/*.wav')):
        output_filepath = join(output_folder, basename(input_filepath))
        execute_conversion(input_filepath, output_filepath, int(args.target_sr), args.force)


if __name__ == "__main__":
    main()

