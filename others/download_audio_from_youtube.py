import argparse
from os import makedirs
from os.path import join
from tqdm import tqdm
from pytube import YouTube
from random import randint
import time

def execute_download(youtube_link, output_dir):
    video_id = youtube_link.replace('https://www.youtube.com/watch?v=', '')
    filename = '{}.mp4'.format(video_id.strip())
    try:
        yt = YouTube(youtube_link)
    except VideoUnavailable:
        print(f'Video {youtube_link} is unavaialable, skipping.')
    else:
        #print(f'Downloading video: {youtube_link}')
        stream = yt.streams.filter(file_extension= 'mp4')
        yt.streams.filter(only_audio=True, subtype='mp4').first().download(output_path=output_dir, filename=filename)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base_dir', default='./')
    parser.add_argument('--input_file', default='links.txt', help='Name of txt file')
    parser.add_argument('--output_dir', default='audios', help='Name of folder')
    args = parser.parse_args()

    input_file = join(args.base_dir, args.input_file)
    output_folder = join(args.base_dir, args.output_dir)
    try:
        f = open(input_file, encoding="utf-8")
        content_file = f.readlines()
    except IOError:
      print("Error: File {} does not appear to exist.".format(input_file))
      return False

    else:
        f.close()

    makedirs(output_folder, exist_ok=True)
    for yt_link in tqdm(content_file):
        t = randint(30,60) 
        print('Waiting %d seconds ...'%(t))
        time.sleep(t) # Overcome YouTube blocking

        execute_download(yt_link, output_folder)


if __name__ == "__main__":
    main()

