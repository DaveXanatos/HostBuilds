# Broadcast RIGHT eye image stream to system in PUB mode
# imagezmq folder must be present in project folder

import imutils
from imutils.video import VideoStream
import argparse
import socket
import sys
import time
import numpy as np
import cv2
import imagezmq

# Create an image sender in PUB/SUB (non-blocking) mode
sender = imagezmq.ImageSender(connect_to='tcp://192.168.1.210:5561', REQ_REP=False)

#vs = VideoStream(src=1,usePiCamera=True).start()
vs = VideoStream(src=1).start()
time.sleep(2.0)

image_window_name = 'RIGHT'
#i = 0
while True:  # press Ctrl-C to stop image sending program
    # Increment a counter and print it's current state to console
    #i = i + 1
    #print('Sending ' + str(i))

    # Send an image to the queue
    frame = vs.read()
    frame = imutils.resize(frame, width=400)
    sender.send_image(image_window_name, frame)
    time.sleep(.1)
