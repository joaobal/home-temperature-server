import Adafruit_DHT
import time

# Choose your sensor:
SENSOR = Adafruit_DHT.DHT11   # use Adafruit_DHT.DHT11 if you have a DHT11
PIN = 4                      # GPIO pin in BCM numbering (e.g., BCM4 = physical pin 7)

while True:
    humidity, temperature = Adafruit_DHT.read_retry(SENSOR, PIN)

    if humidity is not None and temperature is not None:
        print(f"Temp: {temperature:.1f} °C   Humidity: {humidity:.1f} %")
    else:
        print("⚠️ Failed to read from sensor. Check wiring/model.")

    time.sleep(1)

