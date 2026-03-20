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
    subprocess.Popen(command)    
    img = original_img2.copy()
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    while True:

        # якщо користувач натиснув кнопку "назад"
        if GPIO.input(Joystick_Press) == GPIO.LOW:
            if command.poll() is None:
                command.terminate()
            break

        # якщо процес сам завершився
        if command.poll() is not None:
            break

        time.sleep(0.05)    
    #draw.rectangle((0, 0, 160, 128), outline="black", fill="black")
    for i in range(120):
        time.sleep(1)
        #draw.rectangle((40, 30, 160, 50), outline="black", fill="black")
        img = original_img2.copy()
        draw = ImageDraw.Draw(img)
        draw.text((40, 20), f"attacking:", fill="white")
        draw.text((40, 30), f"at {i+1}", fill="white")
        
        disp.display(img)

