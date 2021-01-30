# USAGE
# python /home/pi/Desktop/HOSTCORE/EyeCenteringTool.py
# Revision date 2020-04-14.

# import the necessary packages
from __future__ import division
import time
import RPi.GPIO as GPIO
import Adafruit_PCA9685
from random import randrange
import threading
from threading import Thread
from collections import deque
import zmq

gainH = 0.90  # Tune to eliminate oscillations
gainV = 0.90
ScreenCenterH = 200
ScreenCenterV = 150
SSRH = 3.15 #ScreenServoRatioH
SSRV = 3.15 #ScreenServoRatioV

facePos_q = deque(maxlen=3)

context = zmq.Context()

socket = context.socket(zmq.REQ)
socket.connect("tcp://192.168.1.201:5555") # Mostly for speaking statuses at st$

hlc = 270  # Experimentally Determined Left Horizontal Center Value
hrc = 370  # Experimentally Determined Right Horizontal Center Value
vlc = 320  # Experimentally Determined Left Vertical Center Value (Lower = Higher)
vrc = 312  # Experimentally Determined Right Vertical Center Value (Lower = Lower)

rhlc = hlc # Running values for servo centers (these change with every face detection center point data
rhrc = hrc
rvlc = vlc
rvrc = vrc

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

# No function should ever decrement/increment below _min or above _max
servoLH_min = 230  # hlc = 270; - 60 = 210
servoLH_max = 310  # hlc = 270; + 40 = 330
servoLV_min = 290  # vlc = 320; - 30 = 290
servoLV_max = 350  # vlc = 320; + 30 = 350

servoRH_min = 330  # hrc = 370; - 60 = 310
servoRH_max = 410  # hrc = 370; + 60 = 430
servoRV_min = 282  # vrc = 312; - 30 = 282
servoRV_max = 342  # vrc = 312; + 30 = 342

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

SpeakText = "Motor Functions are Acquiring."
socket.send_string(SpeakText)

# Eyes: (All Centered):
pwm.set_pwm(LUD, 0, vlc)     # L U/D Sync'd   320 Higher = down
pwm.set_pwm(RUD, 0, vrc)     # R U/D Sync'd   320 Lower = down
pwm.set_pwm(LLR, 0, hlc)     # L L/R Sync'd   270 Higher = lefter
pwm.set_pwm(RLR, 0, hrc)     # R L/R Sync'd   380 Higher = lefter
time.sleep(1)

exit()

