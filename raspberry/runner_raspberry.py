import socket
import board
import busio
import numpy as np
from sensor import Sensor
from pydub import AudioSegment, playback
import tempfile
from scipy.spatial.transform import Rotation
import ahrs
import time

import threading

#zolty scl

snare = AudioSegment.from_file("../assets/snare.wav", format="wav")
hihat = AudioSegment.from_file("../assets/klask.wav", format="wav")
perc = AudioSegment.from_file("../assets/perc.wav", format="wav")
width, height = 800, 600

import os
import sys
from contextlib import redirect_stdout, redirect_stderr

i2c = busio.I2C(board.SCL, board.SDA)
stick = Sensor(i2c)
stick.set_range_8g_2000dps()
# stick.set_rate_208()

def start_udp_server(host="0.0.0.0", port=8080):
    last_angle = 0
    angle_x, angle_y, angle_z = 0, 0, 0
    last_gyro = 0
    last_accel = 0
    gyr_tresh = 10
    gyr_flag = True

    m = ahrs.filters.Madgwick(gain=0.043)

    acc, gyr, mag = stick.get_calibrated()
    time_temp = time.time()

    lastTime = time_temp
    q = np.array([1, 0, 0, 0], dtype=np.float64)
    for _ in range(5000):
        q = m.updateMARG(q, gyr, acc, mag)

    print("Calibration done")
    while True:

        acc, gyr, mag = stick.get_calibrated()
        time_temp = time.time()
        deltaTime = time_temp - lastTime
        # print(deltaTime)
        lastTime = time_temp
        m.Dt = deltaTime  # wywalić jak przestanie działać
        q = m.updateMARG(q, gyr, acc, mag)
        rotation = Rotation.from_quat(np.roll(q, -1))
        R = rotation.as_matrix()
        angle_x, angle_y, angle_z = rotation.as_euler("xyz", degrees=True)

        angle_tresh = 600
        angle_z_base = 80
        angle_diff = (angle_y - last_angle) / deltaTime
        shifted = pseudomodulo(angle_z, angle_z_base)
        # print(f"ad:{angle_diff}     y:{angle_y}")
        # print(f"z:{shifted}    y:{angle_y}")
        if gyr_flag and angle_diff > angle_tresh and angle_y > -90 and angle_y < 30:
            print(f"z:{shifted}    y:{angle_y}")
            gyr_flag = False

            if angle_y < -50:
                if shifted > 30 and shifted < 90:
                    print(1)
                    play_sound_async(hihat)
                if shifted < -30 and shifted > -90:
                    print(2)
                    play_sound_async(hihat)
            else:
                if shifted > -135 and shifted < -45:
                    print(3)
                    play_sound_async(snare)
                elif shifted >= -45 and shifted < 0:
                    print(4)
                    play_sound_async(perc)
                elif shifted >= 0 and shifted < 45:
                    print(5)
                    play_sound_async(perc)
                elif shifted >= 45 and shifted < 135:
                    print(6)
                    play_sound_async(snare)

        if not gyr_flag and angle_diff <= angle_tresh:
            gyr_flag = True

        last_angle = angle_y


def play_sound_async(s):
    def play():
        playback.play(s)

    # Create and start the daemon thread
    thread = threading.Thread(target=play, daemon=True)
    thread.start()

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

def pseudomodulo(val, base):
    temp = val - base
    if temp < -180:
        return temp + 360
    if temp > 180:
        return temp - 360
    return temp

if __name__ == "__main__":
    try:
        start_udp_server()
    except KeyboardInterrupt:
        print("Serwer zakończony.")
