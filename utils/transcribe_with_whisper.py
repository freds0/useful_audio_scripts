'''
Tutorial source: https://huggingface.co/openai/whisper-large-v2
'''
import argparse
from tqdm import tqdm
from glob import glob
from os.path import basename, join
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import torch
import torchaudio
import torchaudio.transforms as T

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def load_model():

    model_id = "openai/whisper-large-v2"

    processor = WhisperProcessor.from_pretrained(model_id)
    model = WhisperForConditionalGeneration.from_pretrained(model_id)
    forced_decoder_ids = processor.get_decoder_prompt_ids(language="portuguese", task="transcribe")

    return processor, model.to(device), forced_decoder_ids


def speech_file_to_array_fn(filepath, target_sample_rate=16000):

    filename = basename(filepath)
    waveform, sample_rate = torchaudio.load(filepath)

    if sample_rate != target_sample_rate:
        resampler = T.Resample(sample_rate, target_sample_rate)
        waveform = resampler(waveform)

    return waveform.squeeze()


def transcribe(processor, model, forced_decoder_ids, input_filepath, output_filepath):

    ofile = open(output_filepath, 'a')

    filename = basename(input_filepath)
    waveform = speech_file_to_array_fn(input_filepath)
    input_features = processor(waveform, sampling_rate=16000, return_tensors="pt").input_features 

    with torch.no_grad():
        predicted_ids = model.generate(input_features.to(device), forced_decoder_ids=forced_decoder_ids)

    transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)

    line = "{}|{}".format(filename, transcription[0])
    ofile.write(line + "\n")

    ofile.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', default='wavs', help='Wavs folder')
    parser.add_argument('--output_file', default='transcription.csv', help='Name of csv output file')      
    args = parser.parse_args()

    processor, model, forced_decoder_ids = load_model()
    output_filepath = args.output_file
    ofile = open(output_filepath, 'w')
    ofile.close()

    #for filepath in tqdm(sorted(glob(join(args.input_dir, 'audio/**/**/*.wav')))):
    for filepath in tqdm(sorted(glob(join(args.input_dir, '*.wav')))):
        transcribe(processor, model, forced_decoder_ids, filepath, output_filepath)


if __name__ == "__main__":
    main()
