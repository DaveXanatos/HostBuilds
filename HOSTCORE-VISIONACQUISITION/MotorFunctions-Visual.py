# USAGE python /home/pi/Desktop/HOSTCORE/MotorFunctions-Visual.py
# Revision date 2021-04-14
# Includes head movements embedded in SpeechCenter.py messaging ( using {} ) on port 5554
# Eye Movements from Face Recognition are received on port 5558

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
import wave
import contextlib

gainH = 0.80  # Tune to eliminate oscillations
gainV = 0.80
ScreenCenterH = 200
ScreenCenterV = 150
SSRH = 3.15 #ScreenServoRatioH
SSRV = 3.15 #ScreenServoRatioV

facePos_q = deque(maxlen=3)
jawC_q = deque(maxlen=1)

context = zmq.Context()

socket = context.socket(zmq.REQ)
socket.connect("tcp://192.168.1.201:5555") # Mostly for speaking statuses at start

socketM = context.socket(zmq.SUB)  # Listens for commands to move eyes (FR, noise, etc)
socketM.connect("tcp://192.168.1.202:5558") # FR on visionCORE is 202:5558; on visionACQ it is 210:5558
socketM.setsockopt_string(zmq.SUBSCRIBE, "")

jawCmd = context.socket(zmq.SUB)  # Listens for commands to move jaw (sync to SpeechCenter.py)
jawCmd.bind("tcp://192.168.1.210:5554") # Listens to SpeechCenter.py on LanguageCORE
jawCmd.setsockopt_string(zmq.SUBSCRIBE, "")

def set_voice(msg):                # Talking to the SpeechCenter
    socket.send_string(msg)
    message = socket.recv().decode('utf-8')

hlc = 260  # Experimentally Determined Left Horizontal Center Value (Lower = Lefter) was 270
hrc = 370  # Experimentally Determined Right Horizontal Center Value
vlc = 316  # Experimentally Determined Left Vertical Center Value (Lower = Higher) was 320
vrc = 302  # Experimentally Determined Right Vertical Center Value (Lower = Lower) was 312

rhlc = hlc # Running values for servo centers (these change with every
rhrc = hrc # face detection center point data)
rvlc = vlc
rvrc = vrc

rotc = 450 # Neck Rotation Center (init 470, lower = lefter)
rotMaxR = 650 # Full Right (+200, actual)
rotMaxL = 270 # Full Left (-180, actual)
rotRng = rotMaxR - rotMaxL  # 380

ltec = 440 # Neck Left Elevator Center?
levMax = 490 # Dev Numbers only + 50 from c
levMin = 390 # Dev Numbers only - 50 from c
levRng = levMax - levMin

rtec = 350 # Neck Right Elevator Center?
revMax = 400 # Dev Numbers only + 50 from c
revMin = 300 # Dev Numbers only - 50 from c
revRng = revMax - revMin

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

servoLidLT_max = 270 # max open
servoLidLT_min = 350 # min open (closed)
servoLidLB_max = 350 # max open
servoLidLB_min = 250 # min open (closed)

servoLidRT_max = 360 # max open
servoLidRT_min = 300 # min open (closed)
servoLidRB_max = 345 # max open
servoLidRB_min = 400 # min open (closed)

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

SpeakText = "Motor Functions are Acquiring."
print(SpeakText)
#socket.send_string(SpeakText)
#message = socket.recv()

def sendSpeech(t,d):
    time.sleep(d)
    socket.send_string(t)
    message = socket.recv()

def clamp(n, minn, maxn):
    n = max(min(maxn, n), minn)
    return n

def doRandom(vlc, vrc, hlc, hrc):
    vOffset = randrange(60)-30
    hOffset = randrange(60)-30
    stepTime = round(((randrange(2500)/1000)+.1), 3)
    #print("Random: ",vOffset,hOffset,stepTime)
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

def doJaw(jawSeq):
    init = 0
    for item in jawSeq:
        startDelay = 0  #(len(jawSeq)*.01)+.5
        pct = item[0]
        jdelay = item[1]
        pct = pct/100
        jawRangeL = servoJL_max - servoJL_min
        jawRangeR = servoJR_max - servoJR_min
        openJL = int(servoJL_min + (jawRangeL * pct))
        openJR = int(servoJR_min + (jawRangeR * pct))
        if init == 0:
            time.sleep(startDelay)
            init = 1
        pwm.set_pwm(JL, 0, openJL) # Jaw Open percentage specified
        pwm.set_pwm(JR, 0, openJR) # Jaw Open percentage specified
        time.sleep(jdelay)
    pwm.set_pwm(JL, 0, servoJL_min) # Jaw Closed
    pwm.set_pwm(JR, 0, servoJR_min) # Jaw Closed

#        LEFT                 RIGHT
# rotc   270 <-------450------->650   +x = righter
#
#        Head UP          Head DOWN
# ltec   390 <-------440------->530   +x = downer
# rtec   390 <-------350------->200   -x = downer

def headServos(rot,lel,rel):
    pwm2.set_pwm(ROT, 0, rot) # Rot'n: 270 = Max Left, 650 = Max Right, 470 Center
    pwm2.set_pwm(LEV, 0, lel) # L Elev: 390 = Max Up, 530 = Max  Down, 460 Center
    pwm2.set_pwm(REV, 0, rel) # R Elev: 390 = Max Up, 200 = Max  Down, 295 Center

#        LEFT                 RIGHT
# rotc   270 <-------450------->650   +x = righter

def moveHead(rotNow,levNow,revNow,rotp,levp,revp,spd,hTime,mult):  # CurrROT, CurrLEV, CurrREV, ROT%, LEV%, REV%, speed, hold time

    rotMove = int((rotRng/2)*(rotp/100)) # Move distance from center
    rotPos = rotMove + rotc # Position to move to (half the range, times %age, + center) = final position
    rotNew = rotNow - rotPos # Distance of move from current position
    rotDir = 1
    if rotNew < 0:
        rotDir = -1

    levMove = int((levRng/2)*(levp/100)) # Move distance from center
    levPos = levMove + ltec # Position to move to (half the range, times %age, + center) = final position
    levNew = levNow - levPos # Distance of move from current position
    levDir = 1
    if levNew < 0:
        levDir = -1

    revMove = int((revRng/2)*(revp/100)) # Move distance from center
    revPos = revMove + rtec # Position to move to (half the range, times %age, + center) = final position
    revNew =  revNow - revPos # Distance of move from current position
    revDir = 1
    if revNew < 0:
        revDir = -1

    countRange = (max(abs(rotNew),abs(levNew),abs(revNew)))

    for x in range(0,countRange,mult): # Count from current (last) position to new position
        if rotDir == 1:
            if rotNow > rotPos:
                rotNow = rotNow - (rotDir * mult)     # Moving head right
                if rotNow <= rotPos:
                    rotNow = rotPos
        else:
            if rotNow < rotPos:
                rotNow = rotNow - (rotDir * mult)      # Moving head right
                if rotNow >= rotPos:
                    rotNow = rotPos

        if levDir == 1:
            if levNow > levPos:
                levNow = levNow - (levDir * mult)      # Head down = lev +
                if levNow <= levPos:
                    levNow = levPos
        else:
            if levNow < levPos:
                levNow = levNow - (levDir * mult)
                if levNow >= levPos:
                    levNow = levPos

        if revDir == 1:
            if revNow > revPos:
                revNow = revNow - (revDir * mult)      # Head down = lev +
                if revNow <= revPos:
                    revNow = revPos
        else:
            if revNow < revPos:
                revNow = revNow - (revDir * mult)
                if revNow >= revPos:
                    revNow = revPos

        rotNow = clamp(rotNow,rotMaxL,rotMaxR) # n, minn, maxn - make sure numbers don't go out of bounds
        levNow = clamp(levNow,levMin,levMax) # n, minn, maxn
        revNow = clamp(revNow,revMin,revMax) # n, minn, maxn

        headServos(rotNow,levNow,revNow)

    return rotPos, levPos, revPos  # Returns head final position setting for servos - so range knows where to start from next time

newHeadRO, newHeadLE, newHeadRE = moveHead(rotc,ltec,rtec,0,0,0,.01,.1,1)
time.sleep(.2)

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

def doNo(newHeadRO, newHeadLE, newHeadRE):
    newHeadRO, newHeadLE, newHeadRE = moveHead(newHeadRO,newHeadLE,newHeadRE,30,0,0,0,.001,2) # +, - = down
    newHeadRO, newHeadLE, newHeadRE = moveHead(newHeadRO,newHeadLE,newHeadRE,-30,0,0,0,.001,3)
    newHeadRO, newHeadLE, newHeadRE = moveHead(newHeadRO,newHeadLE,newHeadRE,30,0,0,0,.001,3) # +, - = down
    newHeadRO, newHeadLE, newHeadRE = moveHead(newHeadRO,newHeadLE,newHeadRE,-30,0,0,0,.001,3)
    newHeadRO, newHeadLE, newHeadRE = moveHead(newHeadRO,newHeadLE,newHeadRE,20,0,0,0,.001,3) # +, - = down
    newHeadRO, newHeadLE, newHeadRE = moveHead(newHeadRO,newHeadLE,newHeadRE,-10,0,0,0,.001,2)
    newHeadRO, newHeadLE, newHeadRE = moveHead(newHeadRO,newHeadLE,newHeadRE,0,0,0,.01,.1,2) # Hardcode to center

def doYes(newHeadRO, newHeadLE, newHeadRE):
    newHeadRO, newHeadLE, newHeadRE = moveHead(newHeadRO,newHeadLE,newHeadRE,0,30,-30,.01,.1,1) # +, - = down
    newHeadRO, newHeadLE, newHeadRE = moveHead(newHeadRO,newHeadLE,newHeadRE,0,-30,30,.01,.1,1) # -, +- = up
    newHeadRO, newHeadLE, newHeadRE = moveHead(newHeadRO,newHeadLE,newHeadRE,0,30,-30,.01,.1,1) # +, - = down
    newHeadRO, newHeadLE, newHeadRE = moveHead(newHeadRO,newHeadLE,newHeadRE,0,-30,30,.01,.1,1) # -, +- = up
    newHeadRO, newHeadLE, newHeadRE = moveHead(newHeadRO,newHeadLE,newHeadRE,0,30,-30,.01,.1,1) # +, - = down
    newHeadRO, newHeadLE, newHeadRE = moveHead(newHeadRO,newHeadLE,newHeadRE,0,-30,30,.01,.1,1) # -, +- = up
    newHeadRO, newHeadLE, newHeadRE = moveHead(newHeadRO,newHeadLE,newHeadRE,0,20,-20,.01,.1,1) # +, - = down
    newHeadRO, newHeadLE, newHeadRE = moveHead(newHeadRO,newHeadLE,newHeadRE,0,-10,10,.01,.1,1) # -, +- = up
    newHeadRO, newHeadLE, newHeadRE = moveHead(newHeadRO,newHeadLE,newHeadRE,0,5,-5,.01,.1,1) # +, - = down
    newHeadRO, newHeadLE, newHeadRE = moveHead(newHeadRO,newHeadLE,newHeadRE,0,0,0,.01,.1,1) # -, +- = up

def doRandomHead():
    elevOffset = randrange(60)-30
    rotOffset = randrange(60)-30
    randTime = round((randrange(4)+1), 1)
    return rotOffset, elevOffset, randTime

doCenter(.5)

doCross(.5)

doCenter(.2)

doAR(.2)

doAC(.2)

doCenter(.2)

doUP(.2)

doDOWN(.2)

doCenter(.2)

doVR(.2)

doCenter(.2)

doVC(.2)

doCenter(.2)

doID(.2)

doCenter(.2)

doK(.2)

doCenter(.1)

#Shake Head Yes with Jaw Movement for "Yes"
SpeakText = "Yes"
thread = Thread(target = sendSpeech, args = (SpeakText,.01))
thread.start()
doYes(newHeadRO, newHeadLE, newHeadRE)
thread.join()
time.sleep(1)

#Shake Head No with Jaw Movement for "No"
SpeakText = "No"
thread = Thread(target = sendSpeech, args = (SpeakText,.01))
thread.start()
doNo(newHeadRO, newHeadLE, newHeadRE)    # qty = num cycles; rng = how wide % of rotRng; spd = delay in secs between steps
thread.join()
time.sleep(1)

SpeakText = "Host Startup Sequence Complete"
thread = Thread(target = sendSpeech, args = (SpeakText,.01))
thread.start()
thread.join()

lidSeq = [(50,.2),(75,.5),(10,.1),(50,1),(120,.5),(100,1)]
thread = Thread(target = doLids, args = (lidSeq,))
thread.start()

def watchCmd():
    while 1 == 1:
        message = socketM.recv() # Watches on :5558 - Eyeball Movement Commands from FaceRecognition.py
        extMoveCmd = message.decode('utf-8')
        facePos_q.append(extMoveCmd)
thread = Thread(target = watchCmd) # Puts watchCmd() in BG thread where it just watches & waits
thread.start()

def checkJaw():
    while True:
        jawString = jawCmd.recv() # Watches on :5554 - Jaw String - Duration, Words qty & letters length
        jawMove = jawString.decode('utf-8')
        jawC_q.append(jawMove)
thread = Thread(target = checkJaw) # Puts checkJaw() in BG thread where it just watches & waits
thread.start()

def randBlink():
    lidSeq = [(100,.2),(30,.35),(100,.1)]
    randTime = round((randrange(22)+7), 3)
    doLids(lidSeq)
    time.sleep(randTime)
    randBlink()
thread = Thread(target = randBlink)
thread.start()

def doRead(newHeadRO, newHeadLE, newHeadRE):
    doID(.2)
    newHeadRO, newHeadLE, newHeadRE = moveHead(newHeadRO,newHeadLE,newHeadRE,-100,160,-160,.01,.1,1) # +x = righter, +, - = down, spd, hldtimt, mult
    return newHeadRO, newHeadLE, newHeadRE

#Testing Only: 10 seconds in teh doRead() position
newHeadRO, newHeadLE, newHeadRE = doRead(newHeadRO, newHeadLE, newHeadRE)
time.sleep(10)

def randHead(newHeadRO, newHeadLE, newHeadRE):
    while True:
        rotOffset, elevOffset, randTime = doRandomHead()
        newHeadRO, newHeadLE, newHeadRE = moveHead(newHeadRO,newHeadLE,newHeadRE,rotOffset,elevOffset,elevOffset*-1,.01,.1,1) # +, - = down
        time.sleep(randTime) # Doing nothing
thread = Thread(target = randHead, args=(newHeadRO,newHeadLE,newHeadRE))
thread.start()

noFace = 0

while True:
    message = "-"

    try:
        message = facePos_q.popleft()
    except:
        time.sleep(.2)
    if message != "-":
        noFace = 0
        extMoveCmd = message.split("|")
        emcH = float(extMoveCmd[0])
        emcV = float(extMoveCmd[1])
        servoMoveToH = int((((emcH - ScreenCenterH)/SSRH) * -1)*gainH)
        servoMoveToV = int((((emcV - ScreenCenterV)/SSRV) * -1)*gainV)
        vOffset = servoMoveToV # Will be smtV         servo move to V & H is calculated servo offsets
        hOffset = servoMoveToH # Will be smtH
        vlp, vrp, hlp, hrp = doEyeMove(vOffset, hOffset, .25, rvlc, rvrc, rhlc, rhrc)
        rvlc = vlp # running vertical left center = vertical left positioning
        rvrc = vrp
        rhlc = hlp
        rhrc = hrp
    else:
        noFace = noFace +1
        if noFace > 20:
            doRandom(vlc, vrc, hlc, hrc)

    try:
        jawString = jawC_q.popleft() # jawString example: 3.465|[4, 2, 7, 4, 2, 9, 3, 4, 3]|('yes', 3, 'no', 8)
        jawC_q.clear()
        print(jawString)
        jawStringRaw = jawString.split("|")
        duration = eval(jawStringRaw[0]) # Ex. 3.465
        jawString = eval(jawStringRaw[1]) # Ex. [4, 2, 7, 4, 2, 9, 3, 4, 3]
        headString = eval(jawStringRaw[2]) # Ex. ('yes', 3, 'no', 8)
        jawOpenPct = 20
        wordTime = round(duration/len(jawString), 3)
        letterDelay = .01 # Hardcoding may be replaced by durational attempts
        wordSpace = .05 # Hardcoding may be replaced by durational attempts
        jawSeq = []
        for item in range(len(jawString)):
            jawString[item] = int(jawString[item])
            jawDelay = round(wordTime,2)
            jawString[item] = min((jawString[item]*jawOpenPct), 80)
            jawSeq.append(list([jawString[item],jawDelay]))
        jawSeq = [(x, y) for x, y in jawSeq] # jawSeq = %open,delay =  [(0,1),(25,.3),(10,.1)]
        print(headString) # Development only.  headString will a) turn off random head movements b) reference incoming string and c) act on it
        thread = Thread(target = doJaw, args = (jawSeq,))
        thread.start()

    except:  #except Exception as e:
        #print(e)
        pass

exit()