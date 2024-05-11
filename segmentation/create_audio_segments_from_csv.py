#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Adapted from https://gist.github.com/keithito/771cfc1a1ab69d1957914e377e65b6bd from Keith Ito: kito@kito.us
#
import argparse
from os.path import isfile, join
import librosa
import numpy as np
import pandas as pd
import os
import csv
from scipy.io.wavfile import write
import tqdm

class Segment:
  '''
  Linked segments lists
  '''
  def __init__(self, start, end):
    self.start = start
    self.end = end
    self.next = None
    self.gap = 0 # gap between segments (current and next)
    self.original_filename = None

  def set_next(self, next):
    self.next = next
    self.gap = next.start - self.end

  def set_filename_and_id(self, filename, id):
    self.filename = filename
    self.id = id

  def merge_from(self, next):
    # merge two segments (current and next)
    self.next = next.next
    self.gap = next.gap
    self.end = next.end

  def duration(self, sample_rate):
    return (self.end - self.start - 1) / sample_rate


def load_segments(filename):
    '''
    Read segments from csv file and recreate a segments list
    '''
    df = pd.read_csv(filename, sep = '|', header=None, quoting=csv.QUOTE_NONE)
    total = 0
    head = None
    for index, row in tqdm.tqdm(df.iterrows(), total=len(df[0])):
        # Build up a linked list of segments:
        segment = Segment(df.iloc[index,3], df.iloc[index,4])
        segment.set_filename_and_id(df.iloc[index, 1], df.iloc[index,0])
        segment.original_filename = df.iloc[index, 2]
        if head is None:
          head = segment
        else:
          prev.set_next(segment)
        prev = segment
        total += 1
    return head, total


def build_segments(args, segments, total_segments):
    '''
    Build best segments of wav files
    '''
    # Creates destination folder
    wav_dest_dir = args.output
    os.makedirs(wav_dest_dir, exist_ok=True)

    # Write segments to disk:
    s = segments
    i = 0
    filename = ''
    wav, sample_rate = '', 0
    while s != None:
      print('{} / {}'.format(i, total_segments))
      #if filename != s.original_filename:
      filename = s.source_filename
      out_filename = s.filename
      print('Loading file ' + filename)
      wav, sample_rate = librosa.load(os.path.join(args.input, filename), sr=args.sampling_rate)
      #segment_wav = (wav[s.start:s.end] * 32767).astype(np.int16)
      #
      # Adding 0.3 sec at the end of the file
      #
      #s.end += int(0.3 * sample_rate) 
      segment_wav = (wav[int(s.start):int(s.end)] * 32767).astype(np.int16)
      out_path = join(wav_dest_dir, out_filename)
      #librosa.output.write_wav(out_path, segment_wav, sample_rate)
      write(out_path, sample_rate, segment_wav)
      #duration += len(segment_wav) / sample_rate
      s = s.next
      i+=1


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--csvfile', default='segments.csv', help='Name of the csv file')
  parser.add_argument('--input', default='input', help='Name of the origin wav folder')
  parser.add_argument('--output', default='output', help='Name of wav folder')
  parser.add_argument('--sampling_rate', type=int, default=22050, help='Sampling rate')
  args = parser.parse_args()
  filename = args.csvfile
  segments, total_segments = load_segments(filename)
  build_segments(args, segments, total_segments)


if __name__ == "__main__":
  main()
