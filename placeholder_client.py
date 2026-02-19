import socket
import os
import time
import pyaudio
from pygame import mixer

import io
import speech_recognition as sr

mixer.init()

HOST = "192.168.68.146"
PORT = 5000

r = sr.Recognizer()

recognize_speech = True

os.system("cls")
print("""
████████████████████████████████████████████████
█▄─█▀▀▀█─▄█▄─▄▄─█▄─▄███─▄▄▄─█─▄▄─█▄─▀█▀─▄█▄─▄▄─█
██─█─█─█─███─▄█▀██─██▀█─███▀█─██─██─█▄█─███─▄█▀█
▀▀▄▄▄▀▄▄▄▀▀▄▄▄▄▄▀▄▄▄▄▄▀▄▄▄▄▄▀▄▄▄▄▀▄▄▄▀▄▄▄▀▄▄▄▄▄▀""")
print("Just say something out loud to start")
print("More information here: https://github.com/CSParnell78/ESP32-AI-Assistant/tree/main")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:
        # prompt = input(">> ").strip()
        # if prompt.lower() in ("exit", "quit"):
        #     break

        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source)
        try:
            if recognize_speech == True:
                text = r.recognize_google(audio)
        except sr.UnknownValueError:
            print("Sorry, I could not understand the audio.")
            continue
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            continue

        print(f"Sending text: {text}")
        s.sendall(text.encode("utf-8"))
        
        # read the header
        print("Waiting for response header...")
        header = s.recv(8)
        if not header:
            print("Connection closed by server.")
            break

        file_size = int.from_bytes(header, byteorder="big")
        print(f"Expecting file size: {file_size} bytes")

        # loop until we have all data
        audio_data = b""
        while len(audio_data) < file_size:
            remaining = file_size - len(audio_data)
            chunk = s.recv(4096 if remaining > 4096 else remaining)
            if not chunk:
                print("Connection closed unexpectedly while downloading audio.")
                break
            audio_data += chunk
            # print(f"Received {len(audio_data)}/{file_size} bytes", end='\r')
        
        print(f"\nDownload complete. Total received: {len(audio_data)} bytes")

        # stop already playing audio
        mixer.music.stop()
        mixer.music.unload()

        with open('incoming_audio.wav', 'wb') as f:
            f.write(audio_data)
        
        try:
            # load and play audio from memory to avoid file locking
            audio_stream = io.BytesIO(audio_data)
            mixer.music.load(audio_stream)
            mixer.music.play()
            
            # stop from recognizing speech
            recognize_speech = False
            # Wait until playback finishes
            while mixer.music.get_busy():
                time.sleep(0.1)
            # start recognizing speech
            recognize_speech = True

        except mixer.error as e:
            print(f"error playing audio: {e}")
