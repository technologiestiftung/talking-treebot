import RPi.GPIO as GPIO
import subprocess
import os
import time

# GPIO pin numbers
LED_PIN = 24
BUTTON_PIN = 23

# Setup GPIO
GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
GPIO.setup(LED_PIN, GPIO.OUT)  # Set LED pin as output
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Set button pin as input with pull-up resistor

state = False  # Initially, LED is off
process = None  # Store the subprocess running main.py

try:
    while True:
        # Wait for button press
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:  # Button is pressed
            print("Button was pressed")

            if state:
                # Turn off LED
                GPIO.output(LED_PIN, GPIO.LOW)
                state = False

                # Stop the main.py script
                if process:
                    process.terminate()  # Stop the running process
                    process = None
                    subprocess.run(["/bin/bash", "/home/treebot/talking-treebot/stop_main.sh"])  # Run the stop script
            else:
                # Turn on LED
                GPIO.output(LED_PIN, GPIO.HIGH)
                state = True

                # Start the main.py script
                process = subprocess.Popen(
                    ["/bin/bash", "/home/treebot/talking-treebot/run_main.sh"],
                    preexec_fn=os.setsid
                )

            # Debounce the button press
            time.sleep(0.3)

except KeyboardInterrupt:
    print("Exiting...")

finally:
    # Cleanup GPIO on exit
    GPIO.cleanup()
