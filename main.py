import socket
from ollama import chat
from ollama import ChatResponse
import json
import os

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
                            "content": "keep responses ultra short, sentences when you can, the responses should be no bullshit and to the point, always be accurate with information especifally when asked something specific, no emojis",
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

                data.append({
                    "role": "user",
                    "content": text
                })
                MAXI = 50
                if len(data) > MAXI:
                    data = data[-MAXI:]

                with open(FILE, "w") as f:
                    json.dump(data, f, indent=2)

                conn.sendall(reply.encode("utf-8"))
                                
    