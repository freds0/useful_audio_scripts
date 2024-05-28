from openai import OpenAI
from tqdm import tqdm
from glob import glob
from os.path import join, exists
from pydub import AudioSegment
import argparse
import time
import random

client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key="OPENAI_API_KEY",
)

def get_audio_duration(audio_file_path):
    audio = AudioSegment.from_file(audio_file_path)
    return len(audio) / 1000.0  # Convertendo para segundos


def transcribe_audio(audio_file_path):
    retries = 7  # Número máximo de tentativas
    for _ in range(retries):
        try:
            with open(audio_file_path, 'rb') as audio_file:
                transcription = client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file,
                    response_format="text",
                    language="pt"
                )
            return transcription
        except Exception as e:
            print(f"Erro na transcrição ({_ + 1}/{retries}): {str(e)}")
            waiting_time = random.randint(1, 3)
            time.sleep(waiting_time)  # Aguarda 1 segundo antes de tentar novamente
    return None  # Retorna None se todas as tentativas falharem


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', default='train', help='Wavs folder')
    parser.add_argument('--output_file', default='openai_transcription_2961.csv', help='Name of csv output file')      
    args = parser.parse_args()

    filelist = []
    if exists(args.output_file):
        with open(args.output_file, "r") as ofile:
            data = ofile.readlines()

        for line in data:
            filepath, text = line.split("|")
            filelist.append(filepath)

    for filepath in tqdm(sorted(glob(join(args.input_dir, 'audio/2961/**/*.flac')))):
        if filepath in filelist:
            continue

        duration = get_audio_duration(filepath)
        if duration <= 0.1:
            continue

        text = transcribe_audio(filepath)    
        if text == "":
            continue

        line = "{}|{}".format(filepath, str(text).strip())
        with open(args.output_file, 'a') as ofile:
            ofile.write(line + "\n")


if __name__ == "__main__":
    main()

