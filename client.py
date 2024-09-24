import socket
import threading

# 두 명의 사용자가 모두 연결될 때까지 기다리도록 설정
user_ready = False

def receive_messages(client_socket):
    global user_ready
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message == "READY":
                user_ready = True
                print("두 명의 사용자가 모두 연결되었습니다.")
            else:
                print(f"서버로부터 수신된 메시지: {message}")
        except:
            print("서버 연결 끊김")
            break

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 5555))

    threading.Thread(target=receive_messages, args=(client_socket,)).start()

    while True:
        if user_ready:
            message = input("캐릭터의 움직임 (ex: x, y 좌표): ")
            client_socket.send(message.encode('utf-8'))
        else:
            print("다른 사용자가 연결될 때까지 기다리는 중...")

if __name__ == "__main__":
    start_client()