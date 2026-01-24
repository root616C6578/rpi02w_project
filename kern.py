from PIL import Image, ImageDraw, ImageFont
from st7735 import ST7735
import time
import RPi.GPIO as GPIO
import subprocess
import signal
import os
import bluetooth
from rpi_rf import RFDevice

from src.fm_trx import fmtrx
from src.l2ping import l2ping_attack
from src.rpi433 import rpi433_menu

# GPIO кнопок
BUTTON_UP = 21
BUTTON_DOWN = 16
BUTTON_SELECT = 20
Joystick_UP = 6
Joystick_Down = 19
Joystick_Press = 13
def button_setup():
    GPIO.setmode(GPIO.BCM)
    for btn in [BUTTON_UP, BUTTON_DOWN, BUTTON_SELECT, Joystick_UP, Joystick_Down, Joystick_Press]:
        GPIO.setup(btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)
button_setup()

# Display initialization
disp = ST7735(
    port=0,
    cs=0,
    dc=25,
    rst=27,
    backlight=24,
    width=128,
    height=160,
    rotation=90,
    invert=False
)
disp.begin()

img = Image.new("RGB", (160, 128), "black")
draw = ImageDraw.Draw(img)
font = ImageFont.load_default()
draw.rectangle((0, 0, 160, 128), outline="black", fill="black")
disp.display(img)
time.sleep(0.1)

files_image = ["imgmenu/fbcp.png", "imgmenu/hackfm.png", "imgmenu/l2ping.png", "imgmenu/rpi433.png", "imgmenu/sourapple.png"]
original_img = Image.open("imgmenu/menuimg.png").convert("RGB").resize((128, 128))
original_img2 = Image.open("imgmenu/menuimg2.png").convert("RGB").resize((128, 128))

# Import after defining dependencies to avoid circular imports
from src.sourapple import sourapple_attack

images = [Image.open(x).convert("RGB").resize((128, 128)) for x in files_image]
current_index = 0

def draw_image():
    
    disp.display(images[current_index])
draw_image()
fm_opt = ["select freq", "select wav", "start attack"] 
cursor = 0

def scan_bluetooth_devices():
    nearby_devices = bluetooth.discover_devices(duration=8, flush_cache=True)
    mac_addresses = []  
    if len(nearby_devices) == 0:
        print("Не знайдено пристроїв.")

    if len(nearby_devices) > 0:
        print(f"Знайдено {len(nearby_devices)} пристроїв:")
        for addr in nearby_devices:
            mac_addresses.append(addr)

    return mac_addresses

while True:
    if GPIO.input(BUTTON_UP) == GPIO.LOW:
        time.sleep(0.2)  
        current_index = (current_index + 1) % len(images)
        draw_image()
    if GPIO.input(BUTTON_DOWN) == GPIO.LOW:
        time.sleep(0.2)  
        current_index = (current_index - 1) % len(images) 
        draw_image()
    if GPIO.input(BUTTON_SELECT) == GPIO.LOW:
        time.sleep(0.2)
        if current_index == 0: # FBCT
            subprocess.run(["sudo", "/usr/local/bin/fbcp"])
            break
        time.sleep(0.1)


        if current_index == 1: # FM TRX
            fmtrx(original_img, disp, GPIO, Joystick_UP, Joystick_Down, Joystick_Press, BUTTON_UP, BUTTON_DOWN, BUTTON_SELECT,  fm_opt, draw, font)
            time.sleep(0.1)
            draw_image()
        if current_index == 2: # L2PING
            l2ping_attack(disp, original_img, BUTTON_UP, BUTTON_DOWN, BUTTON_SELECT)
            time.sleep(0.1)
            draw_image()
        if current_index == 3: # RPI433
            rpi433_menu(disp, original_img, BUTTON_UP, BUTTON_DOWN, BUTTON_SELECT)
            time.sleep(0.1)
            draw_image()
        if current_index == 4: # SOUR APPLE
            sourapple_attack()
            time.sleep(0.1)
            draw_image()
# U_U It will be soon......... ^_+
