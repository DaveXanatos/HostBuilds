import time
import RPi.GPIO as GPIO
import os
import zmq

context = zmq.Context()

GPIO.setmode(GPIO.BOARD)  # choose BCM or BOARD
GPIO.setup(40, GPIO.IN, pull_up_down = GPIO.PUD_UP)  

def Int_shutdown(channel):  
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://localhost:5555")  # Connecting to Speech Center
        socket.send(b" Entering a deep and dreamless slumber")
        message = socket.recv()
        
        os.system("sudo shutdown -h now")	
	
GPIO.add_event_detect(40, GPIO.FALLING, callback = Int_shutdown, bouncetime = 2000)

socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")
socket.send(b" Host Online. . . Hello!")
message = socket.recv()

# do nothing while waiting for shutdown button to be pressed
while 1:
        time.sleep(1)
        
