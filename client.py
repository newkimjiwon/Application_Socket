import socket
import threading
import struct
import time

user_ready = False

def receive_messages(client_socket):
    global user_ready
    while True:
        try:
            header = client_socket.recv(3)
            if not header:
                print("서버와의 연결이 끊어졌습니다.")
                break

            message_type, data_length = struct.unpack('!BH', header)

            if data_length > 0:  # 수신할 데이터가 있는 경우
                raw_message = client_socket.recv(data_length)
                # print(f"Received raw message: {raw_message}")  # 디버깅 정보
                message = raw_message.decode('utf-8', errors='replace')  # 오류 발생 시 대체 문자 사용
                if message_type == 0x03:  # 상태 업데이트 메시지 수신
                    if message == "READY":
                        user_ready = True
                        print("두 명의 사용자가 모두 연결되었습니다.")
                    else:
                        print()
                        print(f"서버로부터 수신된 상태 정보:\n{message}")
                        print("캐릭터의 행동을 입력하세요 (move: 'x,y', attack: 'target_name'): ", end = "")
        except Exception as e:
            print(f"에러 발생: {e}")
            break

def send_message(client_socket, message_type, message):
    try:
        data = struct.pack('!BH', message_type, len(message)) + message.encode('utf-8')  # UTF-8 인코딩 사용
        client_socket.send(data)
    except Exception as e:
        print(f"메시지 전송 중 에러 발생: {e}")

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 5555))

    # 캐릭터 이름 전송 (연결 요청 0x00)
    character_name = input("캐릭터 이름을 입력하세요 (영문 10자 이내): ")
    send_message(client_socket, 0x00, character_name)

    threading.Thread(target=receive_messages, args=(client_socket,)).start()

    while True:
        if user_ready:
            action = input("캐릭터의 행동을 입력하세요 (move: 'x,y', attack: 'target_name'): ")
            if "," in action:  # 이동 명령
                send_message(client_socket, 0x01, action)
            else:  # 공격 명령
                send_message(client_socket, 0x02, action)
        else:
            print("다른 사용자가 연결될 때까지 기다리는 중...")
            time.sleep(1)

if __name__ == "__main__":
    start_client()
