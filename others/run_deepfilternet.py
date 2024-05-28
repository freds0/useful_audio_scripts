import subprocess
from glob import glob
from os.path import join
from os import makedirs, listdir
import argparse
from tqdm import tqdm

def execute(input_dir, output_dir):
    #wav_files = glob(join(input_dir, "**/*.wav"))
    folders = listdir(input_dir)
    makedirs(output_dir, exist_ok=True)
    #for wav_filepath in tqdm(wav_files):
    for folder in tqdm(folders):
        in_dir = join(input_dir, folder)
        out_dir = join(output_dir, folder)
        makedirs(out_dir, exist_ok=True)
        command = f"deepFilter --noisy-dir {in_dir} --output-dir={out_dir}"
        #print(command)
        subprocess.run(command, shell=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default='input', help='Name of the origin directory of wav files')
    parser.add_argument('--output', default='output', help='Name of the directory where wav files will be saved')
    args = parser.parse_args()
    execute(args.input, args.output)

if __name__ == "__main__":
    main()
 
