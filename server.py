import socket
import threading

clients = []

def handle_client(client_socket, client_address):
    global clients
    print(f"클라이언트 {client_address} 연결됨")

    # 두 명의 클라이언트가 연결되면 READY 메시지 전송
    if len(clients) == 2:
        for client in clients:
            client.send("READY".encode('utf-8'))

    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                print(f"{client_address}로부터 수신된 메시지: {message}")
                broadcast(message, client_socket)
            else:
                remove_client(client_socket)
                break
        except:
            remove_client(client_socket)
            break

def broadcast(message, sender_socket):
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message.encode('utf-8'))
            except:
                remove_client(client)

def remove_client(client_socket):
    if client_socket in clients:
        clients.remove(client_socket)

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 5555))
    server_socket.listen(2)  # 최대 2개의 클라이언트 수용

    print("서버가 시작되었습니다. 클라이언트를 기다립니다...")

    while True:
        client_socket, client_address = server_socket.accept()
        clients.append(client_socket)
        threading.Thread(target=handle_client, args=(client_socket, client_address)).start()

if __name__ == "__main__":
    start_server()