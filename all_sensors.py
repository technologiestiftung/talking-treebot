#!/usr/bin/env python3

import colorsys
import sys
import time

import st7735

try:
    # Transitional fix for breaking change in LTR559
    from ltr559 import LTR559
    ltr559 = LTR559()
except ImportError:
    import ltr559


import logging

from bme280 import BME280
from fonts.ttf import RobotoMedium as UserFont
from PIL import Image, ImageDraw, ImageFont
from pms5003 import PMS5003
from pms5003 import ReadTimeoutError as pmsReadTimeoutError

from enviroplus import gas

logging.basicConfig(
    format="%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S")

logging.info("""all_sensors.py - Displays readings from all of Enviro plus' sensors""")

# BME280 temperature/pressure/humidity sensor
bme280 = BME280()

# PMS5003 particulate sensor
pms5003 = PMS5003()

# Create ST7735 LCD display class
st7735 = st7735.ST7735(
    port=0,
    cs=1,
    dc="GPIO9",
    backlight="GPIO12",
    rotation=270,
    spi_speed_hz=10000000
)

# Initialize display
st7735.begin()
WIDTH = st7735.width
HEIGHT = st7735.height

# Set up canvas and font
img = Image.new("RGB", (WIDTH, HEIGHT), color=(0, 0, 0))
draw = ImageDraw.Draw(img)
font_size = 14
font = ImageFont.truetype(UserFont, font_size)

# initial sensor values
temperature = pressure = humidity = light = oxidised = reduced = nh3 = pm1 = pm10 = pm25 = 0.0

# Displays data and text on the 0.96" LCD
def display_text(sensor_data):
    y_pos = 2
    x_pos = 2
    draw.rectangle((0, 0, WIDTH, HEIGHT), (255, 255, 255))  # Reset background to white
    for name, value, unit in sensor_data:   
        if name not in ["Reduced", "Oxidised"]:  # Skip displaying Reduced and Oxidised
            sensor_message = f"{name}: {value} {unit}"
            draw.text((x_pos, y_pos), sensor_message, font=font, fill=(0, 0, 0))
            y_pos += font_size  # Move to the next line for the next sensor
    st7735.display(img)

# Get the temperature of the CPU for compensation
def get_cpu_temperature():
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        temp = f.read()
        temp = int(temp) / 1000.0
    return temp

# Tuning factor for compensation. Decrease this number to adjust the
# temperature down, and increase to adjust up
factor = 2.25

cpu_temps = [get_cpu_temperature()] * 5

# Create a values dict to store the data


def get_sensor_readings():
    time.sleep(1)
    sensor_data = []
    #temperature
    cpu_temps = []
    cpu_temp = get_cpu_temperature()
    # Smooth out with some averaging to decrease jitter
    cpu_temps = cpu_temps[1:] + [cpu_temp]
    avg_cpu_temp = sum(cpu_temps) / float(len(cpu_temps))
    raw_temp = bme280.get_temperature()
    temperature = raw_temp - ((avg_cpu_temp - raw_temp) / factor)
    sensor_data.append(("Temperature", round(temperature, 1), "°C"))

    #pressure
    pressure = bme280.get_pressure()
    sensor_data.append(("Pressure", round(pressure, 1), "hPa"))

    #humidity
    reading = bme280.get_humidity()
    humidity = reading
    sensor_data.append(("Humidity", round(humidity, 1), "%"))

    #light
    light = ltr559.get_lux()
    sensor_data.append(("Light", round(light, 1), "Lux"))

    #oxidised
    reading = gas.read_all()
    oxidised = reading.oxidising / 1000
    sensor_data.append(("Oxidised", round(oxidised, 1), "kOhm"))

    #reduced
    reading = gas.read_all()
    reduced = reading.reducing / 1000
    sensor_data.append(("Reduced", round(reduced, 1), "kOhm"))

    #nh3
    reading = gas.read_all()
    nh3 = reading.nh3 / 1000
    sensor_data.append(("NH3", round(nh3, 1), "kOhm"))

    #pm1
   # try:
   #     reading = pms5003.read()
   # except pmsReadTimeoutError:
   #     logging.warning("Failed to read PMS5003")
   #     pm1 = '-'
   # else:
   #     reading = float(reading.pm_ug_per_m3(1.0))
   #     pm1 = reading
   # sensor_data.append(("PM1", pm1, "ug/m3"))

    #pm10
    # try:
    #    reading = pms5003.read()
    #except pmsReadTimeoutError:
    #    logging.warning("Failed to read PMS5003")
    #    pm10 = '-'
    #else:
    #    reading = float(reading.pm_ug_per_m3(10))
    #    pm10 = reading
    #sensor_data.append(("PM10", pm10, "ug/m3"))

    #pm25
    #try:
    #    reading = pms5003.read()
    #except pmsReadTimeoutError:
    #    logging.warning("Failed to read PMS5003")
    #    pm25 = '-'
    #else:
    #    reading = float(reading.pm_ug_per_m3(2.5))
    #    pm25 = reading
    #    sensor_data.append(("PM25", pm25, "ug/m3"))

    return sensor_data

if __name__ == "__main__":
    try:
        while True:
            data = get_sensor_readings()
            display_text(data)
            print("sensor_data:", data)
    except KeyboardInterrupt:
        pass
    finally:
        st7735.set_backlight(0)
        st7735.display(Image.new("RGB", (WIDTH, HEIGHT), "BLACK"))
