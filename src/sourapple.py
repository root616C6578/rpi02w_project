from PIL import Image, ImageDraw, ImageFont
from st7735 import ST7735
import time
import RPi.GPIO as GPIO
import subprocess
import signal
import os
import bluetooth

def sourapple_attack(disp, original_img2, Joystick_Press):
    command = ['sudo', 'python', 'Sour-Apple/sourapple.py']  # /home/alex/Sour-Apple
    process = subprocess.Popen(command)   
    font = ImageFont.load_default()
    start_time = time.time()

    while True:
        img = original_img2.copy()
        draw = ImageDraw.Draw(img)
        elapsed = int(time.time() - start_time)

        draw.text((40, 20), "running:", font=font, fill="white")
        draw.text((40, 30), f"{elapsed}s", font=font, fill="white")
        draw.text((10, 110), "J = stop", font=font, fill="white")
        disp.display(img)

        if GPIO.input(Joystick_Press) == GPIO.LOW:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
            break

        if process.poll() is not None:
            break

        time.sleep(0.05)
