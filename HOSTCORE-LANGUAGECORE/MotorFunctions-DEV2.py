
from __future__ import division
import argparse
import time
import datetime
import calendar
import RPi.GPIO as GPIO

faceSeen = 0

# Import the PCA9685 module.
import Adafruit_PCA9685
from random import randint

# Uncomment to enable debug output.
#import logging
#logging.basicConfig(level=logging.DEBUG)

# Initialise the PCA9685 using the default address (0x40).
pwm = Adafruit_PCA9685.PCA9685()

# Alternatively specify a different address and/or bus:
#pwm = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)

# Configure min and max servo pulse lengths
servo_min = 150  # Min pulse length out of 4096
servo_max = 600  # Max pulse length out of 4096

# Helper function to make setting a servo pulse width simpler.
def set_servo_pulse(channel, pulse):
    pulse_length = 1000000    # 1,000,000 us per second
    pulse_length //= 50       # 60 Hz
    print('{0}us per period'.format(pulse_length))
    pulse_length //= 4096     # 12 bits of resolution
    print('{0}us per bit'.format(pulse_length))
    pulse *= 1000
    pulse //= pulse_length
    pwm.set_pwm(channel, 0, pulse)

# Set frequency to 60hz, good for servos.
pwm.set_pwm_freq(60)

x = 1
while True:
    LU = GPIO.input(11)
    LD = GPIO.input(13)
    LL = GPIO.input(15)
    LR = GPIO.input(29)
    RU = GPIO.input(31)
    RD = GPIO.input(33)
    RL = GPIO.input(35)
    RR = GPIO.input(37)
    FDL = GPIO.input(12)
    FDR = GPIO.input(16)

    # Move servo on channel O between extremes.


    servo_rand = randint(270, 450)   # L U/D
    pwm.set_pwm(0, 0, servo_rand)
    pwm.set_pwm(2, 0, servo_rand)    # R U/D Sync'd
    timer_rand = randint(1, 400)
    timer_rand = timer_rand/1000
    time.sleep(timer_rand)
    
    servo_rand = randint(270, 450)   # L L/R
    pwm.set_pwm(1, 0, servo_rand)
    timer_rand = randint(1, 400)
    timer_rand = timer_rand/1000
    time.sleep(timer_rand)
    
    servo_rand = randint(270, 450)   # R L/R
    pwm.set_pwm(3, 0, servo_rand)
    timer_rand = randint(1, 400)
    timer_rand = timer_rand/1000
    time.sleep(timer_rand)
    #print(timer_rand)

#    servo_rand = randint(150, 600)
#    pwm.set_pwm(4, 0, servo_rand)
#    time.sleep(.1)


    if x == 1:
        choice = servo_max
    elif x == 0:
        choice = servo_min

    x += 1
    if x == 2:
        x = 0
            
    servo_pos = choice              # JAW
    pwm.set_pwm(4, 0, servo_pos)
    time.sleep(.1)



#    pwm.set_pwm(1, 0, servo_min)
#    pwm.set_pwm(2, 0, servo_min)
#    pwm.set_pwm(3, 0, 275)
#    time.sleep(.5)
#    pwm.set_pwm(0, 0, servo_max)
#    pwm.set_pwm(1, 0, servo_max)
#    pwm.set_pwm(2, 0, servo_max)
#    pwm.set_pwm(3, 0, 475)
#    time.sleep(.5)
#    pwm.set_pwm(0, 0, 375)  # Halfway
#    pwm.set_pwm(1, 0, 375)  # Halfway
#    pwm.set_pwm(2, 0, 375)  # Halfway
    #pwm.set_pwm(3, 0, 375)  # Halfway
#    time.sleep(.5)

# One servo for up/down
# Two servos for left/right (one for each eye to allow for "cross-eyed" close focus.)
# Servos will always increment/decrement until l/r and u/d are off, while facedetect=1.
# If facedetect is 0 on one eye, it should sync with other eye if IT is 1.
# If both facedetects are 0, return both to 375.
# No function should ever decrement/increment below 150 or above 600

    
