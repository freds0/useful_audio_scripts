import pydub
import argparse
import subprocess
from os import listdir, makedirs
from os.path import isfile, join, basename

def convert_wav_to_mp3(args):
    wavfiles = [f for f in listdir(join(args.base_dir,args.path_wav_files)) if isfile(join(args.base_dir,args.path_wav_files, f))]
    makedirs(join(args.base_dir,args.path_mp3_files), exist_ok=True)
    for wavfile in wavfiles:
        input_wav_filepath = join(args.base_dir,args.path_wav_files, wavfile)

        filename = basename(input_wav_filepath).split('.')[0]
        output_mp3_filepath = join(args.base_dir, args.path_mp3_files, filename + '.mp3')
        if args.type == 'pydub':
            '''
            y = np.int16(sound)
            song = pydub.AudioSegment(y.tobytes(), frame_rate=22050)
            song.export(output_mp3_filepath, format="mp3", bitrate="128k")
            '''
            sound = pydub.AudioSegment.from_wav(input_wav_filepath, wavfile)
            sound.export(filepath, format="mp3")
        elif args.type == 'lame':
            command_line = "lame {} {}" .format(input_wav_filepath, output_mp3_filepath)
            subprocess.call(command_line, shell=True)
            
       

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-b', '--base_dir', default='./')
  parser.add_argument('-w', '--path_wav_files', default='./', help='Name of wav folder')
  parser.add_argument('-m', '--path_mp3_files', default='mp3', help='Name of mp3 folder')
  parser.add_argument('-t', '--type', default='pydub', help='pydub or lame')
  args = parser.parse_args()
  convert_wav_to_mp3(args)


if __name__ == "__main__":
  main()
