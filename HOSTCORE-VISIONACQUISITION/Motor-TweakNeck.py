# USAGE python /home/pi/Desktop/HOSTCORE/MotorFunctions-Visual.py
# Revision date 2020-08-24

# import the necessary packages


#import argparse


from __future__ import division
import time
import RPi.GPIO as GPIO
import Adafruit_PCA9685
from random import randrange
import threading
from threading import Thread
from collections import deque

SSRH = 3.15 #ScreenServoRatioH
SSRV = 3.15 #ScreenServoRatioV

rotc = 450 # Neck Rotation Center (init 470, lower = lefter)
ltec = 440 # Neck Left Elevator Center?
rtec = 350 # Neck Right Elevator Center?

# Neck on pwm2:
ROT = 2   # Rotation
REV = 1   # Right Elevator
LEV = 0   # Left Elevator

# Initialise the PCA9685 using the default address (0x40).
pwm = Adafruit_PCA9685.PCA9685()  #Alternate to specify diff addr:  pwm2 = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)
pwm2 = Adafruit_PCA9685.PCA9685(address=0x42, busnum=1)

# No function should ever decrement/increment below _min or above _max
servoJR_min = 260
servoJL_min = 320
servoJR_max = 340
servoJL_max = 260

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
pwm2.set_pwm_freq(60)

def clamp(n, minn, maxn):
    n = max(min(maxn, n), minn)
    return n

def doRandom(vlc, vrc, hlc, hrc):
    vOffset = randrange(60)-30
    hOffset = randrange(60)-30
    stepTime = (randrange(2500)/1000)+.1
    print("Random: ",vOffset,hOffset,stepTime)
    doEyeMove(vOffset, hOffset, stepTime, vlc, vrc, hlc, hrc)

def doJaw(jdelay):
    pwm.set_pwm(JL, 0, servoJL_max) # Jaw Open
    pwm.set_pwm(JR, 0, servoJR_max) # Jaw Open
    time.sleep(jdelay)
    pwm.set_pwm(JL, 0, servoJL_min) # Jaw Closed
    pwm.set_pwm(JR, 0, servoJR_min) # Jaw Closed

def moveHead(rot,lel,rel,delay):
    pwm2.set_pwm(ROT, 0, rot) # Rot'n: 270 = Max Left, 650 = Max Right, 470 Center
    pwm2.set_pwm(REV, 0, rel) # R Elev: 390 = Max Up, 200 = Max  Down, 295 Center
    pwm2.set_pwm(LEV, 0, lel) # L Elev: 390 = Max Up, 530 = Max  Down, 460 Center
    time.sleep(delay)

def doNo():
    moveHead(rotc,ltec,rtec,.12)
    moveHead(440,ltec,rtec,.12)
    moveHead(510,ltec,rtec,.12)
    moveHead(430,ltec,rtec,.12)
    moveHead(490,ltec,rtec,.12)
    moveHead(440,ltec,rtec,.12)
    moveHead(rotc,ltec,rtec,.25)

def doYes():
    moveHead(rotc,440,350,.2)        # ltec = 460 # Neck Left Elevator Center?   390 = Max Up, 530 = Max  Down, 440 Center
    moveHead(rotc,480,310,.2)        # rtec = 295 # Neck Right Elevator Center?  390 = Max Up, 200 = Max  Down, 295 Center
    moveHead(rotc,440,350,.2)
    moveHead(rotc,470,320,.2)
    moveHead(rotc,440,350,.2)
    moveHead(rotc,460,330,.12)
    moveHead(rotc,440,350,.25)

doNo()
time.sleep(1)
doYes()
time.sleep(1)

moveHead(rotc,440,350,.25)

exit()

