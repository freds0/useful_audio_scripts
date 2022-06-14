import argparse
from glob import glob
from os import makedirs
from os.path import join, isdir, dirname
from tqdm import tqdm
from pydub import AudioSegment
import librosa
import soundfile as sf

def convert_wavs(input_metadata_file, output_folder, target_sr = 22050, force = False):
    target_sr = int(target_sr)
    try:
        f = open(input_metadata_file)
        content_file = f.readlines()
    except IOError:
      print("Error: File {} does not appear to exist.".format(input_metadata_file))
      return False
    else:
        f.close()

    folder_name = dirname(input_metadata_file)
    for line in content_file:
        filename, text, _ = line.split('|')
        filename = filename.replace('.wav', '')+ '.wav'

        input_filepath = join(folder_name, 'wavs', filename)
        # Read data
        data, original_sr = librosa.load(input_filepath)
        original_sr = int(original_sr)

        output_filepath = join(output_folder, 'wavs', filename)

        if original_sr != target_sr and force:            
            makedirs(dirname(output_filepath), exist_ok = True)
            # Convert data
            converted_data = librosa.resample(y = data, orig_sr = original_sr, target_sr = target_sr)
            # Works only at olde versions of librosa
            # librosa.output.write_wav(output_file, converted_data, new_sr)
            sf.write(output_filepath, converted_data, target_sr)

        elif original_sr == target_sr:
            print(f"Original sr {original_sr} is equal to target sr {target_sr}")
        else:
            print(f"conv {input_filepath} {output_filepath} ")


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--base_dir', default='./')
    parser.add_argument('-i', '--input', default='input')
    parser.add_argument('-c', '--input_csv', default='metadata.csv', help='Input metadata file')
    parser.add_argument('-o', '--output', default='output', help='Output folder')
    parser.add_argument('-s', '--sr', default=22050)
    parser.add_argument('-f', '--force', action='store_true', default=False)
    args = parser.parse_args()

    output_folder = join(args.base_dir, args.output)

    # Read a hierarchy of metadata files at diferent folders
    for folder_path in tqdm(sorted(glob(join(args.base_dir, args.input + '/*')))):
        if not isdir(folder_path):
            continue

        input_metadata_file = join(folder_path, args.input_csv)
        output_folder = folder_path.replace(args.input, args.output)
        convert_wavs(input_metadata_file, output_folder, args.sr, args.force)

if __name__ == "__main__":
    main()
