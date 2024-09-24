import socket
import threading

# 클라이언트 소켓을 저장할 리스트 (현재 연결된 클라이언트들)
clients = []

# 클라이언트가 서버에 연결될 때마다 호출되는 함수
def handle_client(client_socket, client_address):
    global clients
    print(f"클라이언트 {client_address} 연결됨")

    # 두 명의 클라이언트가 연결되면 READY 메시지를 전송
    if len(clients) == 2:
        for client in clients:
            # READY 메시지를 두 클라이언트에게 전송하여 두 명이 모두 연결됨을 알림
            client.send("READY".encode('utf-8'))

    # 클라이언트와 지속적으로 통신을 유지하는 루프
    while True:
        try:
            # 클라이언트로부터 메시지를 수신 (최대 1024 바이트)
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                print(f"{client_address}로부터 수신된 메시지: {message}")
                # 받은 메시지를 다른 클라이언트들에게 전송
                broadcast(message, client_socket)
            else:
                # 메시지가 없으면 해당 클라이언트 연결 종료
                remove_client(client_socket)
                break
        except:
            # 예외 발생 시 해당 클라이언트 연결 종료
            remove_client(client_socket)
            break

# 메시지를 모든 클라이언트에게 전송하는 함수
def broadcast(message, sender_socket):
    for client in clients:
        if client != sender_socket:  # 메시지를 보낸 클라이언트에는 다시 전송하지 않음
            try:
                client.send(message.encode('utf-8'))  # 메시지를 다른 클라이언트들에게 전송
            except:
                # 메시지 전송 실패 시 해당 클라이언트를 제거
                remove_client(client)

# 클라이언트를 리스트에서 제거하는 함수
def remove_client(client_socket):
    if client_socket in clients:
        clients.remove(client_socket)  # 클라이언트를 리스트에서 제거

# 서버를 시작하는 함수
def start_server():
    # 소켓 생성 (AF_INET은 IPv4, SOCK_STREAM은 TCP 소켓 사용)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # 서버 소켓을 '0.0.0.0' IP와 포트 5555에 바인딩
    server_socket.bind(('0.0.0.0', 5555))
    
    # 서버가 클라이언트의 연결을 대기 (최대 2개의 클라이언트를 수용)
    server_socket.listen(2)

    print("서버가 시작되었습니다. 클라이언트를 기다립니다...")

    # 클라이언트가 연결될 때마다 처리
    while True:
        # 클라이언트 연결 수락
        client_socket, client_address = server_socket.accept()
        # 연결된 클라이언트 소켓을 리스트에 추가
        clients.append(client_socket)
        # 각 클라이언트 처리를 위한 새로운 스레드 생성
        threading.Thread(target=handle_client, args=(client_socket, client_address)).start()

# 프로그램의 시작점
if __name__ == "__main__":
    start_server()  # 서버 시작