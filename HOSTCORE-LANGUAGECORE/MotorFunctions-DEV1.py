
from __future__ import division
import argparse
import time
import RPi.GPIO as GPIO
import Adafruit_PCA9685
from random import randint
import os

# ************************************************************** POWER-DOWN VIA GPIO SWITCH DETECTION ************************************
GPIO.setmode(GPIO.BOARD)          # choose BCM or BOARD
GPIO.setup(40, GPIO.IN, pull_up_down = GPIO.PUD_UP)  

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

pwm.set_pwm(0, 0, 280)     # L U/D Sync'd   Max Up, Max Right (host's right)
pwm.set_pwm(2, 0, 440)     # R U/D Sync'd
pwm.set_pwm(1, 0, 270)      # L L/R Sync'd
pwm.set_pwm(3, 0, 270)      # R L/R Sync'd
time.sleep(5)

pwm.set_pwm(0, 0, 440)     # L U/D Sync'd   Max Down, Max Right
pwm.set_pwm(2, 0, 280)     # R U/D Sync'd
pwm.set_pwm(1, 0, 270)      # L L/R Sync'd
pwm.set_pwm(3, 0, 270)      # R L/R Sync'd
time.sleep(5)

pwm.set_pwm(0, 0, 260)     # L U/D Sync'd   Max Up, Max Left (host's left)
pwm.set_pwm(2, 0, 480)     # R U/D Sync'd
pwm.set_pwm(1, 0, 440)      # L L/R Sync'd
pwm.set_pwm(3, 0, 440)      # R L/R Sync'd
time.sleep(5)

pwm.set_pwm(0, 0, 440)     # L U/D Sync'd   Max Down, Max Left (host's left)
pwm.set_pwm(2, 0, 280)     # R U/D Sync'd
pwm.set_pwm(1, 0, 440)      # L L/R Sync'd
pwm.set_pwm(3, 0, 440)      # R L/R Sync'd
time.sleep(5)

pwm.set_pwm(0, 0, 340)     # L U/D Sync'd   Crosseyed (Close Focus Demo)
pwm.set_pwm(2, 0, 340)     # R U/D Sync'd
pwm.set_pwm(1, 0, 270)      # L L/R Sync'd
pwm.set_pwm(3, 0, 440)      # R L/R Sync'd
time.sleep(5)

pwm.set_pwm(0, 0, 340)     # L U/D Sync'd   All Centered
pwm.set_pwm(2, 0, 340)     # R U/D Sync'd
pwm.set_pwm(1, 0, 340)      # L L/R Sync'd
pwm.set_pwm(3, 0, 340)      # R L/R Sync'd
time.sleep(5)

x = 1
while True:

    servo_randV = randint(0, 160)   # U/D  Range slightly smaller for U/D than L/R
    servo_randH = randint(0, 180)   # L/R

    vertL = 280 + servo_randV
    vertR = 440 - servo_randV
    horz = 270 + servo_randH
    horzL = horz
    horzR = horz

    if vertL > 340:              # Mostly so it only looks "close-up" (aka cross-eyed) when looking below horizon.  Just for aesthetics in testing.
        dist = randint(0, 50)
        horzL = horz - dist
        horzR = horz + dist
        if horzL < 280:
            horzL = 280
        if horzL > 480:
            horzL = 480   
    
    pwm.set_pwm(0, 0, vertL)     # L U/D Sync'd
    pwm.set_pwm(2, 0, vertR)     # R U/D Sync'd
    pwm.set_pwm(1, 0, horzL)      # L L/R Sync'd
    pwm.set_pwm(3, 0, horzR)      # R L/R Sync'd
    timer_rand = randint(1, 600)
    timer_rand = timer_rand/1000
    time.sleep(timer_rand)


    if x == 1:
        choice = servo_max
    elif x == 0:
        choice = servo_min

    x += 1
    if x == 2:
        x = 0
            
    servo_pos = choice              # JAW
    pwm.set_pwm(4, 0, servo_pos)
    time.sleep(.12)


# No function should ever decrement/increment below 150 or above 600

    
