import smbus2
from bme280 import BME280
import time

# BME280 Sensor initialisieren
bus = smbus2.SMBus(1)
bme280 = BME280(i2c_dev=bus)

# Sensormesswerte erfassen und formatieren
def get_sensor_readings():
    try:
        # Read the sensor data
        temperature = bme280.get_temperature()
        humidity = bme280.get_humidity()
        pressure = bme280.get_pressure()

        # Return the sensor readings
        sensor_readings = [
            ("Temperatur (Celsius)", f"{int(temperature)}", "°C"),
            ("Luftfeuchtigkeit", f"{humidity:.1f}", "%"),
            ("Luftdruck", f"{pressure:.1f}", "hPa"),
        ]
        return sensor_readings
    except Exception as e:
        print(f"Error reading sensor data: {e}")
        return [
            ("Temperatur (Celsius)", "N/A", "°C"),
            ("Luftfeuchtigkeit", "N/A", "%"),
            ("Luftdruck", "N/A", "hPa"),
        ]

# Example usage
if __name__ == "__main__":
    while True:
        readings = get_sensor_readings()
        for reading in readings:
            print(f"{reading[0]}: {reading[1]} {reading[2]}")
