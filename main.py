import socket
from ollama import chat
from ollama import ChatResponse
import json
import os
from gtts import gTTS
from pygame import mixer
import pyaudio

mixer.init()

# setup tcp server
HOST = '0.0.0.0'
PORT = 5000

# you need to classify what protocol and socket type
# 'AF_INET' is the IP_V4 protocol  'SOCK_STREAM' is the socket type (tcp)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: 
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    print(f"listening {HOST}:{PORT}")

    while True:
        conn, addr = s.accept()
        print(f"connected {addr}")
        
        with conn:
            while True:
                data = conn.recv(1024)

                if not data:
                    print(f"disconnected {addr}")
                    break

                # decode command
                text = data.decode("utf-8").strip()

                
                FILE = "memory.json"
                if os.path.exists(FILE):
                    with open(FILE, "r") as f:
                        data = json.load(f)

                else:
                    data = []

                data.append({"role": 'user', "content": text})
                messages = [
                        {
                            "role": "system",
                            "content": "You are Finn, a nonchalant and overall chill guy. when responding the structure you use is give a short response and then a short explanation. exceptions to this are if the prompt needs further explaining you can go ahead, or if its something simple like a greeting or something then reply with things like hey, yo, whats up, etc. just explain in paragraphs no specialised characters or text ",
                        } 
                    ] + data

                # send command to ai model
                response = chat(
                    model='gemma3:1b',
                    messages = messages,
                )

                reply = response.message.content

                # save command + response to json
                data.append({
                    "role": "assistant",
                    "content": reply,
                })

                MAXI = 10
                if len(data) > MAXI:
                    data = data[-MAXI:]

                with open(FILE, "w") as f:
                    json.dump(data, f, indent=2)

                if not reply.strip():
                    reply = "I didn't catch that."

                tts = gTTS(reply, lang="en")                

                tts.save('response.mp3')
                
                with open('response.mp3', 'rb') as f:
                    audio_bytes = f.read()
                    conn.sendall(len(audio_bytes).to_bytes(8, byteorder='big'))
                    conn.sendall(audio_bytes)


                # conn.sendall(reply.encode("utf-8"))
                                
    