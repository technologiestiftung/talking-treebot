# Talking Treebot

A mobile chatbot essentially used to make citizens interact with trees and foster their empathy for trees as organisms in our daily life.
We use `Python 3.12.4` with `pip` as package manager and `virtualenv` to create isolate virtual environments

## Hardware

- Raspberry Pi Zero v1.1
- 16GB micro SD card
- micro USB -> USB adapter
- USB splitter
- Enviro+ hat including the PM sensor
- Bluetooth Lavalier microphone with USB receiver
- USB speaker box

### Configure Microphone and Speaker

Install the ALSA service utilities and follow steps below.

1. `sudo alsactl init`
2. list available playback devices (speaker) on RasPi `aplay -l`
3. list availabele capture devices (microphone) on RasPI `arecord -l`

4. Set both devices as default:
   `sudo vim /etc/asound.conf`

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

5. Restart the ALS service to apply the canges: `sudo systemctl restart alsa`

## Setup MacOS

1. Install Python v3.12
2. Create a virtual environment: `python3 -m venv treebot-env` and activate it `source treebot-env/bin/activate`
3. Install missing packages with `pip install [the-missing-package]` or simply run `pip install -r requirements.txt`

## Setup Raspberyy Pi

The chatbot uses Rasbian OS Lite to save some RAM and energy.

1. Install [Rasbian OS Lite](https://www.raspberrypi.com/software/operating-systems/) (headless) manually or use the [Raspberry Pi Imager](https://projects.raspberrypi.org/en/projects/raspberry-pi-setting-up/2) to flash your SD card
2. Create a `wpa_supplicant.conf` to connect to your Wifi (see [this tutorial](https://developernation.net/blog/headless-raspberry-pi-setup-wifi-and-ssh/))

### How to interact with my little Pi?

Since the OS is only wokring headless (without screen, keyboard) we need to connect to the Rapsberry via SSH.

1. run `ping raspberrypi.local`
2. copy the IP adress and run `ssh talkingtreebot@[copied-IP-adress]` (192.168.4.223)
3. connect with username and password

(See all devices that are connected to your network: `ifconfig | grep broadcast` + `arp -a`)

First install git to be able to pull the enviro+ repository.
`sudo apt update`
`sudo apt install git`

Follow this introduction to install enviro+: https://learn.pimoroni.com/article/getting-started-with-enviro-plus#installing-the-enviro-python-library

Activate the virtual environment with `source ~/.virtualenvs/pimoroni/bin/activate`.
Run one of the example codes and have fun.
