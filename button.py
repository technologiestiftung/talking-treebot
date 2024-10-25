from gpiozero import LED, Button          
import subprocess

led = LED(24)  
button = Button(23) 

state = False  # Initially, LED is off
process = None  # store the subprocess running main.py

while True:
    button.wait_for_press()  # Wait for button to be pressed
    print("button was pressed")
    
    if state:
        led.off()  # Turn off if currently on
        state = False 
        if process:
                process.terminate()  # Stop main.py script
                process = None
                process = subprocess.Popen(["/bin/bash", "stop_main.sh"])
    else:
        led.on()  # Turn on if currently off
        state = True
        process = subprocess.Popen(["/bin/bash", "run_main.sh"]) 
    
    button.wait_for_release() 

