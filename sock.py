# Klient
import socket
import numpy as np
from madgwick_py.madgwickahrs import MadgwickAHRS
import pygame
import time

cube_vertices = [
    [-1, -3, -1],
    [1, -3, -1],
    [1, 3, -1],
    [-1, 3, -1],
    [-1, -3, 1],
    [1, -3, 1],
    [1, 3, 1],
    [-1, 3, 1],
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
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))
        print(f"Połączono z serwerem {host}:{port}")
        m = MadgwickAHRS()
        data = client_socket.recv(195)  # Odbieranie odpowiedzi
        _, _, _, lastTime = clear_data(data.decode("utf-8"))
        while True:
            data = client_socket.recv(195)  # Odbieranie odpowiedzi
            mag, acc, gyr, time = clear_data(data.decode("utf-8"))
            print(time - lastTime)
            m.samplePeriod = time - lastTime
            lastTime = time
            m.update(gyr, acc, mag)

            R = m.quaternion.quaternion_to_rotation_matrix()
            # Rotate and project cube vertices
            rotated_vertices = rotate_points(cube_vertices, R)
            projected_vertices = project_points(rotated_vertices, width, height)

            # Clear screen
            screen.fill((0, 0, 0))

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
