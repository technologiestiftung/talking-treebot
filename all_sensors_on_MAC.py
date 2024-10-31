#!/usr/bin/env python3
import time

# example variables from the real sensors
temperature = 32
pressure = 1006.5
humidity = 35.6
light = 365
oxidised = 5.8
reduced = 288.1
nh3 = 110.4
pm1 = 17
pm25 = 21
pm10 = 26

def get_sensor_readings():
    sensor_readings = [
        ("Temperature", f"{temperature}", "Grad Celsius"),
        ("Pressure", f"{pressure}", "Hektopascal"),
        ("Humidity", f"{humidity}", "Prozent"),
        ("Light", f"{light}", "Lux"),
        ("Oxidised", f"{oxidised}", "Kiloohm"),
        ("Reduced", f"{reduced}", "Kiloohm"),
        ("NH3", f"{nh3}", "Kiloohm"),
        ("PM1", f"{pm1}", "Mikrogramm pro Kubikmeter"),
        ("PM25", f"{pm25}", "Mikrogramm pro Kubikmeter"),
        ("PM10", f"{pm10}", "Mikrogramm pro Kubikmeter")
    ]
    return sensor_readings