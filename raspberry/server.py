import socket
import board
import busio
import numpy as np
from sensor import Sensor


i2c = busio.I2C(board.SCL, board.SDA)
stick = Sensor(i2c)
stick.set_range_8g_2000dps()
stick.set_rate_208()

def start_udp_server(host="0.0.0.0", port=8080):

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:

        server_socket.bind(("", port))
        print(f"Listening: {host}:{port}")
        _, addr = server_socket.recvfrom(5)

        print(_)
        print(addr)

        while True:
            try:
                message = stick.get_calibrated_str()
                print(len(message))
                if len(message) != 194:
                    continue

                if addr:
                    server_socket.sendto(message.encode("utf-8"), addr)

            except Exception as e:
                print(f"Błąd: {e}")
                break


if __name__ == "__main__":
    try:
        start_udp_server()
    except KeyboardInterrupt:
        print("Serwer zakończony.")
