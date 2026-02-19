import socket
from ollama import chat
from ollama import ChatResponse
import json
import os
import pyttsx3
from pygame import mixer
import pyaudio
import multiprocessing

def generate_audio(text):
    # Initialize engine in a separate process
    engine = pyttsx3.init()
    if os.path.exists('response.wav'):
        os.remove('response.wav')
    engine.save_to_file(text, 'response.wav')
    engine.runAndWait()

def main():
    mixer.init()
    # engine = pyttsx3.init()

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
                            history = json.load(f)

                    else:
                        history = []

                    history.append({"role": 'user', "content": text})
                    print(f"Received command: {text}")
                    messages = [
                            {
                                "role": "system",
                                "content": "You are Finn, a nonchalant and overall chill guy. when responding the structure you use is give a short response and then a short explanation. exceptions to this are if the prompt needs further explaining you can go ahead, or if its something simple like a greeting or something then reply with things like hey, yo, whats up, etc. just explain in paragraphs no specialised characters or text ",
                            } 
                        ] + history

                    # send command to ai model
                    print("Querying AI model...")
                    response = chat(
                        model='gemma3:1b',
                        messages = messages,
                    )

                    reply = response.message.content
                    print(f"AI Reply: {reply}")

                    # save command + response to json
                    history.append({
                        "role": "assistant",
                        "content": reply,
                    })

                    MAXI = 10
                    if len(history) > MAXI:
                        history = history[-MAXI:]

                    with open(FILE, "w") as f:
                        json.dump(history, f, indent=2)

                    if not reply.strip():
                        reply = "I didn't catch that."

                    print("Generating audio...")
                    
                    # Run audio generation in a separate process
                    # This prevents pyttsx3 loop from hanging the main process
                    p = multiprocessing.Process(target=generate_audio, args=(reply,))
                    p.start()
                    p.join()
                    
                    with open('response.wav', 'rb') as f:
                        audio_bytes = f.read()
                        print(f"Audio generated. Size: {len(audio_bytes)} bytes")
                        print("Sending header...")
                        conn.sendall(len(audio_bytes).to_bytes(8, byteorder='big'))
                        print("Sending audio data...")
                        conn.sendall(audio_bytes)
                        print("Sent audio.")


                    # conn.sendall(reply.encode("utf-8"))
                                    
if __name__ == "__main__":
    main()