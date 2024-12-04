# Audio Merger

A command-line tool to merge multiple audio files into a single output 128KBs 2 channel stereo normalized MP3 file with tags taken from the first found in the input file.

Dumb as a donkey. This is the main advantage of that tool. Written by ChatGPT + Coder by kodu.ai. Uses ffmpeg.

## Features

- Input files: wav, mp3, ogg
- Output audio parameters:
  - Stereo (2 channels)
  - 44.1 KHz sample rate
  - Constant bitrate 128 kbps MP3

## Requirements

- Python 3.6+
- ffmpeg (required for MP3 encoding)
- Python packages listed in `requirements.txt` (may be outdated)

## Installation

1. Install ffmpeg for your operating system
2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

```bash
python audio_merger.py input1.wav input2.wav [input3.wav ...] [-o output_custom_file_name.mp3]
#merge list of input files given into an output file, default name output.mp3, may be customized
python audio_merger.py -w working_folder
#merge all audio files in the working folder given an output file with default name output.mp3
python audio_merger.py 
#merge all audio files in the current OS folder given an output file with default name output.mp3

```

