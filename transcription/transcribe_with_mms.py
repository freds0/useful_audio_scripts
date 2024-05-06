import argparse
from tqdm import tqdm
from glob import glob
from os.path import basename, join
from transformers import AutoProcessor, Wav2Vec2ForCTC
import torch
import torchaudio
import torchaudio.transforms as T

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

class MmsTranscriptor:
    '''
    Source: https://huggingface.co/facebook/mms-1b-fl102
    '''
    def __init__(self, model_name='fl102', lang="eng"):
        if lang == "en":
            lang = "eng"
        self.processor, self.model = self._load_model(model_name, lang)

    def _load_model(self, model_name='fl102', lang="eng"):
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

    def _speech_file_to_array_fn(self, filepath, target_sample_rate=16000):
        waveform, sample_rate = torchaudio.load(filepath)
        if sample_rate != target_sample_rate:
            resampler = T.Resample(sample_rate, target_sample_rate)
            waveform = resampler(waveform)
        return waveform.squeeze()

    def transcribe(self, input_filepath):
        waveform = self._speech_file_to_array_fn(input_filepath)
        inputs = self.processor(waveform, sampling_rate=16000, return_tensors="pt")
        inputs = inputs.to(device)

        with torch.no_grad():
            outputs = self.model(**inputs).logits

        ids = torch.argmax(outputs, dim=-1)[0]
        text = self.processor.decode(ids)
        return text


    def transcribe_folder(self, input_dir, output_file):
        ofile = open(output_file, 'w')
        for input_filepath in tqdm(sorted(glob(join(input_dir, '*.wav')))):
            transcription = self.transcribe(input_filepath)
            line = "{}|{}".format(input_filepath, transcription.strip())
            ofile.write(line + "\n")
        ofile.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_dir', default='samples/noisy', help='Wavs folder')
    parser.add_argument('-o', '--output_file', default='transcription_mms.csv', help='CSV output file')
    parser.add_argument('-m', '--model', default='fl102', help='Model version: fl102 | l1107 | all')      
    parser.add_argument('-l', '--lang', default='eng', help='Check https://dl.fbaipublicfiles.com/mms/misc/language_coverage_mms.html')
    args = parser.parse_args()

    asr_model = MmsTranscriptor(args.model, args.lang)
    asr_model.transcribe_folder(args.input_dir, args.output_file)


if __name__ == "__main__":
    main()
