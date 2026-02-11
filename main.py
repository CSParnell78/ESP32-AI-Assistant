import socket
from ollama import chat
from ollama import ChatResponse


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

                # 1. Convert bytes → string
                text = data.decode("utf-8").strip()

                # 2. Send string to model
                response = chat(
                    model='gemma3:1b',
                    messages=[
                        {
                            'role': 'user',
                            'content': text,
                        },
                    ],
                )

                # 3. Get model reply
                reply = response.message.content

                # 4. Convert reply → bytes and send
                conn.sendall(reply.encode("utf-8"))
                                
    