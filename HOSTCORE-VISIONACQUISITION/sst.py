import time
import RPi.GPIO as GPIO
import os

sleepIO = 20  #GPIO20, PIN 38

GPIO.setmode(GPIO.BCM)  # choose BCM or BOARD
GPIO.setup(sleepIO, GPIO.IN, pull_up_down = GPIO.PUD_UP) # GPIO20 PIN 38

def Int_shutdown(channel):
        #os.system("sudo shutdown -h now")
        print("Switch Press Detected")

#GPIO.add_event_detect(sleepIO, GPIO.FALLING, callback = Int_shutdown, bouncetime = 200)

# do nothing while waiting for shutdown button to be pressed
pressed = False
pCount = 0
while 1:
    if not GPIO.input(sleepIO):
        if not pressed:
            print("Button Pressed", pCount)
            pCount = pCount + 1
            pressed = True
    else:
        pressed = False
    time.sleep(.1)




