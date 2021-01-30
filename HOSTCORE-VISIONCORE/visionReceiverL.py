# Uncommitted receiver for LEFT eye stream.  Just displays the images.

import sys
import time
import numpy as np
import threading
from threading import Thread
from collections import deque
import cv2
import imagezmq

test_img = np.zeros(shape=(300,400,3)).astype('uint8')
cv2.namedWindow('LEFT', cv2.WINDOW_GUI_NORMAL)
cv2.imshow('LEFT',test_img)
cv2.moveWindow('LEFT',125,0)
cv2.waitKey(1)

image_hub = imagezmq.ImageHub(open_port='tcp://192.168.1.210:5560', REQ_REP=False)
image_q = deque(maxlen=12)

def image_box():
    while True:
        image_name, image = image_hub.recv_image()
        image_q.append(image)
        print("In image_box: ", len(image_q))

thread = Thread(target = image_box)
thread.start()

while True:  # press Ctrl-C to stop image display program
    try:
        next_image = image_q.popleft()
        cv2.imshow('LEFT', next_image)
        print("In main loop: ", len(image_q))
        cv2.waitKey(1)  # wait until a key is pressed
    except:
        pass

    time.sleep(0.0005)


