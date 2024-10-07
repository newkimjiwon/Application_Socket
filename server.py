import socket
import threading
import struct
import time

# 클라이언트 상태 저장을 위한 리스트
clients = []
character_states = {}  # 각 캐릭터의 상태 정보 저장 (이름: (x, y, health, attack))

# 클라이언트가 서버에 연결될 때마다 호출되는 함수
def handle_client(client_socket, client_address):
    global clients, character_states
    print(f"클라이언트 {client_address} 연결됨")

    while True:
        try:
            header = client_socket.recv(3)
            if not header:
                print(f"클라이언트 {client_address}와의 연결이 끊어짐")
                remove_client(client_socket)
                break

            message_type, data_length = struct.unpack('!BH', header)
            message = client_socket.recv(data_length).decode('utf-8')

            if message_type == 0x00:  # 연결 요청
                print(f"연결 요청 - 캐릭터 이름: {message}")
                character_states[client_socket] = (message, 0, 0, 500, 10)  # 초기 상태 설정
            elif message_type == 0x01:  # 위치 업데이트
                print(f"위치 업데이트 - 좌표: {message}")
                name, _, _, health, attack = character_states[client_socket]
                x, y = map(int, message.split(','))
                character_states[client_socket] = (name, x, y, health, attack)
            elif message_type == 0x02:  # 공격 명령
                target_name = message
                print(f"공격 명령 - 타겟: {target_name}")
                # 공격 로직 처리
                for target_socket, state in character_states.items():
                    if state[0] == target_name:  # 공격할 캐릭터 찾기
                        target_health = state[3]  # 현재 체력
                        if target_health > 0:  # 체력이 0보다 클 때만 감소
                            target_health -= 10  # 공격력에 따라 체력 감소
                            # 체력 업데이트
                            name, x, y, _, attack = state
                            character_states[target_socket] = (name, x, y, target_health, attack)
                            print(f"{target_name}의 체력이 {target_health}으로 감소했습니다.")
                        break

            # 서버 애플리케이션은 20ms 주기로 연결된 모든 클라이언트 애플리케이션에게 모든 사용자들의 캐릭터 상태 정보를 제공
            time.sleep(0.02)
            # 상태 업데이트 메시지를 모든 클라이언트에게 전송
            broadcast_state_update()
        except Exception as e:
            print(f"에러 발생: {e}")
            remove_client(client_socket)
            break

# 상태 업데이트 메시지를 모든 클라이언트에게 전송하는 함수
def broadcast_state_update():
    global clients, character_states
    state_message = ""
    for client, state in character_states.items():
        name, x, y, health, attack = state
        state_message += f"{name} 위치: {x} {y}, 체력: {health}, 공격력: {attack}\n"

    for client in clients:
        try:
            send_message(client, 0x03, state_message)
        except Exception as e:
            print(f"상태 업데이트 전송 중 에러: {e}")
            remove_client(client)

# 메시지를 클라이언트에게 전송하는 함수
def send_message(client_socket, message_type, message):
    try:
        data = struct.pack('!BH', message_type, len(message)) + message.encode('utf-8')
        client_socket.send(data)
    except Exception as e:
        print(f"메시지 전송 중 에러: {e}")

# 클라이언트를 리스트에서 제거하는 함수
def remove_client(client_socket):
    if client_socket in clients:
        clients.remove(client_socket)
        del character_states[client_socket]

# 서버를 시작하는 함수
def start_server():
    global clients
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 5555))
    server_socket.listen(2)

    print("서버가 시작되었습니다. 클라이언트를 기다립니다...")

    while True:
        client_socket, client_address = server_socket.accept()
        clients.append(client_socket)

        if len(clients) == 2:  # 두 명의 클라이언트가 연결되면 READY 메시지 전송
            for client in clients:
                send_message(client, 0x03, "READY")

        threading.Thread(target=handle_client, args=(client_socket, client_address)).start()

# 프로그램의 시작점
if __name__ == "__main__":
    start_server()