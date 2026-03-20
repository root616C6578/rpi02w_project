import subprocess
import time
import os
from PIL import ImageDraw, ImageFont

def fmtrx(original_img, disp, GPIO, Joystick_UP, Joystick_Down, Joystick_Press, BUTTON_UP, BUTTON_DOWN, BUTTON_SELECT,  fm_opt, draw, font):
    img = original_img.copy() 
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    #draw.rectangle((0, 0, 160, 128), outline="black", fill="black")  # Очистити екран

    disp.display(img)
    cursor = 0
    f = 87.5
    fm = 0.0
    directory = "/home/alex/wavfiles" 
    command = ["ls", directory]
    result = subprocess.run(command, capture_output=True, text=True)
    files = result.stdout.splitlines()
    wavfiles = files
    if not wavfiles:
        print("No WAV files found")
        time.sleep(0.5)

    selected_file = ''

    while True:
        img = original_img.copy()
        draw = ImageDraw.Draw(img)
        #draw.rectangle((0, 0, 160, 128), outline="black", fill="black")
        y = 35 
        for i, op in enumerate(fm_opt):
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
        button_state_BACK = GPIO.input(Joystick_Press)

        # Обробка кнопок
        if button_state_UP == GPIO.LOW:
            cursor = (cursor - 1) % len(fm_opt)
            time.sleep(0.1)

        if button_state_DOWN == GPIO.LOW:
            cursor = (cursor + 1) % len(fm_opt)
            time.sleep(0.1)

        # Вихід з головного меню
        if button_state_BACK == GPIO.LOW:
            print("Exit main menu")
            time.sleep(0.2)
            break

        # Select
        if button_state_SELECT == GPIO.LOW:
            if fm_opt[cursor] == "select freq":
                while True:
                    img = original_img.copy()
                    draw = ImageDraw.Draw(img)
                    # draw.rectangle((0, 0, 160, 128), outline="black", fill="black")
                    draw.text((25, 50), f"freq: {f:.1f} MHz", font=font, fill="white")
                    disp.display(img)

                    button_state_JUP = GPIO.input(Joystick_UP)
                    button_state_JDOWN = GPIO.input(Joystick_Down)
                    button_state_SELECT = GPIO.input(BUTTON_SELECT)
                    button_state_BACK = GPIO.input(Joystick_Press)

                    if button_state_JUP == GPIO.LOW and f < 107.9:
                        f += 0.1
                        f = round(f, 1)
                        draw.text((25, 50), f"freq: {f:.1f} MHz", font=font, fill="white")
                        time.sleep(0.05)
                
                    if button_state_JDOWN == GPIO.LOW and f > 87.5:
                        f -= 0.1
                        f = round(f, 1)
                        draw.text((25, 50), f"freq: {f:.1f} MHz", font=font, fill="white")
                        time.sleep(0.05)

                    # Вихід з меню вибору частоти
                    if button_state_BACK == GPIO.LOW:
                        print("Cancel freq selection")
                        fm = round(f, 1)
                        print(fm)
                        time.sleep(0.1)                        
                        time.sleep(0.2)
                        break

            time.sleep(0.1)

            if fm_opt[cursor] == "select wav":
                cursor_wav = 0
                visible_items = 5  
                scroll_offset = 0

                while True:
                    img = original_img.copy()
                    draw = ImageDraw.Draw(img)
                    #draw.rectangle((0, 0, 160, 128), outline="black", fill="black")
                    y = 20

                    if cursor_wav < scroll_offset:
                        scroll_offset = cursor_wav
                    elif cursor_wav >= scroll_offset + visible_items:
                        scroll_offset = cursor_wav - visible_items + 1

                    visible_wavfiles = wavfiles[scroll_offset:scroll_offset + visible_items]

                    for i, op in enumerate(visible_wavfiles):
                        real_index = scroll_offset + i
                        if real_index == cursor_wav:
                            draw.text((25, y), f"> {op}", font=font, fill="white")
                        else:
                            draw.text((25, y), f"  {op}", font=font, fill="white")
                        y += 20

                    disp.display(img)    
                    
                    button_state_UP = GPIO.input(BUTTON_UP)
                    button_state_DOWN = GPIO.input(BUTTON_DOWN)
                    button_state_SELECT = GPIO.input(BUTTON_SELECT)
                    button_state_BACK = GPIO.input(Joystick_Press)

                    # Обробка кнопок
                    if button_state_UP == GPIO.LOW:
                        cursor_wav = (cursor_wav - 1) % len(wavfiles)
                        time.sleep(0.01)

                    if button_state_DOWN == GPIO.LOW:
                        cursor_wav = (cursor_wav + 1) % len(wavfiles)
                        time.sleep(0.01)

                    # Вихід з меню вибору файлу
                    if button_state_BACK == GPIO.LOW:
                        print("Cancel file selection")
                        time.sleep(0.2)
                        break

                    if button_state_SELECT == GPIO.LOW:
                        selected_file = wavfiles[cursor_wav]
                        print(f"Selected WAV file: {selected_file}")
                        time.sleep(0.1)
                        break

            time.sleep(0.1)

            if fm_opt[cursor] == "start attack":
                img = original_img.copy()
                draw = ImageDraw.Draw(img)
                #draw.rectangle((0, 0, 160, 128), outline="black", fill="black")
                draw.text((25,20), f"attack {fm}MHz", fill="white")
                draw.text((25,30), f"file: {selected_file}", fill='white')
                disp.display(img)
                print(fm)
                print(selected_file)
                command = ['sudo', '/home/alex/fm_transmitter/fm_transmitter', '-f', str(fm), "/home/alex/wavfiles/"+selected_file]
                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                while True:
                    button_state_BACK = GPIO.input(Joystick_Press)

                    if button_state_BACK == GPIO.LOW:
                        print("Stopping process...")
                        if process.poll() is None:
                            process.kill()

                        time.sleep(0.2)
                        break

                    if process.poll() is not None:
                        print("Process finished")
                        break

                    time.sleep(0.05)

                stderr = process.stderr.read()
                if stderr:
                    print("Помилки:", stderr)

                cursor = 0


    time.sleep(0.1)