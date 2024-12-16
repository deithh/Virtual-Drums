# Klient
import socket
import numpy as np
from madgwick_py.madgwickahrs import MadgwickAHRS
import pygame
import time
import random
from collections import deque
from pydub import AudioSegment, playback
import tempfile
from scipy.spatial.transform import Rotation

import threading


def play_sound_async(s):
    def play():
        playback.play(s)

    # Uruchamiamy odtwarzanie dźwięku w nowym wątku
    thread = threading.Thread(target=play, daemon=True)
    thread.start()


tempfile.tempdir = "temp2"
snare = AudioSegment.from_file("snare.wav", format="wav")
hihat = AudioSegment.from_file("hihat.wav", format="wav")
perc = AudioSegment.from_file("perc.wav", format="wav")

cube_vertices = [
    [-1, -1, -1],
    [1, -1, -1],
    [1, 1, -1],
    [-1, 1, -1],
    [-1, -1, 1],
    [1, -1, 1],
    [1, 1, 1],
    [-1, 1, 1],
]
cube_vertices = np.array(cube_vertices)

# Define the edges connecting the vertices
edges = [
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 0),  # Back face
    (4, 5),
    (5, 6),
    (6, 7),
    (7, 4),  # Front face
    (0, 4),
    (1, 5),
    (2, 6),
    (3, 7),  # Connecting edges
]

cd = ""


def draw_axes(screen, R, width, height, scale=100):
    axes = [
        [0, 0, 0],
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1],
    ]
    rotated_axes = rotate_points(axes, R)
    projected_axes = project_points(rotated_axes, width, height, scale)

    # Draw X axis (red)
    pygame.draw.line(screen, (255, 0, 0), projected_axes[0], projected_axes[1], 2)
    # Draw Y axis (green)
    pygame.draw.line(screen, (0, 255, 0), projected_axes[0], projected_axes[2], 2)
    # Draw Z axis (blue)
    pygame.draw.line(screen, (0, 0, 255), projected_axes[0], projected_axes[3], 2)


def clear_data(row: str):
    row = row.replace(" ", "")
    row = list(map(float, row.split(";")))
    mag = np.asarray(row[:3])
    acc = np.asarray(row[3:6])
    gyr = np.asarray(row[6:9])

    time = row[-1]

    return mag, acc, gyr, time


def rotate_points(points, R):
    return [np.dot(R, p) for p in points]


def project_points(points, width, height, scale=50):
    projected = []
    for p in points:
        x = int(width / 2 + scale * p[0])
        y = int(height / 2 - scale * p[1])
        projected.append((x, y))
    return projected


def start_client():
    host = "192.168.1.14"  # Adres IP serwera
    port = 8080  # Port serwera

    pygame.init()

    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Quaternion Rotation Visualization")

    # Tworzenie gniazda klienta
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
        # client_socket.connect((host, port))
        addr = ("192.168.1.14", 8080)
        client_socket.sendto("chuj\n".encode("utf-8"), addr)
        print(f"Połączono z serwerem {host}:{port}")
        m = MadgwickAHRS()
        last_angle = 0

        angle_x, angle_y, angle_z = 0, 0, 0

        last_gyro = 0
        last_accel = 0
        data = client_socket.recv(195)  # Odbieranie odpowiedzi
        _, _, _, lastTime = clear_data(data.decode("utf-8"))
        last_accel
        gyr_flag = True
        gyr_tresh = 10
        while True:
            data, _ = client_socket.recvfrom(195)  # Odbieranie odpowiedzi

            mag, acc, gyr, time = clear_data(data.decode("utf-8"))

            m.samplePeriod = time - lastTime
            # period = time - lastTime
            m.update(gyr, acc, mag)
            lastTime = time
            # m.update_imu(gyr, acc)

            angle_x, angle_y, angle_z = m.quaternion.to_euler_angles()

            

            # angle_x -= gyr[0] * period
            # angle_y -= gyr[1] * period
            # angle_z -= gyr[2] * period


            # print(f"x: {angle_x}, y: {angle_y},z: {angle_z}, gyr: {gyr[1]}")


            if gyr_flag and gyr[1] > gyr_tresh :
                gyr_flag = False

                if angle_z > 0.5:
                    play_sound_async(hihat)
                elif angle_z < -0.5:
                    play_sound_async(snare)
                else:
                    play_sound_async(perc)

            if not gyr_flag and gyr[1] <= gyr_tresh:
                gyr_flag = True

            last_angle = angle_y
            last_accel = acc[1]
            last_gyro = gyr[1]

            # if random.randint(0, 200) == 0:
            #     print(f"x:{angle_x * np.pi};y:{angle_y * np.pi};z:{angle_z * np.pi}")

            R = m.quaternion.quaternion_to_rotation_matrix()

            angles = Rotation.from_matrix(R).as_euler('xyz', degrees=True)
            print(angles)
            # Rotate and project cube vertices
            rotated_vertices = rotate_points(cube_vertices, R)
            projected_vertices = project_points(rotated_vertices, width, height)

            # Clear screen
            screen.fill((0, 0, 0))
            draw_axes(screen, R, width, height)

            # Draw edges
            for edge in edges:
                pygame.draw.line(
                    screen,
                    (255, 255, 255),
                    projected_vertices[edge[0]],
                    projected_vertices[edge[1]],
                    2,
                )

            pygame.display.flip()


if __name__ == "__main__":
    start_client()
