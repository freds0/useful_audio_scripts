'''
Tutorial source: https://huggingface.co/openai/whisper-large-v2
'''
import argparse
from tqdm import tqdm
from glob import glob
from os.path import basename, join
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor
import torch
import torchaudio
import torchaudio.transforms as T

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

def load_model():

    model_id = "openai/whisper-large-v3"

    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
    )
    processor = AutoProcessor.from_pretrained(model_id)
    return processor, model.to(device)


def speech_file_to_array_fn(filepath, target_sample_rate=16000):

    filename = basename(filepath)
    waveform, sample_rate = torchaudio.load(filepath)

    if sample_rate != target_sample_rate:
        resampler = T.Resample(sample_rate, target_sample_rate)
        waveform = resampler(waveform)

    return waveform.squeeze()


def transcribe(processor, model, input_filepath, output_filepath):

    ofile = open(output_filepath, 'a', encoding='utf-8')

    filename = basename(input_filepath)
    waveform = speech_file_to_array_fn(input_filepath)
    input_features = processor(waveform, sampling_rate=16000, return_tensors="pt").input_features 

    # Convert input_features to the same dtype as the model
    input_features = input_features.to(device).to(torch_dtype)

    with torch.no_grad():
        predicted_ids = model.generate(input_features.to(device))

    transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)

    line = "{}|{}".format(filename, transcription[0].strip())
    ofile.write(line + "\n")

    ofile.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', default='wavs', help='Wavs folder')
    parser.add_argument('--output_file', default='transcription.csv', help='Name of csv output file')      
    args = parser.parse_args()

    processor, model = load_model()
    output_filepath = args.output_file
    ofile = open(output_filepath, 'w')
    ofile.close()

    #for filepath in tqdm(sorted(glob(join(args.input_dir, 'audio/**/**/*.wav')))):
    for filepath in tqdm(sorted(glob(join(args.input_dir, '*.flac')))):
        transcribe(processor, model, filepath, output_filepath)


if __name__ == "__main__":
    main()
