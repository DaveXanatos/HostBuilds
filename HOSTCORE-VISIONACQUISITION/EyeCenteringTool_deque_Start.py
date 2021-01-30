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

facePos_q = deque(maxlen=3)

context = zmq.Context()

socket = context.socket(zmq.REQ)
socket.connect("tcp://192.168.1.201:5555") # Mostly for speaking statuses at st$

socketM = context.socket(zmq.SUB)  # This one listens for commands to move eyes$
socketM.connect("tcp://192.168.1.202:5558")
socketM.setsockopt_string(zmq.SUBSCRIBE, "")

def set_voice(msg):                # This one does any talking to the SpeechCen$
    socket.send_string(msg)
    message = socket.recv().decode('utf-8')

hlc = 270  # Experimentally Determined Left Horizontal Center Value
hrc = 370  # Experimentally Determined Right Horizontal Center Value
vlc = 320  # Experimentally Determined Left Vertical Center Value (Lower = Higher)
vrc = 312  # Experimentally Determined Right Vertical Center Value (Lower = Lower)

rhlc = hlc # Running values for servo centers (these change with every face detection center point data
rhrc = hrc
rvlc = vlc
rvrc = vrc

ScreenCenterH = 200
ScreenCenterV = 150
SSRH = 3.15 #ScreenServoRatioH
SSRV = 3.15 #ScreenServoRatioV

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
servoLH_min = 230  # Min servo pulse length out of 4096; hlc = 270
servoLH_max = 310  # Max servo pulse length out of 4096
servoLV_min = 290  # Min servo pulse length out of 4096; vlc = 320
servoLV_max = 350  # Max servo pulse length out of 4096

servoRH_min = 330  # Min servo pulse length out of 4096; hrc = 370
servoRH_max = 410  # Max servo pulse length out of 4096
servoRV_min = 282  # Min servo pulse length out of 4096; vrc = 312
servoRV_max = 342  # Max servo pulse length out of 4096

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
message = socket.recv()

def clamp(n, minn, maxn):
    n = max(min(maxn, n), minn)
    return n

def doRandom(vlc, vrc, hlc, hrc):
    vOffset = randrange(60)-30
    hOffset = randrange(60)-30
    stepTime = (randrange(2500)/1000)+.1
    print("Random: ",vOffset,hOffset,stepTime)
    doEyeMove(vOffset, hOffset, stepTime, vlc, vrc, hlc, hrc)

def doCenter():
    pwm.set_pwm(LUD, 0, vlc)     # L U/D Sync'd   320 Higher = down
    pwm.set_pwm(RUD, 0, vrc)     # R U/D Sync'd   320 Lower = down
    pwm.set_pwm(LLR, 0, hlc)     # L L/R Sync'd   270 Higher = lefter
    pwm.set_pwm(RLR, 0, hrc)     # R L/R Sync'd   380 Higher = lefter
    time.sleep(.1)

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

# Eyes: (All Centered):
pwm.set_pwm(LUD, 0, vlc)     # L U/D Sync'd   320 Higher = down
pwm.set_pwm(RUD, 0, vrc)     # R U/D Sync'd   320 Lower = down
pwm.set_pwm(LLR, 0, hlc)     # L L/R Sync'd   270 Higher = lefter
pwm.set_pwm(RLR, 0, hrc)     # R L/R Sync'd   380 Higher = lefter
time.sleep(1)

def doBlink():
    pwm.set_pwm(LLT, 0, 290)     # Lid Left Top     Lower = more open.  290 is $
    pwm.set_pwm(LLB, 0, 350)     # Lid Left Bottom  Lower = more open.  350 is $
    pwm.set_pwm(LRT, 0, 360)     # Lid Right Top    Higher = more open.  360 FO$
    pwm.set_pwm(LRB, 0, 345)     # Lid Right Bottom Higher = more open.  345 FO$

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

def watchCmd():
    while 1 == 1:
        message = socketM.recv() # Watches on :5558
        extMoveCmd = message.decode('utf-8')
        facePos_q.append(extMoveCmd)
        #print("Q Len: ", len(facePos_q),extMoveCmd)

thread = Thread(target = watchCmd) # Puts watchCmd() in BG thread where it just$
thread.start()

#while True:
    #message = input("X|Y> ")
    #extMoveCmd = message.split("|")
    #emcH = float(extMoveCmd[0])
    #emcV = float(extMoveCmd[1])
    #servoMoveToH = int(((emcH - ScreenCenterH)/SSRH) * -1)
    #servoMoveToV = int(((emcV - ScreenCenterV)/SSRV) * -1)
    #vOffset = servoMoveToV # Will be smtV         servo move to V & H is calculated servo offsets
    #hOffset = servoMoveToH # Will be smtH
    ###print("\033[1;0HData: ",emcH,emcV,smtH,smtV,"          ")
    #print("Data: ",emcH,emcV,servoMoveToH,servoMoveToV,message,rvlc,rvrc,rhlc,rhrc,"          ")
    #vlp, vrp, hlp, hrp = doEyeMove(vOffset, hOffset, .25, rvlc, rvrc, rhlc, rhrc)
    #rvlc = vlp # running vertical left center = vertical left positioning
    #rvrc = vrp
    #rhlc = hlp
    #rhrc = hrp
    #print(vlp, vrp, hlp, hrp)
    #print("===============================================================")


while True:
    message = "-"
    try:
        message = facePos_q.popleft()
    except:
        time.sleep(.2)
    if message != "-":
        print("next_pos: ", message)
        extMoveCmd = message.split("|")
        emcH = float(extMoveCmd[0])
        emcV = float(extMoveCmd[1])
        servoMoveToH = int(((emcH - ScreenCenterH)/SSRH) * -1)
        servoMoveToV = int(((emcV - ScreenCenterV)/SSRV) * -1)
        vOffset = servoMoveToV # Will be smtV         servo move to V & H is calculated servo offsets
        hOffset = servoMoveToH # Will be smtH






exit()

