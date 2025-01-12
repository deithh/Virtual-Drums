import board
import busio
from adafruit_extended_bus import ExtendedI2C as I2C
import numpy as np
from sensor import Sensor
from pydub import AudioSegment
from scipy.spatial.transform import Rotation
import ahrs
import time
import threading
import RPi.GPIO as GPIO
import pygame

dub_snare = AudioSegment.from_file("../assets/snare.mp3")
dub_hihat = AudioSegment.from_file("../assets/klask.mp3")
dub_lowerInnerDrum = AudioSegment.from_file("../assets/perc.mp3")
dub_upperRightDrum = AudioSegment.from_file("../assets/crash.mp3")
dub_lowerOuterDrum = AudioSegment.from_file("../assets/[WOH] Snare 4.mp3")
dub_upperLeftDrum = AudioSegment.from_file("../assets/hat_6.mp3")

dub_buttonDrum = AudioSegment.from_file("../assets/Sample God- 50 Cent Kick.mp3")
dub_hello = AudioSegment.from_file("../assets/hello.mp3")


def start_drums_agent(stick):
    pygame.mixer.init(44100, -16, 2)
    print(f"Stick {stick} initializing, mixer settings: {pygame.mixer.get_init()}")


    lowerInnerDrum = pygame.mixer.Sound(dub_lowerInnerDrum.raw_data)
    upperRightDrum = pygame.mixer.Sound(dub_upperRightDrum.raw_data)
    lowerOuterDrum = pygame.mixer.Sound(dub_lowerOuterDrum.raw_data)
    upperLeftDrum = pygame.mixer.Sound(dub_upperLeftDrum.raw_data)
    
    last_angle, angle_y, angle_z = 0, 0, 0
    gyr_flag = True

    m = ahrs.filters.Madgwick(gain=0.033)

    acc, gyr, mag = stick.get_calibrated()
 
    lastTime = time.time()
    q = np.array([1, 0, 0, 0], dtype=np.float64)
    
    for _ in range(5000):
        q = m.updateMARG(q, gyr, acc, mag)

    rotation = Rotation.from_quat(np.roll(q, -1))

    _, _, angle_z = rotation.as_euler("xyz", degrees=True)
    angle_z_base = angle_z

    print(f"Stick {stick}: Calibration done")
    while True:

        acc, gyr, mag = stick.get_calibrated()
        time_temp = time.time()
        deltaTime = time_temp - lastTime

        lastTime = time_temp
        m.Dt = deltaTime  
        q = m.updateMARG(q, gyr, acc, mag)
        rotation = Rotation.from_quat(np.roll(q, -1))
        _, angle_y, angle_z = rotation.as_euler("xyz", degrees=True)

        angle_tresh = 600
        angle_diff = (angle_y - last_angle) / deltaTime
        shifted = pseudomodulo(angle_z, angle_z_base)


        if gyr_flag and angle_diff > angle_tresh and angle_y > -90 and angle_y < 30:

            gyr_flag = False
            if angle_y < -50:
                if shifted > 0 and shifted < 90:
                    print(f"Stick {stick}: Upper left drum")
                    play_sound(upperLeftDrum)
                if shifted < 0 and shifted > -90:
                    print(f"Stick {stick}: Upper right drum")
                    play_sound(upperRightDrum)
            else:
                if shifted > -135 and shifted < -45:
                    print(f"Stick {stick}: Lower outer right drum")
                    play_sound(lowerOuterDrum)
                elif shifted >= -45 and shifted < 0:
                    print(f"Stick {stick}: Lower inner right drum")
                    play_sound(lowerInnerDrum)
                elif shifted >= 0 and shifted < 45:
                    print(f"Stick {stick}: Lower inner left drum")
                    play_sound(lowerInnerDrum)
                elif shifted >= 45 and shifted < 135:
                    print(f"Stick {stick}: Lower outer left drum")
                    play_sound(lowerOuterDrum)

        if not gyr_flag and angle_diff <= angle_tresh:
            gyr_flag = True

        last_angle = angle_y


def play_sound(s):
    s.play()

def pseudomodulo(val, base):
    temp = val - base
    if temp < -180:
        return temp + 360
    if temp > 180:
        return temp - 360
    return temp

def button(BUTTON_GPIO = 17):
    pygame.mixer.init(44100, -16, 2)
    buttonDrum = pygame.mixer.Sound(dub_buttonDrum.raw_data)
    last_push = time.time()
    time_tresh = 0.25

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    while True:
        GPIO.wait_for_edge(BUTTON_GPIO, GPIO.FALLING)
        time_pushed = time.time()
        dt = time_pushed - last_push
        if(dt > time_tresh):
            last_push = time_pushed
            print("Button pressed!")
            play_sound(buttonDrum)
            
        GPIO.wait_for_edge(BUTTON_GPIO, GPIO.RISING)


if __name__ == "__main__":
    pygame.mixer.init(44100, -16, 2)
    hello = pygame.mixer.Sound(dub_hello.raw_data)
    play_sound(hello)

    try:
        # Button
        thread = threading.Thread(target=button, daemon=True)
        thread.start()

        # Stick 1
        i2c1 = I2C(3)
        stick1 = Sensor(i2c1, 1)
        stick1.set_range_8g_2000dps()
        stick1.set_rate_208()
        thread = threading.Thread(target=(lambda : start_drums_agent(stick1)), daemon=True)
        thread.start()


        # Stick 2
        i2c = busio.I2C(board.SCL, board.SDA)
        stick = Sensor(i2c, 2)
        stick.set_range_8g_2000dps()
        stick.set_rate_208()
        start_drums_agent(stick)

    except KeyboardInterrupt:
        print("Serwer zakończony.")
