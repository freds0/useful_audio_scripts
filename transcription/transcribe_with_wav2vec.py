import argparse
from tqdm import tqdm
from glob import glob
from os.path import basename, join
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import torch
import torchaudio
import torchaudio.transforms as T

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

class Wav2Vec2Transcriptor:
    '''
    Source: https://huggingface.co/jonatasgrosman/wav2vec2-large-xlsr-53
    '''
    def __init__(self, lang="en"):
        self.processor, self.model = self._load_model(lang)

    def _load_model(self, language_id):

        if language_id == 'sp':
            model_id = "jonatasgrosman/wav2vec2-large-xlsr-53-spanish"
        elif language_id == 'it':
            model_id = "jonatasgrosman/wav2vec2-large-xlsr-53-italian"
        elif language_id == 'ge':
            model_id = "jonatasgrosman/wav2vec2-large-xlsr-53-german"
        elif language_id == 'pl':
            model_id = "jonatasgrosman/wav2vec2-large-xlsr-53-polish"
        elif language_id == 'pt':
            model_id = "jonatasgrosman/wav2vec2-large-xlsr-53-portuguese"
        elif language_id == 'en':
            model_id = "jonatasgrosman/wav2vec2-large-xlsr-53-english"
        elif language_id == 'du':
            model_id = "jonatasgrosman/wav2vec2-large-xlsr-53-dutch"
        elif language_id == 'fr':
            model_id = "jonatasgrosman/wav2vec2-large-xlsr-53-french"

        processor = Wav2Vec2Processor.from_pretrained(model_id)
        model = Wav2Vec2ForCTC.from_pretrained(model_id)

        return processor, model.to(device)

    def _speech_file_to_array_fn(self, filepath, target_sample_rate=16000):
        waveform, sample_rate = torchaudio.load(filepath)
        if sample_rate != target_sample_rate:
            resampler = T.Resample(sample_rate, target_sample_rate)
            waveform = resampler(waveform)
        return waveform.squeeze()

    def transcribe(self, input_filepath):
        waveform = self._speech_file_to_array_fn(input_filepath, 16000)
        input_values = torch.tensor(waveform, device=device).unsqueeze(0)

        with torch.no_grad():
            logits = self.model(input_values).logits

        predicted_ids = torch.argmax(logits, dim=-1)
        text = self.processor.batch_decode(predicted_ids)
        return text

    def transcribe_folder(self, input_dir, output_file):
        ofile = open(output_file, 'w')
        for input_filepath in tqdm(sorted(glob(join(input_dir, '*.wav')))):
            transcription = self.transcribe(input_filepath)[0]
            line = "{}|{}".format(input_filepath, transcription.strip())
            ofile.write(line + "\n")
        ofile.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', default='samples/noisy', help='Wavs folder')
    parser.add_argument('--output_file', default='transcription_wav2vec.csv', help='CSV output file')
    parser.add_argument('--lang', default='en', help='du, en, fr, ge, it, pl, pt')
    args = parser.parse_args()

    asr_model = Wav2Vec2Transcriptor(args.lang)
    asr_model.transcribe_folder(args.input_dir, args.output_file)


if __name__ == "__main__":
    main()