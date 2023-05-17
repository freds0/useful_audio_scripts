import random
import torch
import torchaudio
import pyrubberband as pyrb
from pydub import AudioSegment
from pydub.effects import speedup
import argparse
import io


class SpeedChange:
    '''
    Source: https://github.com/shangeth/wavencoder/tree/master/wavencoder/transforms
    '''
    def __init__(self, orig_freq=16000):
        self.orig_freq = orig_freq
    # @profile
    def __call__(self, wav, speed_factor):
        wav = wav.squeeze().numpy()
        if speed_factor < 1.0:
            # pyrubberband is the best option to slow speed
            speeded_wav = pyrb.time_stretch(y=wav, sr=self.orig_freq, rate=speed_factor)
        else:
            # Pydub is the best option to fast speed
            audio_segment = self.__convert_nparray_to_audio_segment(wav)
            speeded_audio_segment = speedup(audio_segment, speed_factor)
            speeded_wav = self.convert_audio_segment_to_nparray(speeded_audio_segment)

        speeded_wav = torch.tensor(speeded_wav, dtype=torch.float32).unsqueeze(0)
        return speeded_wav



    def __convert_nparray_to_audio_segment(self, data):
        buffer_ = io.BytesIO()
        torchaudio.save(filepath=buffer_, src=torch.from_numpy(data).unsqueeze(0), sample_rate=self.orig_freq, format="wav")
        buffer_.seek(0)
        audio_segment = AudioSegment.from_file(buffer_, format="wav")
        return audio_segment


    def convert_audio_segment_to_nparray(self, audio_segment):
        buffer_ = io.BytesIO()
        audio_segment.export(buffer_, format="wav")
        waveform, sr = torchaudio.load(buffer_)
        return waveform.squeeze().numpy()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert audio files.')
    parser.add_argument('-i', '--input', default='input', help='Input filepath.')
    parser.add_argument('-o', '--output', default='output', help='Output filepath.')
    parser.add_argument('-s', '--speed', type=float, help='speed factor sf: 0.0 < sf < 2.0.')
    args = parser.parse_args()

    waveform, sr = torchaudio.load(args.input)
    speed_function = SpeedChange(orig_freq=sr)
    transformed_waveform = speed_function(waveform, args.speed)
    torchaudio.save(filepath=args.output, src=transformed_waveform, sample_rate=sr)
