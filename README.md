# Talking Treebot

A mobile chatbot essentially used to make citizens interact with trees and foster their empathy for trees as organisms in our daily life.

We use `Python 3.11.2` with `pip` as package manager and `virtualenv` to create isolate virtual environments.

<p float="left">
        <img width=58%; alt="Treebot Tech" src="https://github.com/user-attachments/assets/62e1056b-88a0-40ff-83bd-b3f14606476d">
        <img width=33%; alt="Treebot Talk" src="https://github.com/user-attachments/assets/035d8ff8-405a-4204-88f1-87f31c5d279f">
</p>


**⚠️ Update: We noticed that the multi-threading approach and playing back sounds on a Raspberry Pi Zero is a too intensive process, meaning that all the tasks will be performed in a very slow manner. Thus, we highly recommend, to switch on another Raspberry Pi with more RAM (e.g. Raspi v4) and get BME280 sensor readings only once at the beginning of each conversation.**

## Hardware

- Raspberry Pi Zero v1.1 (deprecated) / instead use: Raspi v4 with 8GB
- 16GB micro SD card
- micro USB -> USB adapter
- USB splitter (to have two USB slots)
- USB speaker box
- Bluetooth Lavalier microphone with USB receiver
- Enviro+ hat including the PM sensor to measure particles in the air

## Setup Raspberry Pi v4

The chatbot uses Rasbian OS (Bookworm) to save some RAM and energy. Please note that we use the latest Bookworm release in which Python v3.11.2 is pre-installed.

1. Install [Rasbian Bookworm OS](https://www.raspberrypi.com/software/operating-systems/) by using the [Raspberry Pi Imager](https://projects.raspberrypi.org/en/projects/raspberry-pi-setting-up/2) to flash your SD card.

In case you use an older OS of Raspbian you could go with Python v9 (pre-installed).

## Setup Environment
Enable I2C on Raspberry to make BME280 and button work:
`sudo raspi-config nonint do_i2c 0`

System-level dependencies that cannot be installed with pip. Rather use `apt`as system-wide package manager to install the following:
`sudo apt update`
`sudo apt install libasound2-dev`
`sudo apt install portaudio19-dev`
`sudo apt install mpg123`
`sudo apt install git`

1. Install the same Python version you are using on your Raspberry Pi (ideally v3.11.2 any other version like v9 also works)
2. Pull this GitHub Repository by running `git clone https://github.com/technologiestiftung/talking-treebot`
3. Navigate into the folder `cd talkding-treebot`
2. Install `venv` and create a virtual environment: `python3.11 -m venv treebot-env` 
3. Activate venv: `source treebot-env/bin/activate`
4. Install missing environment packages with `pip install [the-missing-package]` or simply run `pip install -r requirements.txt`

## Configure Microphone and Speaker
Install the ALSA service utilities and follow steps below.

1. `sudo alsactl init`
2. list available playback devices (speaker) on RasPi `aplay -l`
3. list available capture devices (microphone) on RasPi `arecord -l`
4. Set both devices as default and edit `sudo vim /etc/asound.conf`

If your speaker is on card 1, device 0, and your microphone is on card 0, device 0, your /etc/asound.conf might look like this:

```
# Default speaker
pcm.!default {
    type hw
    card 2
    device 0
}

ctl.!default {
    type hw
    card 2
}

# Default microphone
pcm.!default {
    type hw
    card 3
    device 0
}

ctl.!default {
    type hw
    card 0
}

```

5. Restart the ALS service to apply the changes: `sudo systemctl restart alsa`

In order to increase the volume of your speaker e.g. to 80% you can run `amixer set Master 80%`


You should test your speaker and microphone configurations:
Record 5sec: `arecord -D hw:0,0 -f cd -t wav -d 5 -r 44100 -c 1 test-record.wav`
Play your recording: `aplay test-recording.wav`

### Starting the Script
Note: running the script with sudo can cause other issues, such as conflicts with PulseAudio or the virtual environment. Try to avoid running `main.py` or `button.py` in sudo mode.

Instead give your user GPIO access to make `button.py` work:
-Add your user (treebot) to the gpio group: `sudo usermod -aG gpio treebot`
- then reboot: `sudo reboot`
- check access (gpio should be listed): `groups`

Run: `python main.py` in order to start the conversation. I f you soldered a button to the Raspi, you can also run `python button.py` to run the main script whislt having more control over the interaction.

## How to interact with my little Pi?

An older version of this project was using a headless OS (without screen, keyboard, mouse) which is why we needed to connect to the Raspberry via SSH.

1. run `ping raspberrypi`
2. copy the IP address and run `ssh talkingtreebot@[copied-IP-adress]` (e.g. 192.168.4.123)
3. connect with username and password

If you can't find the raspberry in your network, check if you laptop and the raspberry are connected to the same Wifi. To see all devices that are connected to your network run `arp -a`

Furthermore, we use magic wormhole to transfer files from the raspberry to our computer.

- Install on Raspberry Pi running `sudo apt install magic-wormhole`
- Install on MacOS running `brew install magic-wormhole`

In case you are using a Raspberry Pi with arm64 architecture (which is the case Raspi v4) you can improve your developer experience connect your Visual Studio Code IDE.
