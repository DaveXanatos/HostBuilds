# USAGE21
# python /home/pi/Desktop/HOSTCORE/GPIOTest.py

import sys
sys.path.append('/usr/local/lib/python3.5/dist-packages/')

import time
import RPi.GPIO as GPIO

OE = 21

GPIO.setmode(GPIO.BCM)  # Using GPIO Numbers, not pins.
GPIO.setup(OE, GPIO.OUT)  # Set up GPIO 4 as output to control Servo Output Enable
GPIO.output(OE, 1) # Set GPIO 4 to 1 to freeze eyeballs initially

def cycleGPIO():
    GPIO.output(OE, 0) # Unfreeze Eyeballs
    print("GPIO 0")
    time.sleep(2)
    GPIO.output(OE, 1)
    print("GPIO 1")
    time.sleep(2)

while True:
    cycleGPIO()

GPIO.cleanup()
exit()

