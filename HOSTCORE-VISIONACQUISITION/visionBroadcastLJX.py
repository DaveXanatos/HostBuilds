# Broadcast LEFT eye image stream to system in PUB mode
# imagezmq folder must be present in project folder
# This version uses JPG compression

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
sender = imagezmq.ImageSender(connect_to='tcp://192.168.1.210:5560', REQ_REP=False)

vs = VideoStream(src=0).start()
time.sleep(2.0)
jpeg_quality = 75

image_window_name = 'LEFT'
while True:  # press Ctrl-C to stop image sending program
    # Send an image to the queue
    frame = vs.read()
    frame = imutils.resize(frame, width=400)

    #frame = np.array(list(reversed(frame))) #Needs to also be flipped horiz.
    #NOTE:  Apparently computationally more intensive than cv2.flip()

    #frame = cv2.flip(frame, -1) # 0-X axis; 1-Y Axis, -1=Both.  Reads Right.
    #NOTE:  Apparently Pixel Values get reversed - FR seems to work opposite
    # when flip is employed, so eyes are sent in the wrong direction.

    frame = cv2.rotate(frame, cv2.ROTATE_180) # Reads Right, but suffers
    # from same pixel index reversal as cv2.flip.

    ret_code, jpg_buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality])
    sender.send_jpg(image_window_name, jpg_buffer)
    time.sleep(.1)

