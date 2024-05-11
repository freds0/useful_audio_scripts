# Source: https://github.com/WeberJulian/TTS-1/blob/multilingual/TTS/bin/remove_silence_using_vad.py
import os
import tqdm
from glob import glob
import argparse
import pathlib
import collections
import contextlib
import wave
import webrtcvad
from tqdm.contrib.concurrent import process_map
import multiprocessing
from itertools import chain
from tqdm import tqdm

def read_wave(path):
    """Reads a .wav file.
    Takes the path, and returns (PCM audio data, sample rate).
    """
    with contextlib.closing(wave.open(path, 'rb')) as wf:
        num_channels = wf.getnchannels()
        assert num_channels == 1
        sample_width = wf.getsampwidth()
        assert sample_width == 2
        sample_rate = wf.getframerate()
        assert sample_rate in (8000, 16000, 32000, 48000)
        pcm_data = wf.readframes(wf.getnframes())
        return pcm_data, sample_rate


def write_wave(path, audio, sample_rate):
    """Writes a .wav file.
    Takes path, PCM audio data, and sample rate.
    """
    with contextlib.closing(wave.open(path, 'wb')) as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio)


class Frame(object):
    """Represents a "frame" of audio data."""
    def __init__(self, bytes, timestamp, duration):
        self.bytes = bytes
        self.timestamp = timestamp
        self.duration = duration


def frame_generator(frame_duration_ms, audio, sample_rate):
    # This code is adpated from: https://github.com/wiseman/py-webrtcvad/blob/master/example.py
    """Generates audio frames from PCM audio data.
    Takes the desired frame duration in milliseconds, the PCM data, and
    the sample rate.
    Yields Frames of the requested duration.
    """
    n = int(sample_rate * (frame_duration_ms / 1000.0) * 2)
    offset = 0
    timestamp = 0.0
    duration = (float(n) / sample_rate) / 2.0
    while offset + n < len(audio):
        yield Frame(audio[offset:offset + n], timestamp, duration)
        timestamp += duration
        offset += n


def vad_collector(sample_rate, frame_duration_ms,
                  padding_duration_ms, vad, frames):
    """Filters out non-voiced audio frames.
    Given a webrtcvad.Vad and a source of audio frames, yields only
    the voiced audio.
    Uses a padded, sliding window algorithm over the audio frames.
    When more than 90% of the frames in the window are voiced (as
    reported by the VAD), the collector triggers and begins yielding
    audio frames. Then the collector waits until 90% of the frames in
    the window are unvoiced to detrigger.
    The window is padded at the front and back to provide a small
    amount of silence or the beginnings/endings of speech around the
    voiced frames.
    Arguments:
    sample_rate - The audio sample rate, in Hz.
    frame_duration_ms - The frame duration in milliseconds.
    padding_duration_ms - The amount to pad the window, in milliseconds.
    vad - An instance of webrtcvad.Vad.
    frames - a source of audio frames (sequence or generator).
    Returns: A generator that yields PCM audio data.
    """
    num_padding_frames = int(padding_duration_ms / frame_duration_ms)
    # We use a deque for our sliding window/ring buffer.
    ring_buffer = collections.deque(maxlen=num_padding_frames)
    # We have two states: TRIGGERED and NOTTRIGGERED. We start in the
    # NOTTRIGGERED state.
    triggered = False

    voiced_frames = []
    for frame in frames:
        is_speech = vad.is_speech(frame.bytes, sample_rate)

        # sys.stdout.write('1' if is_speech else '0')
        if not triggered:
            ring_buffer.append((frame, is_speech))
            num_voiced = len([f for f, speech in ring_buffer if speech])
            # If we're NOTTRIGGERED and more than 90% of the frames in
            # the ring buffer are voiced frames, then enter the
            # TRIGGERED state.
            if num_voiced > 0.9 * ring_buffer.maxlen:
                triggered = True
                # sys.stdout.write('+(%s)' % (ring_buffer[0][0].timestamp,))
                # We want to yield all the audio we see from now until
                # we are NOTTRIGGERED, but we have to start with the
                # audio that's already in the ring buffer.
                for f, s in ring_buffer:
                    voiced_frames.append(f)
                ring_buffer.clear()
        else:
            # We're in the TRIGGERED state, so collect the audio data
            # and add it to the ring buffer.
            voiced_frames.append(frame)
            ring_buffer.append((frame, is_speech))
            num_unvoiced = len([f for f, speech in ring_buffer if not speech])
            # If more than 90% of the frames in the ring buffer are
            # unvoiced, then enter NOTTRIGGERED and yield whatever
            # audio we've collected.
            if num_unvoiced > 0.9 * ring_buffer.maxlen:
                #sys.stdout.write('-(%s)' % (frame.timestamp + frame.duration))
                triggered = False
                yield b''.join([f.bytes for f in voiced_frames])
                ring_buffer.clear()
                voiced_frames = []
    # If we have any leftover voiced audio when we run out of input,
    # yield it.
    if voiced_frames:
        yield b''.join([f.bytes for f in voiced_frames])


def remove_silence(file_tupla):
    filepath, output_dir = file_tupla
    filename = os.path.basename(filepath)
    output_path = os.path.join(output_dir, os.path.basename(filepath))
    # ignore if the file exists 
    if os.path.exists(output_path) and not args.force:
        return False
    # create all directory structure
    pathlib.Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    padding_duration_ms = 300 # default 300
    audio, sample_rate = read_wave(filepath)
    vad = webrtcvad.Vad(int(args.aggressiveness))
    frames = frame_generator(30, audio, sample_rate)
    frames = list(frames)
    segments = vad_collector(sample_rate, 30, padding_duration_ms, vad, frames)
    flag = False
    segments = list(segments)
    num_segments = len(segments)

    if num_segments != 0:
        for i, segment in reversed(list(enumerate(segments))):
            if i >= 1:
                if flag == False:
                    concat_segment = segment
                    flag = True
                else:
                    concat_segment = segment + concat_segment
            else:
                if flag:
                    segment = segment + concat_segment
                write_wave(output_path, segment, sample_rate)
                print(output_path)
                return True
    else:
        print("> Just Copying the file to:", output_path)
        # if fail to remove silence just write the file
        write_wave(output_path, audio, sample_rate)


def execute_silence_removal(input_dir, output_dir, force=False, aggressiveness=1):

    files = sorted(glob(input_dir, recursive=True))
    file_tuples = [(file_path, output_dir) for file_path in files]

    print("> Number of files: ", len(files))
    print("> Folder: ", input_dir)
    if not force:
        print("> Ignoring files that already exist in the output directory.")

    if files:
        # create threads
        num_threads = multiprocessing.cpu_count()
        process_map(remove_silence, file_tuples, max_workers=num_threads, chunksize=15)
    else:
        print("> No files Found !")


if __name__ == "__main__":
    """
    usage
    python remove_silence.py -i=input -o=output -g=/*.wav -a=2 
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, default='input',
                        help='Dataset root dir')
    parser.add_argument('-o', '--output', type=str, default='output',
                        help='Output Dataset dir')
    parser.add_argument('--force', action='store_true', default=False)
    parser.add_argument('-g', '--glob', type=str, default='*.wav',
                        help='path in glob format for acess wavs from input folder. ex: /**/*.wav')
    parser.add_argument('-a', '--aggressiveness', type=int, default=2,
                        help='set its aggressiveness mode, which is an integer between 0 and 3. 0 is the least aggressive about filtering out non-speech, 3 is the most aggressive.')

    args = parser.parse_args()

    for folder in tqdm(os.listdir(args.input)):
        input_folder = os.path.join(args.input, folder, args.glob)
        output_folder = os.path.join(args.output, folder)
        execute_silence_removal(input_folder, output_folder, args.force, args.aggressiveness)
