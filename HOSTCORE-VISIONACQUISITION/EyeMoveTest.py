# USAGE
# python /home/pi/Desktop/HOSTCORE/EyeCenteringTool.py
# Revision date 2020-04-14.

# import the necessary packages
from __future__ import division
import time
import RPi.GPIO as GPIO
import Adafruit_PCA9685
from random import randrange
import zmq

context = zmq.Context()

socketV = context.socket(zmq.SUB)  # Listens for commands to move eyes (sharp noises, etc.)
socketV.connect("tcp://192.168.1.202:5558")
socketV.setsockopt_string(zmq.SUBSCRIBE, "")

print('\033c')
#print(chr(27)+'[2j')
#print('\x1bc')

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
SSRH = 3.5 #ScreenServoRatioH
SSRV = 3.5 #ScreenServoRatioV

def watchCmd():
    try:
        message = socketV.recv_string(flags=zmq.NOBLOCK) # Watches on :5558
    except:
        message = "E|0"

    print(message,"               ")
    if message != "E|0":  # This allows it to not get 0|0 AND lets me set actions for "E"
        extMoveCmd = message.split("|")
        emcH = float(extMoveCmd[0])
        emcV = float(extMoveCmd[1])
        servoMoveToH = int(((emcH - ScreenCenterH)/SSRH) * -1)
        servoMoveToV = int(((emcV - ScreenCenterV)/SSRV) * -1)
    else:
        emcH = 0
        emcV = 0
        servoMoveToH = 0
        servoMoveToV = 0

    return emcH,emcV,servoMoveToH,servoMoveToV,message

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

doBlink()

noFace = 0
while True:
    emcH,emcV,smtH,smtV,rawMsg = watchCmd()  # eye move command V & H is screen pixel location
    if rawMsg == "E|0":
        noFace = noFace + 1
        if noFace > 4:
            #doRandom(rvlc, rvrc, rhlc, rhrc)
            doCenter()
    else:
        noFace = 0
        vOffset = smtV # Will be smtV         servo move to V & H is calculated servo offsets
        hOffset = smtH # Will be smtH
        #print("\033[1;0HData: ",emcH,emcV,smtH,smtV,"          ")
        print("Data: ",emcH,emcV,smtH,smtV,rawMsg,rvlc,rvrc,rhlc,rhrc,"          ")
        vlp, vrp, hlp, hrp = doEyeMove(vOffset, hOffset, .25, rvlc, rvrc, rhlc, rhrc)
        rvlc = vlp # running vertical left center = vertical left positioning
        rvrc = vrp
        rhlc = hlp
        rhrc = hrp
        print(rvlc,rvrc,rhlc,rhrc)
        print("===============================================================")

    # Look Center
    #vOffset = 0
    #hOffset = 0
    #stepTime = .1
    #doEyeMove(vOffset, hOffset, stepTime)

exit()

