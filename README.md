# Useful Audio Scripts

Some useful scripts for audio


## Conversion

### Audio Format

Convert mp3 format audio to wav format: 

```bash
python conversion/convert_mp3_to_wav.py
```

Convert wav format audio to mp3 format: 

```bash
python conversion/convert_wav_to_mp3.py
```

## Wav Sampling rate

Convert sampling rate using sox:

```bash
python convert_sample_rate_with_sox.py
```

Convert sampling rate of a folders hierarchy reading files list from metadata file using librosa:

```bash
python convert_sample_rate_from_csv_with_librosa.py
```
