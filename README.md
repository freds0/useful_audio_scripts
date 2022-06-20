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

## Segmentation

## Segment wavs

Creating several file segments from one audio file.

```bash
python segmentation/segment_audio.py
```

## Change Segment wavs

You can change the segments, for example, adding 0.3 seconds at the end of each segment.

```bash
python segmentation/change_segments.py
```

## Normalization

Normalize audios by mean dBfs.

```bash
python normalization/normalize_audios_by_dbfs.py
```

Normalize audios by max volume using pydub.

```bash
python normalization/normalize_audios_by_max_volume.py
```
 
