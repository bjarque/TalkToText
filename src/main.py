import os
import json
import time
import wave
import subprocess
import tempfile
import threading
import requests
import numpy as np
import sounddevice as sd
import pyperclip
import pyautogui
import time
import re
from pynput import mouse

import sounddevice as sd

from whisper_manager import WhisperServer


whisper = WhisperServer(
    "..//whisper//whisper-server.exe",
    "..//whisper//models//ggml-small.en.bin"
)

whisper.start()


print("Ready - hold Mouse5")


with open("..//config.json") as f:
    config = json.load(f)


with open("..//data//wow_words.json") as f:
    wow_words = json.load(f)



SAMPLE_RATE = config["sample_rate"]

WHISPER = config["whisper_exe"]

MODEL = config["model"]


# ============================
# STATE
# ============================

recording = False
audio = []

lock = threading.Lock()



# ============================
# AUDIO
# ============================

def audio_callback(
        indata,
        frames,
        time_info,
        status
):

    if recording:

        with lock:
            audio.append(
                indata.copy()
            )



stream = sd.InputStream(
    samplerate=SAMPLE_RATE,
    channels=1,
    device=config["input_device"],
    dtype="float32",
    callback=audio_callback
)
stream.start()



# ============================
# WAV SAVE
# ============================

def save_wav(filename, data):

    data = (
        data * 32767
    ).astype(np.int16)


    with wave.open(
        filename,
        "wb"
    ) as wf:

        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)

        wf.writeframes(
            data.tobytes()
        )



# ============================
# WHISPER
# ============================


def run_whisper(filename):

    with open(filename, "rb") as f:

        response = requests.post(
            "http://127.0.0.1:8080/inference",
            files={
                "file": f
            },
            data={
                "language": "en"
            }
        )


    result = response.json()

    return result.get("text", "").strip()


# ============================
# WOW FIXES
# ============================

def fix_words(text):

    lower = text.lower()


    for wrong, correct in wow_words.items():

        if wrong in lower:

            text = text.replace(
                wrong,
                correct
            )

            text = text.replace(
                wrong.title(),
                correct
            )


    return text



# ============================
# CHAT PREFIX
# ============================

import re


def clean_message(text):

    # Remove trailing punctuation
    text = text.strip()

    text = re.sub(
        r"[.!?,;:]+$",
        "",
        text
    )

    return text

import re

SLASH_COMMANDS = {

    # Chat channels
    "say": "/s",
    "guild": "/g",
    "party": "/p",
    "raid": "/ra",
    "officer": "/o",
    "yell": "/y",
    "trade": "/2",
    "general": "/1",
    "looking for group": "/4",

    # Social emotes
    "angry": "/angry",
    "applaud": "/applaud",
    "beg": "/beg",
    "bite": "/bite",
    "bleed": "/bleed",
    "blink": "/blink",
    "blush": "/blush",
    "boggle": "/boggle",
    "bonk": "/bonk",
    "bow": "/bow",
    "burp": "/burp",
    "bye": "/bye",
    "cackle": "/cackle",
    "cheer": "/cheer",
    "chicken": "/chicken",
    "chuckle": "/chuckle",
    "clap": "/clap",
    "confused": "/confused",
    "congratulate": "/congratulate",
    "cry": "/cry",
    "cuddle": "/cuddle",
    "dance": "/dance",
    "ding": "/ding",
    "doom": "/doom",
    "drink": "/drink",
    "drool": "/drool",
    "duck": "/duck",
    "eat": "/eat",
    "eye": "/eye",
    "fart": "/fart",
    "flee": "/flee",
    "flex": "/flex",
    "flirt": "/flirt",
    "flop": "/flop",
    "gasp": "/gasp",
    "gaze": "/gaze",
    "giggle": "/giggle",
    "glare": "/glare",
    "gloat": "/gloat",
    "greet": "/greet",
    "groan": "/groan",
    "grovel": "/grovel",
    "growl": "/growl",
    "grin": "/grin",
    "hug": "/hug",
    "kiss": "/kiss",
    "kneel": "/kneel",
    "laugh": "/laugh",
    "lay": "/lay",
    "lick": "/lick",
    "listen": "/listen",
    "lol": "/lol",
    "lost": "/lost",
    "love": "/love",
    "massage": "/massage",
    "moan": "/moan",
    "mock": "/mock",
    "moon": "/moon",
    "mourn": "/mourn",
    "nod": "/nod",
    "no": "/no",
    "nosepick": "/nosepick",
    "panic": "/panic",
    "pat": "/pat",
    "point": "/point",
    "poke": "/poke",
    "pray": "/pray",
    "purr": "/purr",
    "raise": "/raise",
    "roar": "/roar",
    "rolleyes": "/rolleyes",
    "rude": "/rude",
    "salute": "/salute",
    "scared": "/scared",
    "scratch": "/scratch",
    "sexy": "/sexy",
    "shake": "/shake",
    "shout": "/shout",
    "shrug": "/shrug",
    "sigh": "/sigh",
    "sit": "/sit",
    "sleep": "/sleep",
    "smile": "/smile",
    "smirk": "/smirk",
    "snicker": "/snicker",
    "sniff": "/sniff",
    "snub": "/snub",
    "spit": "/spit",
    "stare": "/stare",
    "surprised": "/surprised",
    "surrender": "/surrender",
    "talk": "/talk",
    "tap": "/tap",
    "tease": "/tease",
    "thank": "/thank",
    "threaten": "/threaten",
    "tickle": "/tickle",
    "train": "/train",
    "violin": "/violin",
    "wave": "/wave",
    "welcome": "/welcome",
    "whistle": "/whistle",
    "wink": "/wink",
    "work": "/work",
    "yawn": "/yawn",

        # Raid / tank commands
    "pulling": "/rw Pulling",
    "pull": "/rw Pulling",
    "ready check": "/readycheck",
    "ready": "/readycheck",
    "clear marks": "/cwm all",
    "clear markers": "/cwm all",

    # Target markers
    "skull": "/tm 8",
    "cross": "/tm 7",
    "square": "/tm 6",
    "triangle": "/tm 5",
    "diamond": "/tm 4",
    "moon": "/tm 3",
    "circle": "/tm 2",
    "star": "/tm 1",

    # Raid warnings
    "raid warning": "/rw",
    "warning": "/rw",

    # Crowd control reminders
    "sheep": "/rw Sheep",
    "trap": "/rw Trap",
    "sap": "/rw Sap",
    "hex": "/rw Hex",
    "banish": "/rw Banish",
    "fear": "/rw Fear",

    # Tank calls
    "wait": "/rw Wait",
    "hold": "/rw Hold",
    "go": "/rw Go",
    "incoming": "/rw Incoming",
    "my pull": "/rw My pull",

    # Utility
    "assist": "/assist",
    "target": "/target",
    "follow": "/follow",
    "stop": "/stopattack",
}


def clean_message(text):

    text = text.strip()

    # Remove ending punctuation
    text = re.sub(
        r"[.!?,;:]+$",
        "",
        text
    )

    return text


def capitalize_first_letter(text):
    if not text:
        return text

    return text[0].upper() + text[1:]
    
def parse_chat(text):

    text = clean_message(text);

    lower = text.lower().strip()


    # Remove "prefix"
    if lower.startswith("prefix "):

        text = text[7:].strip()
        lower = text.lower()



    # Handle:
    # slash cry
    # slash dance hello

    if lower.startswith("slash "):

        parts = text.split(
            maxsplit=2
        )

        command = parts[1].lower()

        if command in SLASH_COMMANDS:

            output = SLASH_COMMANDS[command]

            if len(parts) == 3:

                output += " " + parts[2]

            return output



    # Handle:
    # guild hello
    # party hello

    for word, command in SLASH_COMMANDS.items():

        if lower.startswith(word):

            message = text[len(word):].strip()

            # remove ":" or ","
            message = re.sub(
                r"^[\.\,\:\;\!\?]+\s*",
                "",
                message
            )
            
            if message:
                message = capitalize_first_letter(message)
                return f"{command} {message}"


            else:

                return command



    # Whisper:
    # whisper Thrall hello

    if lower.startswith("whisper"):

        parts = text.split(
            maxsplit=2
        )

        if len(parts) >= 3:

            return (
                f"/w {parts[1]} {parts[2]}"
            )


    return capitalize_first_letter(text)


def clean_message(text):

    text = text.strip()

    # Remove trailing punctuation
    text = re.sub(
        r"[.!?,;:]+$",
        "",
        text
    )

    # Normalize spaces
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text

# ============================
# TRANSCRIBE
# ============================

def transcribe():

    global audio


    with lock:

        if not audio:
            return


        data = np.concatenate(
            audio,
            axis=0
        )


        audio.clear()



    data = data.flatten()
    duration = len(data) / SAMPLE_RATE

    print(
        f"Recorded: {duration:.2f} seconds"
    )

    print(
        f"Audio level: {np.max(np.abs(data)):.4f}"
    )

    with tempfile.NamedTemporaryFile(
        suffix=".wav",
        delete=False
    ) as f:

        filename = f.name



    try:

        save_wav(
            filename,
            data
        )


        raw = run_whisper(
            filename
        )


    finally:

        os.remove(
            filename
        )



    print()
    print("================")
    print("RAW:")
    print(raw)
    print("================")


    if not raw:
        return



    fixed = fix_words(
        raw
    )


    final = parse_chat(
        fixed
    )


    print()
    print("================")
    print("OUTPUT:")
    print(final)
    print("================")


    pyperclip.copy(final)

    time.sleep(0.15)
    pyautogui.press(
        "enter"
    )
    pyautogui.hotkey(
        "ctrl",
        "v"
    )

    time.sleep(0.1)

   
    print(
        "Copied to clipboard"
    )



# ============================
# BUTTON CONTROL
# ============================

def start():

    global recording


    if recording:
        return


    with lock:
        audio.clear()


    recording = True


    print(
        "🎤 Listening..."
    )



def stop():

    global recording


    if not recording:
        return


    recording = False


    print(
        "Processing..."
    )


    threading.Thread(
        target=transcribe,
        daemon=True
    ).start()



def mouse_event(
        x,
        y,
        button,
        pressed
):

    if button == mouse.Button.x2:


        if pressed:
            start()

        else:
            stop()



# ============================
# START
# ============================


print()
print("==========================")
print(" WoW Talk-To-Text")
print("==========================")
print()
print("Hold Mouse5 and speak")
print("Release Mouse5")
print()


listener = mouse.Listener(
    on_click=mouse_event
)

listener.start()

listener.join()
