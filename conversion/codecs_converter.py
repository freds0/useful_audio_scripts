import pydub
import argparse
import subprocess
import tqdm
from os import listdir, makedirs
from os.path import isfile, join, basename
import shutil

temp_sampling_rate = 8000
output_sampling_rate = 16000

def convert_mp3(input_files, input_dir, output_dir):

    for wavfile in tqdm.tqdm(input_files):
        input_filepath = join(input_dir, wavfile)

        filename = basename(input_filepath).split('.')[0]
        tmp_filepath = join('tmp', filename + '.mp3')
        output_filepath = join(output_dir, filename + '.wav')

        #command_line = "sox {} -r {} -c 1 -b 8 {}" .format(input_filepath, temp_sampling_rate, tmp_filepath)
        command_line = "ffmpeg -i {} -acodec mp3 -ar {} -ac 1 -b:a 16k -y {}".format(input_filepath, temp_sampling_rate, tmp_filepath)
        subprocess.call(command_line, shell=True)

        #command_line = "sox {} -r {} -c 1 {}" .format(tmp_filepath, output_sampling_rate, output_filepath)
        command_line = "ffmpeg -acodec mp3 -i {} -f wav -ar {} -y {}".format(tmp_filepath, output_sampling_rate, output_filepath)
        subprocess.call(command_line, shell=True)
        

def convert_gsm(input_files, input_dir, output_dir):

    for wavfile in tqdm.tqdm(input_files):
        input_filepath = join(input_dir, wavfile)

        filename = basename(input_filepath).split('.')[0]
        tmp_filepath = join('tmp', filename + '.wav')
        output_filepath = join(output_dir, filename + '.wav')

        command_line = "ffmpeg -i {} -c:a libgsm -ar {} -ab 13000  -ac 1 -f gsm {}".format(input_filepath, temp_sampling_rate, tmp_filepath)
        #command_line = "sox {} -r {} -c 1 {}" .format(input_filepath, temp_sampling_rate, tmp_filepath)
        subprocess.call(command_line, shell=True)

        command_line = "ffmpeg -c:a libgsm -ar {} -ac 1 -i {} -f wav -ar {} -y {}".format(temp_sampling_rate, tmp_filepath, output_sampling_rate, output_filepath)
        #command_line = "sox {} -r {} -c 1 {}" .format(tmp_filepath, output_sampling_rate, output_filepath)
        subprocess.call(command_line, shell=True)


def convert_g726(input_files, input_dir, output_dir):

    bit_rate = ['16k', '24k', '32k', '40k']

    for wavfile in tqdm.tqdm(input_files):
        input_filepath = join(input_dir, wavfile)

        filename = basename(input_filepath).split('.')[0]
        tmp_filepath = join('tmp', filename + '.wav')
        output_filepath = join(output_dir, filename + '.wav')

        command_line = "ffmpeg -i {} -acodec g726 -ar {} -f g726 -y {}".format(input_filepath, temp_sampling_rate, tmp_filepath)
        subprocess.call(command_line, shell=True)

        command_line = "ffmpeg -f g726 -ac 1 -ar {} -i {} -f wav -ar {} -y {}".format(temp_sampling_rate, tmp_filepath, output_sampling_rate, output_filepath)
        subprocess.call(command_line, shell=True)


def convert_adpcm(input_files, input_dir, output_dir):

    for wavfile in tqdm.tqdm(input_files):
        input_filepath = join(input_dir, wavfile)

        filename = basename(input_filepath).split('.')[0]
        tmp_filepath = join('tmp', filename + '.wav')
        output_filepath = join(output_dir, filename + '.wav')

        command_line = "ffmpeg -i {} -acodec adpcm_ms -ar {} -b:a 16k -f wav -y {}".format(input_filepath, temp_sampling_rate, tmp_filepath)
        subprocess.call(command_line, shell=True)

        command_line = "ffmpeg -acodec adpcm_ms -i {} -f wav -ar {} -y {}".format(tmp_filepath, output_sampling_rate, output_filepath)
        subprocess.call(command_line, shell=True)


def convert_g723(input_files, input_dir, output_dir):

    for wavfile in tqdm.tqdm(input_files):
        input_filepath = join(input_dir, wavfile)

        filename = basename(input_filepath).split('.')[0]
        tmp_filepath = join('tmp', filename + '.wav')
        output_filepath = join(output_dir, filename + '.wav')

        command_line = "ffmpeg -i {}  -acodec g723_1 -ar {} -ac 1 -b:a 6.3k -f wav -y {}".format(input_filepath, temp_sampling_rate, tmp_filepath)
        subprocess.call(command_line, shell=True)

        command_line = "ffmpeg -acodec g723_1 -i {} -f wav -ar {} -y {}".format(tmp_filepath, output_sampling_rate, output_filepath)
        subprocess.call(command_line, shell=True)


def convert_ogg(input_files, input_dir, output_dir):

    for wavfile in tqdm.tqdm(input_files):
        input_filepath = join(input_dir, wavfile)

        filename = basename(input_filepath).split('.')[0]
        tmp_filepath = join('tmp', filename + '.oga')
        output_filepath = join(output_dir, filename + '.wav')

        command_line = "ffmpeg -i {} -c:a libopus -ar {} -b:a 4.5k -y {}".format(input_filepath, temp_sampling_rate, tmp_filepath)
        subprocess.call(command_line, shell=True)

        command_line = "ffmpeg -c:a libopus -i {} -f wav -ar {} -y {}".format(tmp_filepath, output_sampling_rate, output_filepath)
        subprocess.call(command_line, shell=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--base_dir', default='./')
    parser.add_argument('-i', '--input', default='./wav', help='Name of wav folder')
    parser.add_argument('-t', '--temp', default='./tmp', help='Name of mp3 folder')
    parser.add_argument('-o', '--output', default='./result', help='Name of mp3 folder')
    parser.add_argument('-c', '--codec', default='mp3', help='pydub or lame')
    args = parser.parse_args()

    input_files = [f for f in listdir(join(args.base_dir,args.input)) if isfile(join(args.base_dir,args.input, f))]

    input_dir = join(args.base_dir,args.input)

    output_dir = join(args.base_dir, args.output)
    try:
        shutil.rmtree(output_dir)
    except OSError as e:
        print("Error: %s : %s" % (output_dir, e.strerror))
    makedirs(output_dir, exist_ok=True)

    tmp_dir = join(args.base_dir, 'tmp')
    try:
        shutil.rmtree(tmp_dir)

    except OSError as e:
        print("Error: %s : %s" % (tmp_dir, e.strerror))
    makedirs(tmp_dir, exist_ok=True)


    if args.codec == 'mp3':
        convert_mp3(input_files, input_dir, output_dir)
    elif args.codec == 'gsm':
        convert_gsm(input_files, input_dir, output_dir)
    elif args.codec == 'g726':
        convert_g726(input_files, input_dir, output_dir)
    elif args.codec == 'adpcm':
        convert_adpcm(input_files, input_dir, output_dir)
    elif args.codec == 'g723':
        convert_g723(input_files, input_dir, output_dir)
    elif args.codec == 'ogg':
        convert_ogg(input_files, input_dir, output_dir)
    else:
        print("Codec invalido")

if __name__ == "__main__":
	main()	
