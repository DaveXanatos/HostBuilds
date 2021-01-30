# Broadcast LEFT eye image stream to system in PUB mode
# imagezmq folder must be present in project folder

from imutils.video import VideoStream
import argparse
import socket
import sys
import time
import numpy as np
import cv2
import imagezmq

# Create an image sender in PUB/SUB (non-blocking) mode
sender = imagezmq.ImageSender(connect_to='tcp://*:5560', REQ_REP=False)

#vs = VideoStream(src=0,usePiCamera=True).start()
vs = VideoStream(src=0).start()
time.sleep(.1)

winName = 'LEFT'
#i = 0
while True:  # press Ctrl-C to stop image sending program
    # Increment a counter and print it's current state to console
    #i = i + 1
    #print('Sending ' + str(i))

    # Send an image to the queue
    frame = vs.read()
    sender.send_image(winName,frame)
    time.sleep(.1)
