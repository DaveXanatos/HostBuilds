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

hlc = 260  # Experimentally Determined Left Horizontal Center Value (Lower = Lefter) was 270
hrc = 370  # Experimentally Determined Right Horizontal Center Value
vlc = 316  # Experimentally Determined Left Vertical Center Value (Lower = Higher) was 320
vrc = 302  # Experimentally Determined Right Vertical Center Value (Lower = Lower) was 312

rhlc = hlc # Running values for servo centers (these change with every
rhrc = hrc # face detection center point data
rvlc = vlc
rvrc = vrc

rotc = 450 # Neck Rotation Center (init 470, lower = lefter)
ltec = 440 # Neck Left Elevator Center?
rtec = 350 # Neck Right Elevator Center?

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
# Jaw on pwm
JL = 4
JR = 11

# Neck on pwm2:
ROT = 2   # Rotation
REV = 1   # Right Elevator
LEV = 0   # Left Elevator

# Initialise the PCA9685 using the default address (0x40).
pwm = Adafruit_PCA9685.PCA9685()  #Alternate to specify diff addr:  pwm2 = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)
pwm2 = Adafruit_PCA9685.PCA9685(address=0x42, busnum=1)

# No function should ever decrement/increment below _min or above _max
servoLH_min = 230  # hlc = 270; - 60 = 210
servoLH_max = 310  # hlc = 270; + 40 = 330
servoLV_min = 268  # vlc = 320; - 30 = 290 Was 290
servoLV_max = 350  # vlc = 320; + 30 = 350

servoRH_min = 330  # hrc = 370; - 60 = 310
servoRH_max = 410  # hrc = 370; + 60 = 430
servoRV_min = 282  # vrc = 312; - 30 = 282
servoRV_max = 338  # vrc = 312; + 30 = 342 Was 342

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

# Eyes: (All Centered):
def doCenter(t):
    pwm.set_pwm(LUD, 0, vlc)     # L U/D Sync'd   320 Higher = down
    pwm.set_pwm(RUD, 0, vrc)     # R U/D Sync'd   320 Lower = down
    pwm.set_pwm(LLR, 0, hlc)     # L L/R Sync'd   270 Higher = lefter
    pwm.set_pwm(RLR, 0, hrc)     # R L/R Sync'd   380 Higher = lefter
    time.sleep(t)

# Eyes: (Look Crosseyed):
def doCross(t):
    pwm.set_pwm(LUD, 0, vlc)     # L U/D Sync'd   320 Higher = down
    pwm.set_pwm(RUD, 0, vrc)     # R U/D Sync'd   320 Lower = down
    pwm.set_pwm(LLR, 0, servoLH_min)
    pwm.set_pwm(RLR, 0, servoRH_max)
    time.sleep(t)

# Eyes: (Look Horizontal Left - AR):
def doAR(t):
    pwm.set_pwm(LUD, 0, vlc)     # L U/D Sync'd   320 Higher = down
    pwm.set_pwm(RUD, 0, vrc)     # R U/D Sync'd   320 Lower = down
    pwm.set_pwm(LLR, 0, servoLH_max)
    pwm.set_pwm(RLR, 0, servoRH_max)
    time.sleep(t)

# Eyes: (Look Horizontal Right - AC):
def doAC(t):
    pwm.set_pwm(LUD, 0, vlc)     # L U/D Sync'd   320 Higher = down
    pwm.set_pwm(RUD, 0, vrc)     # R U/D Sync'd   320 Lower = down
    pwm.set_pwm(LLR, 0, servoLH_min)
    pwm.set_pwm(RLR, 0, servoRH_min)
    time.sleep(t)

# Eyes: (Straight Up):
def doUP(t):
    pwm.set_pwm(LUD, 0, servoLV_min)     # L U/D Sync'd   320 Higher = down
    pwm.set_pwm(RUD, 0, servoRV_max)     # R U/D Sync'd   320 Lower = down
    pwm.set_pwm(LLR, 0, hlc)     # L L/R Sync'd   270 Higher = lefter
    pwm.set_pwm(RLR, 0, hrc)     # R L/R Sync'd   380 Higher = lefter
    time.sleep(t)

# Eyes: (Straight Down):
def doDOWN(t):
    pwm.set_pwm(LUD, 0, servoLV_max)     # L U/D Sync'd   320 Higher = down
    pwm.set_pwm(RUD, 0, servoRV_min)     # R U/D Sync'd   320 Lower = down
    pwm.set_pwm(LLR, 0, hlc)     # L L/R Sync'd   270 Higher = lefter
    pwm.set_pwm(RLR, 0, hrc)     # R L/R Sync'd   380 Higher = lefter
    time.sleep(t)

# Eyes: (Up-Left - Visual Remembered - VR):
def doVR(t):
    pwm.set_pwm(LUD, 0, servoLV_min)     # L U/D Sync'd   320 Higher = down
    pwm.set_pwm(RUD, 0, servoRV_max)     # R U/D Sync'd   320 Lower = down
    pwm.set_pwm(LLR, 0, servoLH_max)
    pwm.set_pwm(RLR, 0, servoRH_max)
    time.sleep(t)

# Eyes: (Up-Right - Visual Constructed - VC):
def doVC(t):
    pwm.set_pwm(LUD, 0, servoLV_min)     # L U/D Sync'd   320 Higher = down
    pwm.set_pwm(RUD, 0, servoRV_max)     # R U/D Sync'd   320 Lower = down
    pwm.set_pwm(LLR, 0, servoLH_min)
    pwm.set_pwm(RLR, 0, servoRH_min)
    time.sleep(t)

# Eyes: (Down-Left - Internal Dialog - ID):
def doID(t):
    pwm.set_pwm(LUD, 0, servoLV_max)     # L U/D Sync'd   320 Higher = down
    pwm.set_pwm(RUD, 0, servoRV_min)     # R U/D Sync'd   320 Lower = down
    pwm.set_pwm(LLR, 0, servoLH_max)
    pwm.set_pwm(RLR, 0, servoRH_max)
    time.sleep(t)

# Eyes: (Down-Right - Kinesthetic - K):
def doK(t):
    pwm.set_pwm(LUD, 0, servoLV_max)     # L U/D Sync'd   320 Higher = down
    pwm.set_pwm(RUD, 0, servoRV_min)     # R U/D Sync'd   320 Lower = down
    pwm.set_pwm(LLR, 0, servoLH_min)
    pwm.set_pwm(RLR, 0, servoRH_min)
    time.sleep(t)

def doEyeMove(vOffset, hOffset, stepTime, rvlc, rvrc, rhlc, rhrc):   # clamp(n, minn, maxn)
    vlp = rvlc - vOffset  # Using RUNNING center Values (updated by face center data each time)
    vrp = rvrc + vOffset
    hlp = rhlc + hOffset
    hrp = rhrc + hOffset
    vlp = clamp(vlp,servoLV_min,servoLV_max) #290 to 340 Left Vertical; vlc = 320 (30 down & 20 up)
    vrp = clamp(vrp,servoRV_min,servoRV_max) #290 to 340 Right Vertical; vrc = 312
    hlp = clamp(hlp,servoLH_min,servoLH_max) #230 to 310 Left Horizontal; hlc = 270
    hrp = clamp(hrp,servoRH_min,servoRH_max) #230 to 310 Right Horizontal; hrc = 370
    pwm.set_pwm(LUD, 0, vlp)     # L U/D Sync'd   320 Higher = down
    pwm.set_pwm(RUD, 0, vrp)     # R U/D Sync'd   320 Lower = down
    pwm.set_pwm(LLR, 0, hlp)     # L L/R Sync'd   270 Higher = lefter
    pwm.set_pwm(RLR, 0, hrp)     # R L/R Sync'd   380 Higher = lefter
    time.sleep(stepTime)
    return vlp, vrp, hlp, hrp

#def doJaw(pct,jdelay):
def doJaw(jawSeq):
    for item in jawSeq:
        pct = item[0]
        jdelay = item[1]
        pct = pct/100
        jawRangeL = servoJL_max - servoJL_min
        jawRangeR = servoJR_max - servoJR_min
        openJL = int(servoJL_min + (jawRangeL * pct))
        openJR = int(servoJR_min + (jawRangeR * pct))
        #print(openJL, openJR)
        #print(servoJL_max, servoJR_max)
        pwm.set_pwm(JL, 0, openJL) # Jaw Open percentage specified
        pwm.set_pwm(JR, 0, openJR) # Jaw Open percentage specified
        #pwm.set_pwm(JL, 0, servoJL_max) # Jaw Open percentage specified
        #pwm.set_pwm(JR, 0, servoJR_max) # Jaw Open percentage specified
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

servoLidLT_max = 270 # max open
servoLidLT_min = 350 # min open (closed)
servoLidLB_max = 350 # max open
servoLidLB_min = 250 # min open (closed)

servoLidRT_max = 360 # max open
servoLidRT_min = 300 # min open (closed)
servoLidRB_max = 345 # max open
servoLidRB_min = 400 # min open (closed)

def doLids(lidSeq):
    for item in lidSeq:
        pct = item[0]
        Ldelay = item[1]
        pct = pct/100
        lidRangeLT = servoLidLT_max - servoLidLT_min  # Current vals yield range LT -80
        lidRangeRT = servoLidRT_max - servoLidRT_min  # vals yield +60
        lidRangeLB = servoLidLB_max - servoLidLB_min  # vals yield +100
        lidRangeRB = servoLidRB_max - servoLidRB_min  # vals yield -55
        openLidLT = int(servoLidLT_min + (lidRangeLT * pct))  # So... 100% = 350 + (-80 * 1) = 270 (max open - YES)  50% = 310
        openLidRT = int(servoLidRT_min + (lidRangeRT * pct))  # So... 100% = 300 + (+60 * 1) = 360 (max open - YES)
        openLidLB = int(servoLidLB_min + (lidRangeLB * pct))  # So... 100% = 250 + (+100 * 1) = 350 (max open - YES)
        openLidRB = int(servoLidRB_min + (lidRangeRB * pct))  # So... 100% = 400 + (-55 * 1) = 345 (max open - YES)
        time.sleep(Ldelay)
        pwm.set_pwm(LLT, 0, openLidLT)     # Lid Left Top     Lower = more open.  270 is OPEN, 350 is closed?
        pwm.set_pwm(LLB, 0, openLidLB)     # Lid Left Bottom  Lower = more open.  350 is OPEN, 250 is closed
        pwm.set_pwm(LRT, 0, openLidRT)     # Lid Right Top    Higher = more open.  360 is OPEN, 300 is closed
        pwm.set_pwm(LRB, 0, openLidRB)     # Lid Right Bottom Higher = more open.  345 is OPEN, 400 is closed
    # Return to default:
    pwm.set_pwm(LLT, 0, 270)     # Lid Left Top     Lower = more open.  270 is OPEN, 350 is closed?
    pwm.set_pwm(LLB, 0, 350)     # Lid Left Bottom  Lower = more open.  350 is OPEN, 250 is closed
    pwm.set_pwm(LRT, 0, 360)     # Lid Right Top    Higher = more open.  360 is OPEN, 300 is closed
    pwm.set_pwm(LRB, 0, 345)     # Lid Right Bottom Higher = more open.  345 is OPEN, 400 is closed
    time.sleep(.1)

def doBlink(qty,addDelay):
    print("blink")
    if qty == "":
        qty = 1
    if addDelay == "":
        addDelay = 0
    for x in range(qty):
        pwm.set_pwm(LLT, 0, 290)     # Lid Left Top     Lower = more open.  290 is OPEN, 350 is closed?
        pwm.set_pwm(LLB, 0, 350)     # Lid Left Bottom  Lower = more open.  350 is OPEN, 250 is closed
        pwm.set_pwm(LRT, 0, 360)     # Lid Right Top    Higher = more open.  360 is OPEN, 300 is closed
        pwm.set_pwm(LRB, 0, 345)     # Lid Right Bottom Higher = more open.  345 is OPEN, 400 is closed

        pwm.set_pwm(LLT, 0, 350)     # Lid Left Top     Lower = more open.  Max Clo$
        pwm.set_pwm(LLB, 0, 250)     # Lid Left Bottom  Lower = more closed.  Max C$
        pwm.set_pwm(LRT, 0, 300)     # Lid Right Top    Higher = more open.  350 FO$
        pwm.set_pwm(LRB, 0, 400)     # Lid Right Bottom Higher = more closed.  345 $
        time.sleep(.15)              # Zero time means NO blink.

        pwm.set_pwm(LLT, 0, 290)     # Lid Left Top     Lower = more open.  290 is $
        pwm.set_pwm(LLB, 0, 350)     # Lid Left Bottom  Lower = more open.  350 is $
        pwm.set_pwm(LRT, 0, 360)     # Lid Right Top    Higher = more open.  360 FO$
        pwm.set_pwm(LRB, 0, 345)     # Lid Right Bottom Higher = more open.  345 FO$
        time.sleep(.1)
        time.sleep(addDelay)


doCenter(1)

#doCross(.5)
#doCenter(.5)
#doAR(.5)
#doAC(.5)
#doCenter(.5)
#doUP(.5)
#doDOWN(.5)
#doCenter(.5)
#doVR(.5)
#doCenter(.5)
#doVC(.5)
#doCenter(.5)
#doID(.5)
#doCenter(.5)
#doNo()
#time.sleep(1)
#doYes()

doK(1.5)
doCenter(.01)

#time.sleep(1)

jawSeq = [(25,.3),(10,.1),(60,.2),(80,.2),(50,.25),(100,.25),(50,.25),(60,.1),(50,.1),(80,.1),(45,.1),(22,.35)]
#doJaw(jawSeq)
thread = Thread(target = doJaw, args = (jawSeq,))
thread.start()

lidSeq = [(50,.2),(75,.5),(10,.1),(50,1),(0,.1),(100,1)]
#doBlink(3,.2)
thread = Thread(target = doLids, args = (lidSeq,))
thread.start()

exit()

