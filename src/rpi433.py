from PIL import Image, ImageDraw, ImageFont
import time
import RPi.GPIO as GPIO
import subprocess
import signal
import os
import bluetooth
from rpi_rf import RFDevice

def rpi433_menu(disp, original_img, BUTTON_UP, BUTTON_DOWN, BUTTON_SELECT):
    class RFReceiver:
        @staticmethod
        def receive(pin):
            rfdevice = RFDevice(pin)
            rfdevice.enable_rx()
            timestamp = None
            rx_code_list = []
            protocol_list = []
            pulse_length_list = []
            try:
                while True:
                    if rfdevice.rx_code_timestamp != timestamp:
                        timestamp = rfdevice.rx_code_timestamp
                        code = rfdevice.rx_code
                        protocol = rfdevice.rx_proto
                        pulse_length = rfdevice.rx_pulselength
                        rx_code_list = [int(x) for x in str(code)]
                        protocol_list = [int(x) for x in str(protocol)]
                        pulse_length_list = [int(x) for x in str(pulse_length)]
                        time.sleep(0.01) 
            except KeyboardInterrupt:     
                rfdevice.cleanup()
                return rx_code_list, protocol_list, pulse_length_list

    class RFTransmitter:
        @staticmethod
        def transmit(pin, code, protocol, pulselength, repeat=10):
            rfdevice = RFDevice(pin)
            rfdevice.enable_tx()
            rfdevice.tx_repeat = repeat
            rfdevice.tx_code(code, protocol, pulselength)
            rfdevice.cleanup()
    img = original_img.copy()
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    cursor = 0
    options = ["Receive", "Transmit"]
    
    while True:
        img = original_img.copy()
        draw = ImageDraw.Draw(img)
        y = 35 
        for i, op in enumerate(options):
            if i == cursor:
                draw.text((25, y), f"> {op}", font=font, fill="white")  # Вибраний елемент
            else:
                draw.text((25, y), f"  {op}", font=font, fill="white") 
            y += 20
        disp.display(img)  # Оновлення екран  

        # Читання стану кнопок
        button_state_UP = GPIO.input(BUTTON_UP)
        button_state_DOWN = GPIO.input(BUTTON_DOWN)
        button_state_SELECT = GPIO.input(BUTTON_SELECT)  

        # Обробка кнопок
        if button_state_UP == GPIO.LOW:
            cursor = (cursor - 1) % len(options)
            time.sleep(0.1)  
        if button_state_DOWN == GPIO.LOW:
            cursor = (cursor + 1) % len(options)
            time.sleep(0.1) 

        #Select
        if button_state_SELECT == GPIO.LOW:
            if options[cursor] == "Receive":
                img = original_img.copy()
                draw = ImageDraw.Draw(img)
                draw.text((5, 20), "Receiving...", font=font, fill="white")
                disp.display(img)
                code, protocol, pulse_length = RFReceiver.receive(pin=17)
                img = original_img.copy()
                draw = ImageDraw.Draw(img)
                draw.text((5, 20), f"Code: {''.join(map(str, code))}", font=font, fill="white")
                draw.text((5, 40), f"Protocol: {''.join(map(str, protocol))}", font=font, fill="white")
                draw.text((5, 60), f"PulseLen: {''.join(map(str, pulse_length))}", font=font, fill="white")
                disp.display(img)
                time.sleep(5)
            elif options[cursor] == "Transmit":
                code = 123456
                protocol = 1
                pulse_length = 350
                img = original_img.copy()
                draw = ImageDraw.Draw(img)
                draw.text((5, 20), "Transmitting...", font=font, fill="white")
                disp.display(img)
                RFTransmitter.transmit(pin=12, code=code, protocol=protocol, pulselength=pulse_length)
                img = original_img.copy()
                draw = ImageDraw.Draw(img)
                draw.text((5, 20), "Transmission complete", font=font, fill="white")
                disp.display(img)
                time.sleep(5)
            time.sleep(0.1)
            break
            