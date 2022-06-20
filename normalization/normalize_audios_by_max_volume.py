import argparse
import glob
import os
from os import makedirs
from os.path import join, exists, basename
from pydub import effects  
from pydub import AudioSegment
import tqdm

def normalize_files(args):
    path_orig = join(args.base_dir,args.input)
    path_dest = join(args.base_dir,args.output)

    if not(exists(path_dest)):
        makedirs(path_dest)

    for path_file in tqdm.tqdm(sorted(glob.glob(path_orig + "/*.wav"))):
        filename = basename(path_file)
        dest_file = join(path_dest, filename)

        _sound = AudioSegment.from_file(path_file, "wav")  
        sound = effects.normalize(_sound)  
        sound.export(dest_file, format="wav")            


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--base_dir', default='./')
  parser.add_argument('--input', default='input', help='Name of the origin directory of wav files')
  parser.add_argument('--output', default='output', help='Name of the directory where wav files will be saved')
  args = parser.parse_args()
  normalize_files(args)


if __name__ == "__main__":
  main()
