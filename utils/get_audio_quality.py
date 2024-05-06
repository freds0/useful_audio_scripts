import argparse
from os.path import join, dirname
import torchaudio
import torchaudio.functional as F
from torchaudio.pipelines import SQUIM_OBJECTIVE
from tqdm import tqdm
import concurrent.futures

# Obtenha o modelo SQUIM_OBJECTIVE
objective_model = SQUIM_OBJECTIVE.get_model()
input_dir = ""

def get_audio_quality(input_filepath):
    try:
        waveform, sr = torchaudio.load(input_filepath)
    except Exception as e:
        print(f"Error loading file: {str(e)}")
        waveform = None
        return 0, 0, 0

    if sr != 16000:
        waveform = F.resample(waveform, sr, 16000)

    stoi_hyp, pesq_hyp, si_sdr_hyp = objective_model(waveform)
    return stoi_hyp[0], pesq_hyp[0], si_sdr_hyp[0]

def write_metrics(output_file, wav_filename, stoi, pesq, si_sdr):
    line = f"{wav_filename}|{stoi}|{pesq}|{si_sdr}\n"
    output_file.write(line)

def process_audio_file(input_data):
    wav_filename, _, _, _, _, _, _, _ = input_data.split("|")
    global input_dir
    input_filepath = join(input_dir, wav_filename)
    stoi, pesq, si_sdr = get_audio_quality(input_filepath)
    return wav_filename, stoi, pesq, si_sdr

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', type=str, default='metadata.csv')
    parser.add_argument('--output', '-o', type=str, default='metrics.csv')
    parser.add_argument('--num_threads', '-n', type=int, default=4)  # Defina o número desejado de threads

    args = parser.parse_args()
    global input_dir 
    input_dir = dirname(args.input)

    with open(args.input, 'r') as infile, open(args.output, "w") as ofile:
        input_data = infile.readlines()[1:]
        separator = "|"

        with concurrent.futures.ThreadPoolExecutor(max_workers=args.num_threads) as executor:
            results = list(tqdm(executor.map(process_audio_file, input_data), total=len(input_data)))
        
        ofile.write("wav_filename|stoi|pesq|si_sdr\n")
        for result in results:
            wav_filename, stoi, pesq, si_sdr = result
            write_metrics(ofile, wav_filename, stoi, pesq, si_sdr)

if __name__ == "__main__":
    main()

