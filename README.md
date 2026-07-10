# WoW TalkToText

A local voice assistant for World of Warcraft Classic.

Speak into your microphone, convert speech to WoW chat commands, and paste directly into the game.

## Features

- 100% local speech recognition
- No API keys
- No cloud services
- Whisper.cpp backend
- CUDA GPU acceleration
- Mouse5 push-to-talk
- WoW chat command parsing
- Dungeon abbreviation correction
- Raid/tank voice commands

## Example

Say:

"guild looking for healer zf"

Output:

/g looking for healer Zul'Farrak


Say:

"slash cry"

Output:

/cry


Say:

"mark skull"

Output:

/tm 8

## Requirements

- Python 3.11+
- Windows
- NVIDIA GPU recommended
- whisper.cpp with CUDA support

## Setup

Install dependencies:


pip install -r requirements.txt


Download whisper.cpp from https://github.com/ggml-org/whisper.cpp/releases/download/v1.9.1/whisper-cublas-12.4.0-bin-x64.zip and place files in:



/whisper


Download model:


ggml-small.en.bin


Place it in:


/whisper/models


Run:


python main.py
