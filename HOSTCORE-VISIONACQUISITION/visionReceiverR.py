# Uncommitted receiver for RIGHT eye stream.  Just displays the images.


import sys
import numpy as np
import cv2
import imagezmq

image_hub = imagezmq.ImageHub(open_port='tcp://192.168.1.210:5561', REQ_REP=False)

test_img = np.zeros(shape=(300,400,3)).astype('uint8')
cv2.imshow('RIGHT',test_img)
cv2.moveWindow('RIGHT',527,0)
cv2.waitKey(1)

while True:  # press Ctrl-C to stop image display program
    image_name, image = image_hub.recv_image()
    cv2.imshow(image_name, image)
    cv2.waitKey(1)  # wait until a key is pressed
