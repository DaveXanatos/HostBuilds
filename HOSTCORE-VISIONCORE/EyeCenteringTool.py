# USAGE
# python /home/pi/Desktop/HOSTCORE/MotorFunctions.py
# Revision date 2020-02-21.  Looking to silence servos with setPWM with 0 for both the start and stop times.
# If you want to turn the LEDs totally off use setPWM(pin, 4096, 0); not setPWM(pin, 4095, 0)

# import the necessary packages
from __future__ import division
import argparse
import time
import datetime
import calendar
import RPi.GPIO as GPIO
import os
import Adafruit_PCA9685
from random import randrange
import threading  #from threading import Thread = way to use for background threading
from threading import Thread

# Set vars for servos
# Eyes on pwm:
RLR = 13  # R l/r
RUD = 12  # R u/d
LLR = 2   # L l/r
LUD = 3   # L u/d
# Lids on pwm:
LLT = 0   # Lid Left Top
LLB = 1   # Lid Left Bottom
LRT = 15  # Lid Right Top
LRB = 14  # Lid Right Bottom

# Initialise the PCA9685 using the default address (0x40).
pwm = Adafruit_PCA9685.PCA9685()  #Alternate to specify diff addr:  pwm2 = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)
#pwm2 = Adafruit_PCA9685.PCA9685(address=0x42, busnum=1)

# No function should ever decrement/increment below 150 or above 600
servo_min = 200  # Min servo pulse length out of 4096
servo_max = 480  # Max servo pulse length out of 4096

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
#pwm2.set_pwm_freq(60)

def setOffsets(rhl, rhr, rvl, rvr):
    global servoActualCL
    global servoActualCR
    global servoActualCVL
    global servoActualCVR
    servoActualCL = rhl
    servoActualCR = rhr
    servoActualCVL = rvl
    servoActualCVR = rvr
    vOffset = 0
    hOffset = 0
    stepTime = .5

def clamp(n, minn, maxn):
    n = max(min(maxn, n), minn)
    return n

def largest(num1, num2, num3):
    if (num1 > num2) and (num1 > num3):
        largestNum = num1
    elif (num2 > num1) and (num2 > num3):
        largestNum = num2
    else:
        largestNum = num3
    print("largestNum: ", largestNum, num1, num2, num3)  # For testing/dev only
    return largestNum

def doEyeMove(vOffset, hOffset, stepTime):
    vlp = vlc - vOffset
    vrp = vrc + vOffset
    hlp = hlc + hOffset
    hrp = hrc + hOffset
    pwm.set_pwm(LUD, 0, vlp)     # L U/D Sync'd   320 Higher = down
    pwm.set_pwm(RUD, 0, vrp)     # R U/D Sync'd   320 Lower = down
    pwm.set_pwm(LLR, 0, hlp)     # L L/R Sync'd   270 Higher = lefter
    pwm.set_pwm(RLR, 0, hrp)     # R L/R Sync'd   380 Higher = lefter
    time.sleep(stepTime)

hlc = 270  # Experimentally Determined Left Horizontal Center Value
hrc = 370  # Experimentally Determined Right Horizontal Center Value
vlc = 320  # Experimentally Determined Left Vertical Center Value (Lower = Higher)
vrc = 312  # Experimentally Determined Right Vertical Center Value (Lower = Lower)

setOffsets(hlc, hrc, vlc, vrc)  # setOffsets(rhl, rhr, rvl, rvr): Sets ServoActualCenters;
                                # Also sets my default, starter values for all servo positions

# Eyes: (All Centered):
pwm.set_pwm(LUD, 0, vlc)     # L U/D Sync'd   320 Higher = down
pwm.set_pwm(RUD, 0, vrc)     # R U/D Sync'd   320 Lower = down
pwm.set_pwm(LLR, 0, hlc)     # L L/R Sync'd   270 Higher = lefter
pwm.set_pwm(RLR, 0, hrc)     # R L/R Sync'd   380 Higher = lefter
time.sleep(1)

exit()
