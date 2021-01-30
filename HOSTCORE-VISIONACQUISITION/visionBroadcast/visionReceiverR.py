# Uncommitted receiver for RIGHT eye stream.  Just displays the images.


import sys
import cv2
import imagezmq

image_hub = imagezmq.ImageHub(open_port='tcp://127.0.0.1:5561', REQ_REP=False)
while True:  # press Ctrl-C to stop image display program
    image_name, image = image_hub.recv_image()
    cv2.imshow(image_name, image)
    cv2.waitKey(1)  # wait until a key is pressed
