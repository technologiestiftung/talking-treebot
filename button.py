import RPi.GPIO as GPIO
import subprocess
import time

# GPIO pin numbers
LED_PIN = 24
BUTTON_PIN = 23

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:  # Button is pressed
            print("Button was pressed")

            # Flash LED briefly to indicate the signal was sent
            GPIO.output(LED_PIN, GPIO.HIGH)
            subprocess.run(
                ["systemctl", "--user", "kill", "--signal=SIGUSR1", "treebot.service"]
            )
            time.sleep(0.1)
            GPIO.output(LED_PIN, GPIO.LOW)

            # Debounce the button press
            time.sleep(0.3)

except KeyboardInterrupt:
    print("Exiting...")

finally:
    GPIO.cleanup()
