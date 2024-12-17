# Klient
import socket
import numpy as np

import pygame

from pydub import AudioSegment, playback
import tempfile
from scipy.spatial.transform import Rotation
import ahrs

from cube import cube_vertices, cube_edges

import threading

import numpy as np

snare = AudioSegment.from_file("../assets/snare.wav", format="wav")
hihat = AudioSegment.from_file("../assets/snare.wav", format="wav")
perc = AudioSegment.from_file("../assets/snare.wav", format="wav")
width, height = 800, 600


def play_sound_async(s):
    def play():
        playback.play(s)

    thread = threading.Thread(target=play, daemon=True)
    thread.start()


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


def project_points(points, width, height, scale=50):
    projected = []
    for p in points:
        x = int(width / 2 + scale * p[0])
        y = int(height / 2 - scale * p[1])
        projected.append((x, y))
    return projected


def init_pygame():
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Quaternion Rotation Visualization")

    return screen


def draw_all(screen, R):
    rotated_vertices = rotate_points(cube_vertices, R)
    projected_vertices = project_points(rotated_vertices, width, height)

    screen.fill((0, 0, 0))
    draw_axes(screen, R, width, height)

    for edge in cube_edges:
        pygame.draw.line(
            screen,
            (255, 255, 255),
            projected_vertices[edge[0]],
            projected_vertices[edge[1]],
            2,
        )

    pygame.display.flip()


def start_client(host="192.168.1.14", port=8080):

    screen = init_pygame()

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:

        addr = (host, port)
        client_socket.sendto("chuj\n".encode("utf-8"), addr)
        print(f"Połączono z serwerem {host}:{port}")

        last_angle = 0
        angle_x, angle_y, angle_z = 0, 0, 0
        last_gyro = 0
        last_accel = 0
        gyr_tresh = 10
        gyr_flag = True

        m = ahrs.filters.Madgwick(gain=0.05, gain_marg=0.05)
        # get inital position
        data = client_socket.recv(195)
        mag, acc, gyr, time = clear_data(data.decode("utf-8"))
        q = np.array([1, 0, 0, 0], dtype=np.float64)
        for _ in range(5000):
            q = m.updateMARG(q, gyr, acc, mag)

        while True:
            data, _ = client_socket.recvfrom(195)

            mag, acc, gyr, time = clear_data(data.decode("utf-8"))
            q = m.updateMARG(q, gyr, acc, mag)
            R = quaternion_to_rotation_matrix(q)

            if gyr_flag and gyr[1] > gyr_tresh:
                gyr_flag = False

                if angle_z > 0.5:
                    play_sound_async(hihat)
                elif angle_z < -0.5:
                    play_sound_async(snare)
                else:
                    play_sound_async(perc)

            if not gyr_flag and gyr[1] <= gyr_tresh:
                gyr_flag = True

            angles = Rotation.from_matrix(R).as_euler("xyz", degrees=True)
            print(angles)

            draw_all(screen, R)


if __name__ == "__main__":
    tempfile.tempdir = "temp2"
    start_client()
