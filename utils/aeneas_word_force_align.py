"""
source: https://gist.github.com/johnmeade/80e411d6a9482c6b1ed4836820d85306

Note: Aeneas is based on TTS and DTW, which is not ideal for word-level alignment.
However, it is easy to install and works quite well, so it is still very useful.
This gist just lazily writes files to "/tmp" for demonstration purposes.
System and Python dependencies (Ubuntu):
    sudo apt-get install python-dev espeak espeak-data libespeak1 libespeak-dev ffmpeg
    pip install numpy textgrid
    pip install aeneas
Example:
    >>> txt = 'perry tells me that mister cole never touches malt liquor'
    >>> force_align(txt, 'cathy-low.wav')
    [
        ForceAlignedText(text='perry', start_sec=0.0, end_sec=0.4),
        ForceAlignedText(text='tells', start_sec=0.4, end_sec=0.68),
        ForceAlignedText(text='me', start_sec=0.68, end_sec=0.92),
        ForceAlignedText(text='that', start_sec=0.92, end_sec=1.12),
        ForceAlignedText(text='mister', start_sec=1.12, end_sec=1.28),
        ForceAlignedText(text='cole', start_sec=1.28, end_sec=1.68),
        ForceAlignedText(text='never', start_sec=1.68, end_sec=2.04),
        ForceAlignedText(text='touches', start_sec=2.04, end_sec=2.48),
        ForceAlignedText(text='malt', start_sec=2.48, end_sec=2.76),
        ForceAlignedText(text='liquor', start_sec=2.76, end_sec=3.32),
    ]
"""


import secrets
from pathlib import Path
from typing import NamedTuple

from aeneas.executetask import ExecuteTask
from aeneas.task import Task
from textgrid import TextGrid


class ForceAlignedText(NamedTuple):
    text: str
    start_sec: float
    end_sec: float


def force_align(txt, wav_fn, lang="eng"):
    sec = secrets.token_hex(8)
    txt_fn = Path("/tmp", sec + ".txt")
    tg_fn = Path("/tmp", sec + ".textgrid")

    # write words to file
    with txt_fn.open("w") as f:
        f.write("\n".join(txt.split()))

    # create aeneas Task object
    config_string = (
        f"task_language={lang}"
        "|is_text_type=plain"
        "|os_task_file_format=textgrid"
        "|mfcc_mask_nonspeech=True"
        "|mfcc_mask_nonspeech_l3=True"
    )
    task = Task(config_string=config_string)
    task.audio_file_path_absolute = str(wav_fn)
    task.text_file_path_absolute = str(txt_fn)
    task.sync_map_file_path_absolute = str(tg_fn)

    # process Task
    ExecuteTask(task).execute()
    task.output_sync_map_file()

    # read results
    textgrid = TextGrid.fromFile(tg_fn)
    tier = next(tier for tier in textgrid.tiers if tier.name == "Token")
    words = [
        ForceAlignedText(text=i.mark, start_sec=i.minTime, end_sec=i.maxTime)
        for i in tier.intervals
    ]
    return words