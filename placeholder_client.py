import socket
from gtts import gTTS
from pygame import mixer
import os
import time

mixer.init()



HOST = "0.0.0.0"
PORT = 5000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:
        prompt = input(">> ").strip()
        if prompt.lower() in ("exit", "quit"):
            break

        s.sendall(prompt.encode("utf-8"))

        reply_bytes = s.recv(65536)
        print(reply_bytes.decode("utf-8", errors="replace"))
        tts = gTTS(reply_bytes.decode("utf-8", errors="replace"))
        tts.save('response.mp3')
        mixer.music.load("response.mp3")
        mixer.music.set_volume(0.7)
        mixer.music.play()

        while mixer.music.get_busy():
            time.sleep(0.1)

