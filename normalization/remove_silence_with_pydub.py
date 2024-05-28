import argparse
from pydub import AudioSegment
#from pydub.silence import split_on_silence
from glob import glob
from tqdm import tqdm
from os.path import exists, join, basename
from os import makedirs
from pydub.silence import detect_nonsilent


def remove_silence(path_in, path_out, format="wav", min_silence_len=50, silence_thresh_multiplier=2.5, close_gap=200, min_segment_len=350):
    try:
        sound = AudioSegment.from_file(path_in, format=format)
        silence_thresh = sound.dBFS * silence_thresh_multiplier
        non_sil_times = detect_nonsilent(sound, min_silence_len=min_silence_len, silence_thresh=silence_thresh)
    except Exception as e:
        print(f"Error processing file {path_in}: {str(e)}")
        return False

    if len(non_sil_times) == 0:
        print(f"No non-silent segments found in {path_in}. Skipping file.")
        sound.export(path_out, format='wav')
        return True

    non_sil_times_concat = [non_sil_times[0]]
    for t in non_sil_times[1:]:
        if t[0] - non_sil_times_concat[-1][-1] < close_gap:
            non_sil_times_concat[-1][-1] = t[1]
        else:
            non_sil_times_concat.append(t)

    non_sil_times = [t for t in non_sil_times_concat if t[1] - t[0] > min_segment_len]

    if len(non_sil_times) > 0:
        sound[non_sil_times[0][0]: non_sil_times[-1][1]].export(path_out, format='wav')
    else:
        print(f"After filtering, no suitable audio segments found in {path_in}. Skipping file.")
        return False

    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', default='input', help='Input folder')
    parser.add_argument('-o', '--output', default='output', help='Output folder')
    parser.add_argument('--min_silence_len', type=int, default=50, help='Minimum silence length in ms')
    parser.add_argument('--silence_thresh_multiplier', type=float, default=2.5, help='Silence threshold multiplier')
    parser.add_argument('--close_gap', type=int, default=200, help='Close gap in ms')
    args = parser.parse_args()

    if not(exists(args.output)):
        makedirs(args.output)

    for input_filepath in tqdm(sorted(glob(args.input + "/*.wav"))):
        filename = basename(input_filepath)
        output_filepath = join(args.output, filename)
        remove_silence(input_filepath, output_filepath, min_silence_len=args.min_silence_len, silence_thresh_multiplier=args.silence_thresh_multiplier, close_gap=args.close_gap)


if __name__ == "__main__":
    main()
