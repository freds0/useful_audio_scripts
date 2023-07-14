import argparse
from resemblyzer import VoiceEncoder, preprocess_wav
import pyreaper
import torch
import torchaudio
from os.path import join, exists, basename
from os import makedirs
from tqdm import tqdm
from glob import glob

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


def extract_embeddings(filelist, output_dir):
    '''
    Embeddings from: Generalized End-To-End Loss for Speaker Verification 
    '''
    encoder = VoiceEncoder()

    for filepath in tqdm(filelist):
        # Load audio file
        if not exists(filepath):
            print("file {} doesnt exist!".format(filepath))
            continue

        filename = basename(filepath)
        wav = preprocess_wav(filepath)
        file_embedding = encoder.embed_utterance(wav)
        embedding = torch.tensor(file_embedding)

        # Saving embedding
        output_filename = filename.split(".")[0] + ".pt"
        output_filepath = join(output_dir, output_filename)
        torch.save(embedding, output_filepath)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', default="input", help='Input folder')
    parser.add_argument('-o', '--output', default='output', help='Output folder')
    args = parser.parse_args()

    filelist = None
    filelist = glob(join(args.input, '*.wav'))

    makedirs(args.output, exist_ok=True)
    extract_embeddings(filelist, args.output)


if __name__ == "__main__":
    main()
