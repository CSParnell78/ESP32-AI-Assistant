import socket
import os
import time
import pyaudio
from pygame import mixer

import speech_recognition as sr

mixer.init()

HOST = "192.168.68.146"
PORT = 5000

r = sr.Recognizer()

recognize_speech = True

os.system("cls")
print("Welcome to This chabot demo.")
print("Speak something out loud for a reply")
print("Enjoy!")

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
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")

        s.sendall(text.encode("utf-8"))
        
        # read the header
        header = s.recv(8)

        file_size = int.from_bytes(header, byteorder="big")

        # loop until we have all data
        audio_data = b""
        while len(audio_data) < file_size:
            remaining = file_size - len(audio_data)
            audio_data += s.recv(4096 if remaining > 4096 else remaining)

        # stop already playing audio
        mixer.music.stop()
        mixer.music.unload()


        with open('incoming_audio.mp3', 'wb') as f:
            f.write(audio_data)
        
        try:
            # load and play audio
            mixer.music.load("incoming_audio.mp3")
            mixer.music.play()
            # stop from recognizing speech
            recognize_speech = False
            # Wait until playback finishes
            while mixer.music.get_busy():
                time.sleep(0.1)
            # start recognizing speech
            recognize_speech = True

        except pygame.error as e:
            print(f"error playing audio: {e}")

