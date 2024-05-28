import argparse
from pydub import AudioSegment
from os import listdir
from os.path import isfile, join

def get_silence(audio, threshold, interval):
    "get length of silence in seconds from a wav file"

    # swap out pydub import for other types of audio
    wav = AudioSegment.from_wav(audio)

    # break into chunks
    chunks = [wav[i:i+interval] for i in range(0, len(wav), interval)]

    # find number of chunks with dBFS below threshold
    silent_blocks = 0
    for c in chunks:
        if c.dBFS == float('-inf') or c.dBFS < threshold:
            silent_blocks += 1
        #else:
        #    break

    # convert blocks into seconds
    return round(silent_blocks * (interval / 1000), 3)

def get_duration(audio):
    "get duration of audio in seconds"

    # swap out pydub import for other types of audio
    wav = AudioSegment.from_wav(audio)
    return round(len(wav) / 1000, 3)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir',  help='Input folder')
    parser.add_argument('--threshold',  default=-80, help='Threshold for silence. Tweak based on signal-to-noise ratio')
    parser.add_argument('--interval',  default=1, help='Interval in ms. Increase to speed up')
    args = parser.parse_args()

    # get files in a directory
    audio_files = [i for i in listdir(args.input_dir) if isfile(join(args.input_dir, i))]

    leading_silences = {a: get_silence(join(args.input_dir, a),
                                       args.threshold, args.interval) for a in audio_files}

    # to get tab-separated values:
    for name, leading_silence in leading_silences.items():
        duration = get_duration(join(args.input_dir, name))
        percentage = round(leading_silence / duration * 100, 3)
        print("{}|{}|{}|{}".format(name, leading_silence, duration, percentage))

if __name__ == "__main__":
    main()


