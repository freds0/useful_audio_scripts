'''
Tutorial source: https://huggingface.co/facebook/mms-1b-fl102
'''
import argparse
from tqdm import tqdm
from glob import glob
from os.path import basename, join
from transformers import AutoProcessor, Wav2Vec2ForCTC
import torch
import torchaudio
import torchaudio.transforms as T

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def load_model(model_name='fl102', lang=""):

    if model_name == "fl102":
        model_id = "facebook/mms-1b-fl102"
    elif model_name == "l1107":
        model_id = 'facebook/mms-1b-l1107'
    elif model_name == "all":
        model_id = "facebook/mms-1b-all"

    processor = AutoProcessor.from_pretrained(model_id)
    model = Wav2Vec2ForCTC.from_pretrained(model_id)

    if lang != "":
        processor.tokenizer.set_target_lang(lang)
        model.load_adapter(lang)

    return processor, model.to(device)


def speech_file_to_array_fn(filepath, target_sample_rate=16000):

    filename = basename(filepath)
    waveform, sample_rate = torchaudio.load(filepath)

    if sample_rate != target_sample_rate:
        resampler = T.Resample(sample_rate, target_sample_rate)
        waveform = resampler(waveform)

    return waveform.squeeze()


def transcribe(processor, model, input_filepath, output_filepath):

    ofile = open(output_filepath, 'a')

    filename = basename(input_filepath)
    waveform = speech_file_to_array_fn(input_filepath)
    inputs = processor(waveform, sampling_rate=16000, return_tensors="pt")
    inputs = inputs.to(device)
    with torch.no_grad():
        outputs = model(**inputs).logits

    ids = torch.argmax(outputs, dim=-1)[0]
    transcription = processor.decode(ids)

    line = "{}|{}".format(filename, transcription)
    ofile.write(line + "\n")

    ofile.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_dir', default='wavs', help='Wavs folder')
    parser.add_argument('-o', '--output_file', default='transcription.csv', help='Name of csv output file')      
    parser.add_argument('-m', '--model', default='fl102', help='Model version: fl102 | l1107 | all')      
    parser.add_argument('-l', '--lang', default='por', help='Check https://dl.fbaipublicfiles.com/mms/misc/language_coverage_mms.html')      
    args = parser.parse_args()

    processor, model = load_model(args.model, args.lang)
    output_filepath = args.output_file
    ofile = open(output_filepath, 'w')
    ofile.close()

    for input_filepath in tqdm(sorted(glob(join(args.input_dir, '*.wav')))):
        transcribe(processor, model, input_filepath, output_filepath)


if __name__ == "__main__":
    main()
