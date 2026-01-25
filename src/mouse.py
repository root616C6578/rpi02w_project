from pymouse import PyMouse
import time
import RPi.GPIO as GPIO
import os

# ----- Задаємо DISPLAY явно -----
os.environ["DISPLAY"] = ":0"  # або заміни на той, що у тебе через echo $DISPLAY

# ----- GPIO налаштування -----
GPIO.setmode(GPIO.BCM)

btn_up = 5
btn_down = 26
btn_left = 19
btn_right = 6
btn_key1 = 21                  
btn_key2 = 20

GPIO.setup(btn_up, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(btn_down, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(btn_left, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(btn_right, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(btn_key1, GPIO.IN, GPIO.PUD_UP)  # left button
GPIO.setup(btn_key2, GPIO.IN, GPIO.PUD_UP)  # right button

# ----- Головна функція для імпорту -----
def run_mouse():
    m = PyMouse()
    KEY1_flag = False
    KEY2_flag = False

    try:
        while True:  
            nowxy = m.position() 

            # ----- Кнопки натискання -----
            if (not GPIO.input(btn_key1)) and (not KEY1_flag):  # left click
                KEY1_flag = True
                print("KEY1")
                m.click(nowxy[0], nowxy[1], 1)
            if GPIO.input(btn_key1):
                KEY1_flag = False

            if (not GPIO.input(btn_key2)) and (not KEY2_flag):  # right click
                KEY2_flag = True
                print("KEY2")
                m.click(nowxy[0], nowxy[1], 2)
            if GPIO.input(btn_key2):
                KEY2_flag = False

            # ----- Рух миші -----
            if not GPIO.input(btn_up):
                m.move(nowxy[0] - 5, nowxy[1])
            if not GPIO.input(btn_down):
                m.move(nowxy[0] + 5, nowxy[1])
            if not GPIO.input(btn_left):
                m.move(nowxy[0], nowxy[1] + 5)
            if not GPIO.input(btn_right):
                m.move(nowxy[0], nowxy[1] - 5)

            time.sleep(0.02)  # опитування 20 мс

    except KeyboardInterrupt:
        print("Exiting mouse control...")
        GPIO.cleanup()

# ----- Виконання, якщо запускається окремо -----
if __name__ == "__main__":
    run_mouse()
