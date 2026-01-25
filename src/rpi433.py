from PIL import Image, ImageDraw, ImageFont
import time
import RPi.GPIO as GPIO
from rpi_rf import RFDevice

# ----- Налаштування GPIO -----
RX_GPIO = 17   # GPIO для прийому сигналів
TX_GPIO = 12   # GPIO для передавання
LOG_FILE = "rf_log.txt"

# ----- Ініціалізація RF -----
rf_rx = RFDevice(RX_GPIO)
rf_rx.enable_rx()

rf_tx = RFDevice(TX_GPIO)
rf_tx.enable_tx()

# ----- Логування сигналів -----
def log_signal(code, pulselength, protocol):
    with open(LOG_FILE, "a") as f:
        f.write(f"{code} {pulselength} {protocol}\n")

def load_signals():
    signals = []
    try:
        with open(LOG_FILE, "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 3:
                    signals.append([int(parts[0]), int(parts[1]), int(parts[2])])
    except FileNotFoundError:
        pass
    return signals

# ----- Меню Receive / Transmit -----
def rpi433_menu(disp, original_img, BUTTON_UP, BUTTON_DOWN, BUTTON_SELECT):
    img = original_img.copy()
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    cursor = 0
    options = ["Receive", "Transmit"]

    while True:
        # --- Намалювати меню ---
        img = original_img.copy()
        draw = ImageDraw.Draw(img)
        y = 35 
        for i, op in enumerate(options):
            prefix = ">" if i == cursor else " "
            draw.text((25, y), f"{prefix} {op}", font=font, fill="white")
            y += 20
        disp.display(img)

        # --- Кнопки ---
        if GPIO.input(BUTTON_UP) == GPIO.LOW:
            cursor = (cursor - 1) % len(options)
            time.sleep(0.15)
        if GPIO.input(BUTTON_DOWN) == GPIO.LOW:
            cursor = (cursor + 1) % len(options)
            time.sleep(0.15)

        # --- Select ---
        if GPIO.input(BUTTON_SELECT) == GPIO.LOW:
            if options[cursor] == "Receive":
                # Receive Loop
                while True:
                    timestamp = rf_rx.rx_code_timestamp
                    while rf_rx.rx_code_timestamp == timestamp:
                        # Вихід по кнопці SELECT
                        if GPIO.input(BUTTON_SELECT) == GPIO.LOW:
                            return
                        time.sleep(0.01)

                    code = rf_rx.rx_code
                    pulselength = rf_rx.rx_pulselength
                    protocol = rf_rx.rx_proto

                    # Логування
                    log_signal(code, pulselength, protocol)

                    # Відобразити останні сигнали
                    signals = load_signals()
                    max_lines = 6
                    start_idx = max(0, len(signals) - max_lines)

                    img = original_img.copy()
                    draw = ImageDraw.Draw(img)
                    y = 10
                    for sig in signals[start_idx:]:
                        draw.text((5, y), f"{sig[0]} {sig[1]} {sig[2]}", font=font, fill="white")
                        y += 15
                    disp.display(img)

            elif options[cursor] == "Transmit":
                signals = load_signals()
                if not signals:
                    img = original_img.copy()
                    draw = ImageDraw.Draw(img)
                    draw.text((5, 20), "No signals to send!", font=font, fill="white")
                    disp.display(img)
                    time.sleep(2)
                else:
                    tx_cursor = 0
                    while True:
                        img = original_img.copy()
                        draw = ImageDraw.Draw(img)
                        y = 10
                        # Вивід всіх сигналів
                        max_lines = 6
                        start_idx = max(0, tx_cursor - max_lines + 1)
                        for i, sig in enumerate(signals[start_idx:start_idx + max_lines]):
                            actual_idx = start_idx + i
                            prefix = ">" if actual_idx == tx_cursor else " "
                            draw.text((5, y), f"{prefix}{sig[0]} {sig[1]} {sig[2]}", font=font, fill="white")
                            y += 15
                        disp.display(img)

                        # Навігація по списку
                        if GPIO.input(BUTTON_UP) == GPIO.LOW:
                            tx_cursor = (tx_cursor - 1) % len(signals)
                            time.sleep(0.15)
                        if GPIO.input(BUTTON_DOWN) == GPIO.LOW:
                            tx_cursor = (tx_cursor + 1) % len(signals)
                            time.sleep(0.15)
                        if GPIO.input(BUTTON_SELECT) == GPIO.LOW:
                            code, pulselength, protocol = signals[tx_cursor]
                            img = original_img.copy()
                            draw = ImageDraw.Draw(img)
                            draw.text((5, 20), f"Transmitting {code}", font=font, fill="white")
                            disp.display(img)
                            rf_tx.tx_code(code, protocol, pulselength)
                            time.sleep(1)
                            break

            time.sleep(0.1)
            break
