# USAGE
# python /home/pi/Desktop/HOSTCORE/MotorFunctions.py
# Revision date 2020-02-21.  Looking to silence servos with setPWM with 0 for both the start and stop times.

# import the necessary packages

from __future__ import division

import sys
sys.path.append('/usr/local/lib/python3.5/dist-packages/')

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
import zmq

OE = 21

context = zmq.Context()

socket = context.socket(zmq.REQ)
socket.connect("tcp://192.168.1.201:5555") # Mostly for speaking statuses at startup

socketV = context.socket(zmq.REP)  # This one listens for commands to move eyes (sharp noises, etc.)
socketV.bind("tcp://*:5558")

GPIO.setmode(GPIO.BCM)  # Using GPIO Numbers, not pins.
GPIO.setup(OE, GPIO.OUT)  # Set up GPIO 4 as output to control Servo Output Enable
GPIO.output(OE, 1) # Set GPIO 4 to 1 to freeze eyeballs initially

extMoveCmd = "X" # Testing here only.  X means to just run a doRandom() - presence of numbers will be a command to move

def watchCmd():
    while 1 == 1:
        message = socketV.recv() # Watches on :5558
        extMoveCmd = message.decode('utf-8')
        #print("Received reply %s " % (newName))
        socketV.send_string(extMoveCmd)
        print("Received: ",extMoveCmd)

thread = Thread(target = watchCmd) # Puts watchCmd() in BG thread where it just listens for commands.
thread.start()

def set_voice(msg):                # This one does any talking to the SpeechCenter
    socket.send_string(msg)
    message = socket.recv().decode('utf-8')
    if message == msg:
        print(">")
    else:
        print("<")

def doRandom():
    vOffset = randrange(60)-30
    hOffset = randrange(60)-30
    stepTime = (randrange(2500)/1000)+.1
    print("Random: ",vOffset,hOffset,stepTime)
    doEyeMove(vOffset, hOffset, stepTime)

SpeakText = "Motor Functions are Acquiring."
socket.send_string(SpeakText)
message = socket.recv()

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

def doBlink():
    pwm.set_pwm(LLT, 0, 290)     # Lid Left Top     Lower = more open.  290 is good start default for full open, Max Closed 480
    pwm.set_pwm(LLB, 0, 350)     # Lid Left Bottom  Lower = more open.  350 is good start default for full open. Max Closed 520
    pwm.set_pwm(LRT, 0, 360)     # Lid Right Top    Higher = more open.  360 FO, Max closed 200
    pwm.set_pwm(LRB, 0, 345)     # Lid Right Bottom Higher = more open.  345 FO, Max closed 205

    pwm.set_pwm(LLT, 0, 350)     # Lid Left Top     Lower = more open.  Max Closed 400
    pwm.set_pwm(LLB, 0, 250)     # Lid Left Bottom  Lower = more closed.  Max Closed 250
    pwm.set_pwm(LRT, 0, 300)     # Lid Right Top    Higher = more open.  350 FO, Max closed 250
    pwm.set_pwm(LRB, 0, 400)     # Lid Right Bottom Higher = more closed.  345 FO, Max closed 405
    time.sleep(.15)              # Zero time means NO blink.

    pwm.set_pwm(LLT, 0, 290)     # Lid Left Top     Lower = more open.  290 is good start default for full open, Max Closed 480
    pwm.set_pwm(LLB, 0, 350)     # Lid Left Bottom  Lower = more open.  350 is good start default for full open. Max Closed 520
    pwm.set_pwm(LRT, 0, 360)     # Lid Right Top    Higher = more open.  360 FO, Max closed 200
    pwm.set_pwm(LRB, 0, 345)     # Lid Right Bottom Higher = more open.  345 FO, Max closed 205
    time.sleep(.1)

hlc = 270  # Experimentally Determined Left Horizontal Center Value
hrc = 370  # Experimentally Determined Right Horizontal Center Value
vlc = 320  # Experimentally Determined Left Vertical Center Value (Lower = High$
vrc = 312  # Experimentally Determined Right Vertical Center Value (Lower = Low$

setOffsets(hlc, hrc, vlc, vrc)  # setOffsets(rhl, rhr, rvl, rvr): Sets ServoActualCenters;
                                # Also sets my default, starter values for all servo positions

GPIO.output(OE, 0) # Unfreeze Eyeballs

# Eyes: (All Centered):
vOffset = 0
hOffset = 0
stepTime = 1
doEyeMove(vOffset, hOffset, stepTime)

# Lids (Blink):
doBlink()

# Eyes:
# Look Upper Left
vOffset = 30
hOffset = 30
stepTime = .5
doEyeMove(vOffset, hOffset, stepTime)

# Look Center
vOffset = 0
hOffset = 0
stepTime = .5
doEyeMove(vOffset, hOffset, stepTime)

# Look Lower Right
vOffset = -30
hOffset = -30
stepTime = .5
doEyeMove(vOffset, hOffset, stepTime)

# Look Center
vOffset = 0
hOffset = 0
stepTime = .5
doEyeMove(vOffset, hOffset, stepTime)

# Look Upper Right
vOffset = 30
hOffset = -30
stepTime = .5
doEyeMove(vOffset, hOffset, stepTime)

# Look Center
vOffset = 0
hOffset = 0
stepTime = .5
doEyeMove(vOffset, hOffset, stepTime)

# Look Lower Left
vOffset = -30
hOffset = 30
stepTime = 1
doEyeMove(vOffset, hOffset, stepTime)

# Look Center
vOffset = 0
hOffset = 0
stepTime = .5
doEyeMove(vOffset, hOffset, stepTime)

speakText = "Motor Functions Online"
print(speakText)
thread = Thread(target = set_voice, args = (speakText, ))  # This line actually speaks the text in speakText
thread.start()

doBlink()

while True:
    if extMoveCmd != "X":
        print(extMoveCmd) # Testing.  Will eventually move eyes to position received from ZMQ port.
        time.sleep(1)
    else:
        doRandom()

GPIO.output(OE, 1) # Freeze Eyeballs

GPIO.cleanup()
exit()
