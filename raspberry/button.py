from pydub import AudioSegment, playback
import threading

snare = AudioSegment.from_file("../assets/snare.wav", format="wav")
hihat = AudioSegment.from_file("../assets/klask.wav", format="wav")
perc = AudioSegment.from_file("../assets/perc.wav", format="wav")
buttonDrum = AudioSegment.from_file("../assets/Sample God- 50 Cent Kick.wav", format="wav")
width, height = 800, 600

import RPi.GPIO as GPIO

import time

BUTTON_GPIO = 17


def play_sound_async(s):
    def play():
        playback.play(s)

    # Create and start the daemon thread
    thread = threading.Thread(target=play)
    thread.start()

last_push = time.time()
time_tresh = 0.2

if __name__ == '__main__':
    # TODP
        # play_sound_async(pornhub) 
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    while True:
        GPIO.wait_for_edge(BUTTON_GPIO, GPIO.FALLING)
        time_pushed = time.time()
        temp = time_pushed - last_push
        print(temp)
        if( temp > time_tresh):
            last_push = time_pushed
            # print("Button pressed!")
            play_sound_async(buttonDrum)
            
        GPIO.wait_for_edge(BUTTON_GPIO, GPIO.RISING)
