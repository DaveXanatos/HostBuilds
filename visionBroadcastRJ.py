# Broadcast RIGHT eye image stream to system in PUB mode
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
sender = imagezmq.ImageSender(connect_to='tcp://192.168.1.210:5561', REQ_REP=False)

vs = VideoStream(src=1).start()
time.sleep(2.0)
jpeg_quality = 75

image_window_name = 'RIGHT'
while True:  # press Ctrl-C to stop image sending program
    # Send an image to the queue
    frame = vs.read()
    frame = imutils.resize(frame, width=400)
    ret_code, jpg_buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality])
    sender.send_jpg(image_window_name, jpg_buffer)
    time.sleep(.1)



