import socket
import os
import time
import pyaudio
from pygame import mixer

mixer.init()

HOST = "192.168.68.146"
PORT = 5000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:
        prompt = input(">> ").strip()
        if prompt.lower() in ("exit", "quit"):
            break

        s.sendall(prompt.encode("utf-8"))
        
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

        except pygame.error as e:
            print(f"error playing audio: {e}")

