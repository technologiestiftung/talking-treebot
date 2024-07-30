# Talking Treebot

A mobile chatbot essentially used to make citizens interact with trees and foster their empathy for trees as organisms in our daily life.

## Hardware

- Raspberry Pi Zero v1.1
- Enviro+ hat including the PM sensor
- USB speaker
- Bluetooth microphone

## Software

Raspberry Pi Zero

1. Install Rasbian OS Lite (headless) on Rypsberry Pi
2. Handover some credentials for a WIFI connection

MacOS

1. Install Python v3.12
2. Create a virtual environment: `python3 -m venv treebot-env` and activate it `source treebot-env/bin/activate`
3. install missing packages

### Setup Raspbian

First install git to be able to pull the enviro+ repository.
`sudo apt update`
`sudo apt install git`

Follow this introduction to install enviro+: https://learn.pimoroni.com/article/getting-started-with-enviro-plus#installing-the-enviro-python-library

In order to install `pyaudio`you need to install portaudio first `brew install portaudio`.

Activate the virtual environment with `source ~/.virtualenvs/pimoroni/bin/activate`.
Run one of the example codes and have fun.

### How to interact with my little Pi?

The chatbot uses Rasbian OS Lite to save some RAM and energy. Since the OS is only wokring headless (without screen, keyboard) we need to connect to the Rapsberry via SSH.

1. run `ping raspberrypi.local`
2. copy the IP adress and run `ssh talkingtreebot@[copied-IP-adress]` (192.168.4.223)
3. connect with username and password

(See all devices that are connected to your network: `ifconfig | grep broadcast` + `arp -a`)
