import queue
import sounddevice as sd
import vosk
import json
import pyttsx3
from agent_loop import process_user_input

# Initialize TTS engine
tts_engine = pyttsx3.init()

# Load Vosk model (offline STT)
model = vosk.Model("models/vosk-model-small-en-us-0.15")
audio_queue = queue.Queue()

def audio_callback(indata, frames, time, status):
    audio_queue.put(bytes(indata))

def start_listening():
    recognizer = vosk.KaldiRecognizer(model, 16000)

    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=audio_callback):

        while True:
            data = audio_queue.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "")
                if text:
                    handle_voice_command(text)

def handle_voice_command(text):
    response = process_user_input(text)
    speak(response)

def speak(text):
    tts_engine.say(text)
    tts_engine.runAndWait()