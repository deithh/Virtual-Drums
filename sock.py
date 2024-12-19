# Klient
import socket
import numpy as np

import pygame
import time
import random
from collections import deque
from pydub import AudioSegment, playback
import tempfile
from ahrs.filters import EKF
from ahrs.common.orientation import acc2q
import threading
import imufusion


def euler_to_rotation_matrix(roll, pitch, yaw):
    """
    Converts Euler angles (roll, pitch, yaw) to a 3x3 rotation matrix.
    Angles are assumed to be in radians.

    Parameters:
        roll (float): Rotation around the X-axis.
        pitch (float): Rotation around the Y-axis.
        yaw (float): Rotation around the Z-axis.

    Returns:
        numpy.ndarray: A 3x3 rotation matrix.
    """
    # Compute individual rotation matrices
    R_x = np.array(
        [[1, 0, 0], [0, np.cos(roll), -np.sin(roll)], [0, np.sin(roll), np.cos(roll)]]
    )

    R_y = np.array(
        [
            [np.cos(pitch), 0, np.sin(pitch)],
            [0, 1, 0],
            [-np.sin(pitch), 0, np.cos(pitch)],
        ]
    )

    R_z = np.array(
        [[np.cos(yaw), -np.sin(yaw), 0], [np.sin(yaw), np.cos(yaw), 0], [0, 0, 1]]
    )

    # Combine the rotation matrices
    R = R_z @ R_y @ R_x

    return R


def play_sound_async():
    def play():
        playback.play(sound)

    # Uruchamiamy odtwarzanie dźwięku w nowym wątku
    thread = threading.Thread(target=play, daemon=True)
    thread.start()


tempfile.tempdir = "temp2"
sound = AudioSegment.from_file("assets/snare.wav", format="wav")

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


def quaternion_to_rotation_matrix(q):
    w, x, y, z = q[0], q[1], q[2], q[3]
    R = np.array(
        [
            [1 - 2 * (y**2 + z**2), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x**2 + z**2), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x**2 + y**2)],
        ]
    )
    return R


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
        # print(f"Połączono z serwerem {host}:{port}")
        sample_rate = 100
        m = imufusion.Ahrs()
        data = client_socket.recv(195)  # Odbieranie odpowiedzi
        _, _, _, lastTime = clear_data(data.decode("utf-8"))

        while True:
            data, _ = client_socket.recvfrom(195)  # Odbieranie odpowiedzi

            mag, acc, gyr, time = clear_data(data.decode("utf-8"))

            m.update(gyr, acc, mag, 0.1)

            R = m.quaternion.to_matrix()
            # print(f"y: {angle_y}, gyr: {gyr[1]}")

            # if gyr_flag and gyr[1] > gyr_tresh and angle_y <= 0:
            #     gyr_flag = False
            #     play_sound_async()
            # if not gyr_flag and gyr[1] <= gyr_tresh:
            #     gyr_flag = True

            # last_angle = angle_y
            # last_accel = acc[1]
            # last_gyro = gyr[1]

            # if random.randint(0, 200) == 0:
            #     print(f"x:{angle_x * np.pi};y:{angle_y * np.pi};z:{angle_z * np.pi}")

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
