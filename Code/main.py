import dht
import machine
import time
from machine import ADC, Pin
import hcsr04

# Define DHT22 pin
DHT_PIN = 4  # GPIO4

# Define GPIO pin connected to the relay module to control the fan
FAN_PIN = 21  # GPIO21

# Define temperature and humidity thresholds
TEMP_THRESHOLD = 25.0  # in Celsius
HUMIDITY_THRESHOLD = 60.0  # in percentage

# Initialize DHT sensor
dht_sensor = dht.DHT22(machine.Pin(DHT_PIN))

# Initialize fan pin
fan = machine.Pin(FAN_PIN, machine.Pin.OUT)

# Define GPIO pin connected to the relay module to control the bulb
BULB_PIN = 19  # GPIO19

# Initialize bulb pin
bulb = machine.Pin(BULB_PIN, machine.Pin.OUT)

# Define LDR pin
LDR_PIN = 34  # GPIO34

class LDR:
    """This class reads a value from a light dependent resistor (LDR)"""

    def __init__(self, pin, min_value=0, max_value=100):
        """
        Initializes a new instance.
        :parameter pin: A pin that's connected to an LDR.
        :parameter min_value: A min value that can be returned by value() method.
        :parameter max_value: A max value that can be returned by value() method.
        """

        if min_value >= max_value:
            raise Exception('Min value is greater or equal to max value')

        # initialize ADC (analog to digital conversion)
        self.adc = ADC(Pin(pin))

        # set 11dB input attenuation (voltage range roughly 0.0v - 3.6v)
        self.adc.atten(ADC.ATTN_11DB)

        self.min_value = min_value
        self.max_value = max_value

    def read(self):
        """
        Read a raw value from the LDR.
        :return: A value from 0 to 4095.
        """
        return self.adc.read()

    def value(self):
        """
        Read a value from the LDR in the specified range.
        :return: A value from the specified [min, max] range.
        """
        return (self.max_value - self.min_value) * self.read() / 4095

# Initialize an LDR
ldr = LDR(LDR_PIN)

# Initialize ultrasonic sensor
ultrasonic = hcsr04.HCSR04(trigger_pin=13, echo_pin=12, echo_timeout_us=1000000)
PRESENCE_THRESHOLD = 100  # Distance in cm to detect presence

# Main loop
while True:
    # Measure distance to detect presence
    distance = ultrasonic.distance_cm()
    print(f'distance is {distance} cm')

    if distance < PRESENCE_THRESHOLD:
        # Person detected
        print('Person detected')

        # Read data from DHT22 sensor
        dht_sensor.measure()
        temperature = dht_sensor.temperature()
        humidity = dht_sensor.humidity()

        # Check if data is valid
        if temperature is not None and humidity is not None:
            print('Temperature: {0:0.1f}°C, Humidity: {1:0.1f}%'.format(temperature, humidity))

            # Check if temperature and humidity exceed thresholds
            if temperature > TEMP_THRESHOLD or humidity > HUMIDITY_THRESHOLD:
                fan.off()  # Turn fan on
                print('Fan turned on')
            else:
                fan.on()  # Turn fan off
                print('Fan turned off')
        else:
            print('Failed to read data from DHT22 sensor. Retrying...')

        # Read a value from the LDR
        light_value = ldr.value()
        print('Light value: {}'.format(light_value))

        # Control the bulb based on light intensity
        if light_value > 50:
            bulb.off()  # Turn bulb on
            print('Bulb turned on')
        else:
            bulb.on()  # Turn bulb off
            print('Bulb turned off')

    else:
        # No person detected, turn off all devices
        print('No person detected, turning off all devices')
        fan.on()
        bulb.on()

    # Wait before next reading
    time.sleep(5)  # Adjust interval as needed