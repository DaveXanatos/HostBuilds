import time
import RPi.GPIO as GPIO
import os

time.sleep(45) # 45 second delay to allow editing in case there is an immediate shutdown issue.

sleepIO = 20  #GPIO20, PIN 38

GPIO.setmode(GPIO.BCM)  # choose BCM or BOARD
GPIO.setup(sleepIO, GPIO.IN, pull_up_down = GPIO.PUD_UP) # GPIO20 PIN 38

def Int_shutdown():
        print("Entering a Deep and Dreamless Slumber")
        os.system("sudo shutdown -h now")

# do nothing while waiting for shutdown button to be pressed
pressed = False
pCount = 0
while 1:
    if not GPIO.input(sleepIO):
        if not pressed:
            print("Button Pressed", pCount)
            pCount = pCount + 1
            pressed = True
            if (pCount == 4):
                Int_shutdown()
    else:
        pressed = False
    time.sleep(.1)

