# USAGE
# python /home/pi/Desktop/HOSTCORE/MotorFunctions.py
# Revision date 2019-02-12

# import the necessary packages
from __future__ import division
import argparse
import time
import datetime
import calendar
import RPi.GPIO as GPIO
import os
import Adafruit_PCA9685
from random import randint
import serial
import threading  #from threading import Thread = way to use for background threading

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
# Neck on pwm2:
ROT = 2   # Rotation
REV = 1   # Right Elevator
LEV = 0   # Left Elevator

# Initialise the PCA9685 using the default address (0x40).
pwm = Adafruit_PCA9685.PCA9685()  #Alternate to specify diff addr:  pwm2 = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)
pwm2 = Adafruit_PCA9685.PCA9685(address=0x42, busnum=1)

# No function should ever decrement/increment below 150 or above 600
servo_min = 150  # Min servo pulse length out of 4096
servo_max = 600  # Max servo pulse length out of 4096

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

#Configure Serial Port and initial comms data
port = "/dev/ttyS0"  #["/dev/serial0", "/dev/ttyS0"]
serialPort = serial.Serial(port, 57600, timeout = .5)   #9600, 14400, 19200, 38400, 57600, 115200, 128000, 256000 bits/s
messNo = 0
serialPort.flushInput()
serialPort.flushOutput()
print (chr(27) + "[2J")  # Clear screen

def setOffsets(rhl, rhr, rvl, rvr):
    global servoActualCL
    global servoActualCR
    global servoActualCVL
    global servoActualCVR
    servoActualCL = rhl
    servoActualCR = rhr
    servoActualCVL = rvl
    servoActualCVR = rvr

def clamp(n, minn, maxn):
    n = max(min(maxn, n), minn)
    return n
    
# Set initial values (Center)
# Rotation: 270 = Max Look Left, 650 = Max Look Right, 470 Center.
lastrotp = 470
# Left Elevator: 390 = Look Up, 530 = Look Down, 460 Center
lastlftp = 460
# Right Elevator: 390 = Look Up, 200 = Look Down, 295 Center
lastrgtp = 295

def largest(num1, num2, num3):
    if (num1 > num2) and (num1 > num3):
        largestNum = num1
    elif (num2 > num1) and (num2 > num3):
        largestNum = num2
    else:
        largestNum = num3
    print("largestNum: ", largestNum, num1, num2, num3)  # For testing/dev only
    return largestNum

def moveHead(lastrotp, newrotp, lastlftp, newlftp, lastrgtp, newrgtp, delay):
    print(lastrotp, newrotp, lastlftp, newlftp, lastrgtp, newrgtp, delay)
    dirRotSteps = 1
    dirLftSteps = 1
    dirRgtSteps = 1
    
    rotSteps = newrotp - lastrotp # = 300 - 470 = -170
    lftSteps = newlftp - lastlftp # = 400 - 460 = -60
    rgtSteps = newrgtp - lastrgtp # = 340 - 295 = 45

    if rotSteps == 0:
        rotSteps = 1
    if lftSteps == 0:
        lftSteps = 1
    if rgtSteps == 0:
        rgtSteps = 1

    if rotSteps < 0:
        dirRotSteps = -1
    if lftSteps < 0:
        dirLftSteps = -1
    if rgtSteps < 0:
        dirRgtSteps = -1

    #print(dirRotSteps, dirLftSteps, dirRgtSteps)

    rotSteps = abs(rotSteps)  # 170
    lftSteps = abs(lftSteps)  # 60
    rgtSteps = abs(rgtSteps)  # 45

    whichLarge = largest(rotSteps, lftSteps, rgtSteps)

    lftMult = lftSteps/whichLarge  # 60/170 = .3529411765
    rgtMult = rgtSteps/whichLarge  # 45/170 = .2647058824
    rotMult = rotSteps/whichLarge  # 170/170 = 1

    lftSteps = lastlftp
    rgtSteps = lastrgtp
    rotSteps = lastrotp

    #print(startPos, newPos, dirSteps)
    for stepVals in range(whichLarge):
        lftSteps = lftSteps + (dirLftSteps * lftMult)
        rgtSteps = rgtSteps + (dirRgtSteps * rgtMult)
        rotSteps = rotSteps + (dirRotSteps * rotMult)
        print(rgtSteps, lftSteps, rotSteps)
        
        lftStepsI = int(lftSteps)
        rgtStepsI = int(rgtSteps)
        rotStepsI = int(rotSteps)
        
        pwm2.set_pwm(REV, 0, rgtStepsI)    
        pwm2.set_pwm(ROT, 0, rotStepsI)    
        pwm2.set_pwm(LEV, 0, lftStepsI)
        
        delay = delay * .0001
        time.sleep(delay)
        print("StepVals: " + str(stepVals) + ", R: " + str(rgtSteps) + ", L: " + str(lftSteps) + ", Ro: " + str(rotSteps) + "\n")  # testing only
        print(rgtMult, lftMult, rotMult)
        
    #return int(rotSteps), int(rgtSteps), int(lftSteps)

hlc = 270  # Experimentally Determined Left Horizontal Center Value
hrc = 380  # Experimentally Determined Right Horizontal Center Value
vlc = 335  # Experimentally Determined Left Vertical Center Value
vrc = 335  # Experimentally Determined Right Vertical Center Value

setOffsets(hlc, hrc, vlc, vrc)  # setOffsets(rhl, rhr, rvl, rvr): Sets ServoActualCenters; Also sets my default, starter values for all servo positions

# Eyes: (All Centered):
pwm.set_pwm(LUD, 0, vlc)     # L U/D Sync'd   335 Higher = down
pwm.set_pwm(RUD, 0, vrc)     # R U/D Sync'd   335 Lower = down
pwm.set_pwm(LLR, 0, hlc)     # L L/R Sync'd   270 Higher = lefter
pwm.set_pwm(RLR, 0, hrc)     # R L/R Sync'd   380 Higher = lefter
time.sleep(1)

# Lids (Blink):
pwm.set_pwm(LLT, 0, 290)     # LLT = 0   # Lid Left Top     Lower = more open.  290 is good start default for full open, Max Closed 480
pwm.set_pwm(LLB, 0, 350)     # LLB = 1   # Lid Left Bottom  Lower = more open.  350 is good start default for full open. Max Closed 520
pwm.set_pwm(LRT, 0, 360)     # LRT = 15  # Lid Right Top    Higher = more open.  360 FO, Max closed 200
pwm.set_pwm(LRB, 0, 345)     # LRB = 14  # Lid Right Bottom Higher = more open.  345 FO, Max closed 205

pwm.set_pwm(LLT, 0, 480)     # LLT = 0   # Lid Left Top     Lower = more open.  300 is good start default for full open, Max Closed 480
pwm.set_pwm(LLB, 0, 520)     # LLB = 1   # Lid Left Bottom  Lower = more open.  350 is good start default for full open. Max Closed 520
pwm.set_pwm(LRT, 0, 200)     # LRT = 15  # Lid Right Top    Higher = more open.  350 FO, Max closed 200
pwm.set_pwm(LRB, 0, 205)     # LRB = 14  # Lid Right Bottom Higher = more open.  345 FO, Max closed 205
time.sleep(.15)              # Time required to allow lids to blink.  Zero time means NO blink.

pwm.set_pwm(LLT, 0, 290)     # LLT = 0   # Lid Left Top     Lower = more open.  290 is good start default for full open, Max Closed 480
pwm.set_pwm(LLB, 0, 350)     # LLB = 1   # Lid Left Bottom  Lower = more open.  350 is good start default for full open. Max Closed 520
pwm.set_pwm(LRT, 0, 360)     # LRT = 15  # Lid Right Top    Higher = more open.  360 FO, Max closed 200
pwm.set_pwm(LRB, 0, 345)     # LRB = 14  # Lid Right Bottom Higher = more open.  345 FO, Max closed 205
time.sleep(1)


# Hard coded to establish fixed starting points/known values in case they're "adjusted" in the physical world.
# Eyes: (All Centered):
pwm.set_pwm(LUD, 0, 345)  # L U/D Sync'd   330 Higher = down
pwm.set_pwm(RUD, 0, 335)  # R U/D Sync'd   360 Lower = down
pwm.set_pwm(LLR, 0, 270)  # L L/R Sync'd   270 Higher = lefter
pwm.set_pwm(RLR, 0, 380)  # R L/R Sync'd   380 Higher = lefter
time.sleep(.5)

# Eyes: (Test Run):
pwm.set_pwm(LUD, 0, 345)  # L U/D Sync'd   c330 Higher = down
pwm.set_pwm(RUD, 0, 335)  # R U/D Sync'd   c360 Lower = down
pwm.set_pwm(LLR, 0, 220)  # L L/R Sync'd   c270 Higher = lefter
pwm.set_pwm(RLR, 0, 270)  # R L/R Sync'd   c380 Higher = lefter
time.sleep(1)

# Eyes: (All Centered):
pwm.set_pwm(LUD, 0, 345)  # L U/D Sync'd   330 Higher = down
pwm.set_pwm(RUD, 0, 335)  # R U/D Sync'd   360 Lower = down
pwm.set_pwm(LLR, 0, 270)  # L L/R Sync'd   270 Higher = lefter
pwm.set_pwm(RLR, 0, 380)  # R L/R Sync'd   380 Higher = lefter
time.sleep(.1)

# Neck:
pwm2.set_pwm(ROT, 0, 470) # Rot'n: 270 = Max Left, 650 = Max Right, 470 Center
pwm2.set_pwm(REV, 0, 295) # R Elev: 390 = Max Up, 200 = Max  Down, 295 Center
pwm2.set_pwm(LEV, 0, 460) # L Elev: 390 = Max Up, 530 = Max  Down, 460 Center
time.sleep(.5)




# Eyes: (Up Left):
pwm.set_pwm(LUD, 0, 300)  # L U/D Sync'd   c345 Higher = down
pwm.set_pwm(RUD, 0, 380)  # R U/D Sync'd   c335 Lower = down
pwm.set_pwm(LLR, 0, 300)  # L L/R Sync'd   c270 Higher = lefter
pwm.set_pwm(RLR, 0, 410)  # R L/R Sync'd   c380 Higher = lefter
#Lids:
pwm.set_pwm(LLT, 0, 200)  # Lid Left Top     Lower = more open.  300 default for full open, Max Closed 480
pwm.set_pwm(LLB, 0, 370)  # Lid Left Bottom  Lower = more open.  350 default for full open. Max Closed 520
pwm.set_pwm(LRT, 0, 450)  # Lid Right Top    Higher = more open. 350 FO, Max closed 200
pwm.set_pwm(LRB, 0, 325)  # Lid Right Bottom Higher = more open. 345 FO, Max closed 205
# Neck: (Up Left)
newrotp = 300
newlftp = 400
newrgtp = 340
delay = 1
moveHead(lastrotp, newrotp, lastlftp, newlftp, lastrgtp, newrgtp, delay)
lastrotp = newrotp
lastlftp = newlftp
lastrgtp = newrgtp
time.sleep(.1)





# Eyes: (All Centered):
pwm.set_pwm(LUD, 0, 345)  # L U/D Sync'd   345 Higher = down
pwm.set_pwm(RUD, 0, 335)  # R U/D Sync'd   335 Lower = down
pwm.set_pwm(LLR, 0, 270)  # L L/R Sync'd   270 Higher = lefter
pwm.set_pwm(RLR, 0, 380)  # R L/R Sync'd   380 Higher = lefter
#Lids:
pwm.set_pwm(LLT, 0, 290)  # Lid Left Top     Lower = more open.  290 default for full open, Max Closed 480
pwm.set_pwm(LLB, 0, 350)  # Lid Left Bottom  Lower = more open.  350 default for full open. Max Closed 520
pwm.set_pwm(LRT, 0, 360)  # Lid Right Top    Higher = more open. 360 FO, Max closed 200
pwm.set_pwm(LRB, 0, 345)  # Lid Right Bottom Higher = more open. 345 FO, Max closed 205
# Neck: (Centered):
newrotp = 470
newlftp = 460
newrgtp = 295
delay = 1
moveHead(lastrotp, newrotp, lastlftp, newlftp, lastrgtp, newrgtp, delay)
lastrotp = newrotp
lastlftp = newlftp
lastrgtp = newrgtp
time.sleep(.1)





# Eyes: (Up Right):
pwm.set_pwm(LUD, 0, 300)  # L U/D Sync'd   c345 Higher = down
pwm.set_pwm(RUD, 0, 380)  # R U/D Sync'd   c335 Lower = down
pwm.set_pwm(LLR, 0, 240)  # L L/R Sync'd   c270 Higher = lefter
pwm.set_pwm(RLR, 0, 330)  # R L/R Sync'd   c380 Higher = lefter
#Lids:
pwm.set_pwm(LLT, 0, 200)  # Lid Left Top     Lower = more open.  290 default for full open, Max Closed 480
pwm.set_pwm(LLB, 0, 370)  # Lid Left Bottom  Lower = more open.  350 default for full open. Max Closed 520
pwm.set_pwm(LRT, 0, 450)  # Lid Right Top    Higher = more open. 360 FO, Max closed 200
pwm.set_pwm(LRB, 0, 325)  # Lid Right Bottom Higher = more open. 345 FO, Max closed 205
#Neck: (Up & Right)
newrotp = 600
newlftp = 400
newrgtp = 340
delay = 1
moveHead(lastrotp, newrotp, lastlftp, newlftp, lastrgtp, newrgtp, delay)
lastrotp = newrotp
lastlftp = newlftp
lastrgtp = newrgtp
time.sleep(.1)





# Eyes: (All Centered):
pwm.set_pwm(LUD, 0, 345)  # L U/D Sync'd   345 Higher = down
pwm.set_pwm(RUD, 0, 335)  # R U/D Sync'd   335 Lower = down
pwm.set_pwm(LLR, 0, 270)  # L L/R Sync'd   270 Higher = lefter
pwm.set_pwm(RLR, 0, 380)  # R L/R Sync'd   380 Higher = lefter
#Lids:
pwm.set_pwm(LLT, 0, 290)  # Lid Left Top     Lower = more open.  290 default for full open, Max Closed 480
pwm.set_pwm(LLB, 0, 350)  # Lid Left Bottom  Lower = more open.  350 default for full open. Max Closed 520
pwm.set_pwm(LRT, 0, 360)  # Lid Right Top    Higher = more open. 360 FO, Max closed 200
pwm.set_pwm(LRB, 0, 345)  # Lid Right Bottom Higher = more open. 345 FO, Max closed 205
# Neck: (Centered)
newrotp = 470
newlftp = 460
newrgtp = 295
delay = 1
moveHead(lastrotp, newrotp, lastlftp, newlftp, lastrgtp, newrgtp, delay)
lastrotp = newrotp
lastlftp = newlftp
lastrgtp = newrgtp
time.sleep(.1)





# Eyes: (Down Right):
pwm.set_pwm(LUD, 0, 390)  # L U/D Sync'd   c345 Higher = down
pwm.set_pwm(RUD, 0, 300)  # R U/D Sync'd   c335 Lower = down
pwm.set_pwm(LLR, 0, 240)  # L L/R Sync'd   c270 Higher = lefter
pwm.set_pwm(RLR, 0, 350)  # R L/R Sync'd   c380 Higher = lefter
#Lids:
pwm.set_pwm(LLT, 0, 380)  # Lid Left Top     Lower = more open.  300 default for full open, Max Closed 480
pwm.set_pwm(LLB, 0, 320)  # Lid Left Bottom  Lower = more open.  350 default for full open. Max Closed 520
pwm.set_pwm(LRT, 0, 300)  # Lid Right Top    Higher = more open. 360 FO, Max closed 200
pwm.set_pwm(LRB, 0, 350)  # Lid Right Bottom Higher = more open. 345 FO, Max closed 205
# Neck: (down Right):
newrotp = 600
newlftp = 500
newrgtp = 220
delay = 1
moveHead(lastrotp, newrotp, lastlftp, newlftp, lastrgtp, newrgtp, delay)
lastrotp = newrotp
lastlftp = newlftp
lastrgtp = newrgtp
time.sleep(.1)





# Eyes: (All Centered):
pwm.set_pwm(LUD, 0, 345)  # L U/D Sync'd   345 Higher = down
pwm.set_pwm(RUD, 0, 335)  # R U/D Sync'd   335 Lower = down
pwm.set_pwm(LLR, 0, 270)  # L L/R Sync'd   270 Higher = lefter
pwm.set_pwm(RLR, 0, 380)  # R L/R Sync'd   380 Higher = lefter
#Lids:
pwm.set_pwm(LLT, 0, 290)  # Lid Left Top     Lower = more open.  290 default for full open, Max Closed 480
pwm.set_pwm(LLB, 0, 350)  # Lid Left Bottom  Lower = more open.  350 default for full open. Max Closed 520
pwm.set_pwm(LRT, 0, 360)  # Lid Right Top    Higher = more open. 360 FO, Max closed 200
pwm.set_pwm(LRB, 0, 345)  # Lid Right Bottom Higher = more open. 345 FO, Max closed 205
# Neck: (Center)
newrotp = 470
newlftp = 460
newrgtp = 295
delay = 1
moveHead(lastrotp, newrotp, lastlftp, newlftp, lastrgtp, newrgtp, delay)
lastrotp = newrotp
lastlftp = newlftp
lastrgtp = newrgtp
time.sleep(.1)





# Eyes: (Down Left):
pwm.set_pwm(LUD, 0, 390)  # L U/D Sync'd   c345 Higher = down
pwm.set_pwm(RUD, 0, 300)  # R U/D Sync'd   c335 Lower = down
pwm.set_pwm(LLR, 0, 320)  # L L/R Sync'd   c270 Higher = lefter
pwm.set_pwm(RLR, 0, 410)  # R L/R Sync'd   c380 Higher = lefter
#Lids:
pwm.set_pwm(LLT, 0, 380)  # Lid Left Top     Lower = more open.  300 default for full open, Max Closed 480
pwm.set_pwm(LLB, 0, 320)  # Lid Left Bottom  Lower = more open.  350 default for full open. Max Closed 520
pwm.set_pwm(LRT, 0, 300)  # Lid Right Top    Higher = more open. 360 FO, Max closed 200
pwm.set_pwm(LRB, 0, 350)  # Lid Right Bottom Higher = more open. 345 FO, Max closed 205
# Neck: (Down Left):
newrotp = 300 
newlftp = 500
newrgtp = 200
delay = 1
moveHead(lastrotp, newrotp, lastlftp, newlftp, lastrgtp, newrgtp, delay)
lastrotp = newrotp
lastlftp = newlftp
lastrgtp = newrgtp
time.sleep(.1)





# Eyes: (All Centered):
pwm.set_pwm(LUD, 0, 345)  # L U/D Sync'd   345 Higher = down
pwm.set_pwm(RUD, 0, 335)  # R U/D Sync'd   335 Lower = down
pwm.set_pwm(LLR, 0, 270)  # L L/R Sync'd   270 Higher = lefter
pwm.set_pwm(RLR, 0, 380)  # R L/R Sync'd   380 Higher = lefter
#Lids:
pwm.set_pwm(LLT, 0, 290)  # Lid Left Top     Lower = more open.  290 default for full open, Max Closed 480
pwm.set_pwm(LLB, 0, 350)  # Lid Left Bottom  Lower = more open.  350 default for full open. Max Closed 520
pwm.set_pwm(LRT, 0, 360)  # Lid Right Top    Higher = more open. 360 FO, Max closed 200
pwm.set_pwm(LRB, 0, 345)  # Lid Right Bottom Higher = more open. 345 FO, Max closed 205
# Neck: (Center)
newrotp = 470
newlftp = 460
newrgtp = 295
delay = 1
moveHead(lastrotp, newrotp, lastlftp, newlftp, lastrgtp, newrgtp, delay)
lastrotp = newrotp
lastlftp = newlftp
lastrgtp = newrgtp
time.sleep(.5)



# DO NO
# Neck: (Left):
newrotp = 440 
newlftp = 460
newrgtp = 295
delay = 0
moveHead(lastrotp, newrotp, lastlftp, newlftp, lastrgtp, newrgtp, delay)
lastrotp = newrotp
lastlftp = newlftp
lastrgtp = newrgtp
#time.sleep(.1)

# Neck: (Right):
newrotp = 500 
newlftp = 460
newrgtp = 295
delay = 0
moveHead(lastrotp, newrotp, lastlftp, newlftp, lastrgtp, newrgtp, delay)
lastrotp = newrotp
lastlftp = newlftp
lastrgtp = newrgtp
#time.sleep(.1)

# Neck: (Left):
newrotp = 450 
newlftp = 460
newrgtp = 295
delay = 0
moveHead(lastrotp, newrotp, lastlftp, newlftp, lastrgtp, newrgtp, delay)
lastrotp = newrotp
lastlftp = newlftp
lastrgtp = newrgtp
#time.sleep(.1)

# Neck: (Right):
newrotp = 480 
newlftp = 460
newrgtp = 295
delay = 0
moveHead(lastrotp, newrotp, lastlftp, newlftp, lastrgtp, newrgtp, delay)
lastrotp = newrotp
lastlftp = newlftp
lastrgtp = newrgtp
#time.sleep(.1)

# Neck: (Center)
newrotp = 470
newlftp = 460
newrgtp = 295
delay = 0
moveHead(lastrotp, newrotp, lastlftp, newlftp, lastrgtp, newrgtp, delay)
lastrotp = newrotp
lastlftp = newlftp
lastrgtp = newrgtp
time.sleep(.5)



# DO YES
# Neck: (Down):
newrotp = 470 
newlftp = 490  # Higher = down (Max up = 390, Max dn =  530, ctr = 460)
newrgtp = 265  # Higher = up (Max up = 390, Max dn = 200, ctr = 295)
delay = 0
moveHead(lastrotp, newrotp, lastlftp, newlftp, lastrgtp, newrgtp, delay)
lastrotp = newrotp
lastlftp = newlftp
lastrgtp = newrgtp
#time.sleep(.1)

# Neck: (Up):
newrotp = 470 
newlftp = 430
newrgtp = 325
delay = 0
moveHead(lastrotp, newrotp, lastlftp, newlftp, lastrgtp, newrgtp, delay)
lastrotp = newrotp
lastlftp = newlftp
lastrgtp = newrgtp
#time.sleep(.1)

# Neck: (Down):
newrotp = 470 
newlftp = 480
newrgtp = 275
delay = 0
moveHead(lastrotp, newrotp, lastlftp, newlftp, lastrgtp, newrgtp, delay)
lastrotp = newrotp
lastlftp = newlftp
lastrgtp = newrgtp
#time.sleep(.1)

# Neck: (Up):
newrotp = 470 
newlftp = 440
newrgtp = 315
delay = 0
moveHead(lastrotp, newrotp, lastlftp, newlftp, lastrgtp, newrgtp, delay)
lastrotp = newrotp
lastlftp = newlftp
lastrgtp = newrgtp
#time.sleep(.1)

# Neck: (Center)
newrotp = 470
newlftp = 460
newrgtp = 295
delay = 0
moveHead(lastrotp, newrotp, lastlftp, newlftp, lastrgtp, newrgtp, delay)
lastrotp = newrotp
lastlftp = newlftp
lastrgtp = newrgtp
time.sleep(2)





x = 1
isFace = 0
noFace = 0
FFS = 0
print (chr(27) + "[2J")  # Clear screen

while True:

    hl = hlc
    hr = hrc
    vl = vlc
    vr = vrc

    try:
        M2R_string = "|RGT|0000000000"  # This gets sent to R and starts the ring

        mNo = format(messNo, '08d')
        M2R_string = "MID|" + mNo + M2R_string
        bytes_sent = serialPort.write(M2R_string)
        print "\033[2;0HSENT: " + str(bytes_sent) + " " + M2R_string + " \n"  # Note positioning escape sequence
        bytesToRead = 35
        R_string = serialPort.read(bytesToRead)  # Read from R
        print "RECEIVED: " + R_string + " \n"
        splLen = len(R_string.split('|'))
        print "Split length: " + str(splLen)
        try:
            MID, MNo, RX, RY, PA, PC, AS = R_string.split('|')
            if int(MNo) == messNo:
                print "DATA GOOD! (" + MNo + " " + str(messNo) + ")\033[K"
            else:
                print "DATA BAD (" + MNo + " " + str(messNo) + ")\033[K"
            if MID == "RGT":
                print "RECEIVED FROM RIGHT: " + str(MNo) + "; RX: " + RX + "; RY: " + RY + "\033[K"  
            else:
                print "Not for me"
        except:
            print "Something screwey\033[K"
            print "--------------------------------\033[K"
            speakText="I\m not feeling quite myself today."
            t1 = threading.Thread(target = hostSpeak, args = (speakText, "C"))
            t1.start()
            #pass
        #serialPort.flushInput()
        #SserialPort.flushOutput()
        #serialPort.close()
        messNo = messNo + 1
    except IOError:
        print "Failed at", port, "\n"
        pass

    if RX =="":
        RX = 0
    if RY =="":
        RY = 0

    RX = int(RX)
    RY = int(RY)

    if RX == 0 and RY == 0:
        isFace = 0
        RX = 200
        RY = 150
    else:
        isFace = 1

    if isFace == 1:
        noFace = 0

        hl = servoActualCL - int(round((RX-200) * .4)) # was .459
        hr = servoActualCR - int(round((RX-200) * .4)) # was .459
        vl = servoActualCVL + int(round((RY-150) * .05)) # was .4, but calc'd at .565
        vr = servoActualCVR - int(round((RY-150) * .05)) # was .4, but calc'd at .565
        
        print "FACE SEEN"
        print "RX: " + str(RX) + ": RX: " + str(RX) + "; RY: " + str(RY) + "; RY: " + str(RY) + "\033[K"
        print "hl: " + str(hl) + "; hr: " + str(hr) + "; vl: " + str(vl) + "; vr: " + str(vr) + "\033[K"

        if FFS == 0:
            speakText="Well Hello there!  I can see you now."
            #background_thread = Thread(target = hostSpeak, args = (speakText, "C"))  # Background = NO SPEECH!
            t1 = threading.Thread(target = hostSpeak, args = (speakText, "C"))
            t1.start()
            #t1.join()  # Join will make main program wait until thread is done.  Leave commented if you wish to allow speech to NOT delay program.
            FFS = 1

    if isFace == 0:
        noFace = noFace + 1

        if noFace >= 20:    # If after 20 data rounds with no face seen, return to center.
            servoActualCL = hlc
            servoActualCR = hrc
            servoActualCVL = vlc
            servoActualCVR = vrc

        hl = servoActualCL
        hr = servoActualCR
        vl = servoActualCVL
        vr = servoActualCVR

        print "NO FACE!!"
        print "RX: " + str(RX) + ": RX: " + str(RX) + "; RY: " + str(RY) + "; RY: " + str(RY) + "\033[K"
        print "hl: " + str(hl) + "; hr: " + str(hr) + "; vl: " + str(vl) + "; vr: " + str(vr) + "\033[K"

    moveToHL = clamp(hl, 220, 370)  # moveToHL = clamp(hl, 240, 460)
    moveToHR = clamp(hr, 270, 440)  # moveToHR = clamp(hr, 240, 460)
    moveToVL = clamp(vl, 270, 400)  # moveToVL = clamp(vl, 280, 440)
    moveToVR = clamp(vr, 270, 400)  # moveToVR = clamp(vr, 280, 440)

    if moveToHR <= 270:
        speakText="Full Right"   # "You are all the way over to my right."
        if not (t1.isAlive()):
            t1 = threading.Thread(target = hostSpeak, args = (speakText, "C"))
            t1.start()
    if moveToHR >= 440:
        speakText="Full Left"    # "You are all the way over to my left."
        if not (t1.isAlive()):
            t1 = threading.Thread(target = hostSpeak, args = (speakText, "C"))
            t1.start()
    if moveToVR <= 270:
        speakText="Full Down"    # "What on earth are you doing down there?"
        if not (t1.isAlive()):
            t1 = threading.Thread(target = hostSpeak, args = (speakText, "C"))
            t1.start()
    if moveToVR >= 400:
        speakText="Full Up"      # "My goodness you sure are tall."
        if not (t1.isAlive()):
            t1 = threading.Thread(target = hostSpeak, args = (speakText, "C"))
            t1.start()

    # Eyes:
    # LEFT EYE SERVO VERTICAL LV,  MaxU: 270  MaxD: 400  C: 345   Range:  130    Calc'd center SHOULD be 335
    # LEFT EYE PIXELS, Max UP: 0, Max Dn: 300, Range: 300, Center: 150
    # RIGHT EYE SERVO VERTICAL RV, MaxU: 400  MaxD: 270  C: 335   Range:  130    Calc'd center SHOULD be 335
    # RIGHT EYE PIXELS, Max UP: 0, Max Dn: 300, Range: 300, Center: 150

    # LH MaxL: 370   MaxR: 220 Centered: 270  Range:  150     Calc'd center SHOULD be 295...
    # RH MaxL: 440   MaxR: 270 Centered: 380  Range:  170     Calc'd center SHOULD be 355

    print "Servo Data:\033[K"
    print "moveToHL: " + str(moveToHL) + "; moveToHR: " + str(moveToHR) + "\033[K"
    print "moveToVL: " + str(moveToVL) + "; moveToVR: " + str(moveToVR) + "\033[K"
    print "Servo Deltas:         "
    print "Delta Center: HL: " + str(servoActualCL-moveToHL) + "     HR: " + str(servoActualCR-moveToHR) + "\033[K"
    print "Delta Center: VL: " + str(servoActualCVL-moveToVL) + "    VR: " + str(servoActualCVR-moveToVR) + "\033[K"

    moveToHR = int((servoActualCR + moveToHR)/2)   # Averages last val (servoActual) with new val (moveTo) - eliminates hysteresis on horizontal.
    moveToHL = int((servoActualCL + moveToHL)/2)
    moveToVR = int((servoActualCVR + moveToVR)/2)
    moveToVL = int((servoActualCVL + moveToVL)/2)

    moveToVL = 400 - (moveToVR - 270)   # For testing only... L seems to be losing it somewhere...
    
    pwm.set_pwm(LUD, 0, moveToVL)     # live = moveToVL; use vlc default for testing; L U/D Sync'd
    pwm.set_pwm(RUD, 0, moveToVR)     # live = moveToVR; use vrc default for testing; R U/D Sync'd
    pwm.set_pwm(LLR, 0, moveToHL)     # live = moveToHL; use hlc default for testing; L L/R Sync'd
    pwm.set_pwm(RLR, 0, moveToHR)     # live = moveToHL; use hrc default for testing; R L/R Sync'd
    
    servoActualCL = clamp(moveToHL, 220, 370)  # Sets servoActual to new values and sets up next round.
    servoActualCR = clamp(moveToHR, 270, 440)
    servoActualCVL = clamp(moveToVL, 270, 400)
    servoActualCVR = clamp(moveToVR, 270, 400)
    time.sleep(.1)

    if devMode == 1:
        print "Servo Actual Center NEW: HL: " + str(servoActualCL) + "     HR: " + str(servoActualCR) + "\033[K"
        print "Servo Actual Center NEW: VL: " + str(servoActualCVL) + "    VR: " + str(servoActualCVR) + "\033[K"
    
    if logMode == 1:
        logString = str(MNo) + "|" + str(RX) + "|" + str(RY) + "|" + str(isFace) + "|" + str(hl) + "|" + str(hr) + "|" + str(vl) + "|" + str(vr) + "|" + str(moveToHL) + "|" + str(moveToHR) + "|" + str(moveToVL) + "|" + str(moveToVR) + "|" + str(servoActualCL) + "|" + str(servoActualCR) + "|" + str(servoActualCVL) + "|" + str(servoActualCVR) + "|\n"
        with open(logFileName, 'a') as file_object:  # w will overwrite file each time, a appends to existing
            file_object.write(logString)

    #time.sleep(.1)

    
