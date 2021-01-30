# Uncommitted receiver for LEFT eye stream.  Just displays the images.

import sys
import numpy as np
import cv2
import imagezmq

test_img = np.zeros(shape=(300,400,3)).astype('uint8')
cv2.namedWindow('LEFT', cv2.WINDOW_GUI_NORMAL)
cv2.imshow('LEFT',test_img)
cv2.moveWindow('LEFT',125,0)
cv2.waitKey(1)

while True:  # press Ctrl-C to stop image display program
    image_hub = imagezmq.ImageHub(open_port='tcp://192.168.1.210:5560', REQ_REP=False)
    image_name, image = image_hub.recv_image()
    #image_name, jpg_buffer = image_hub.recv_jpg()
    #image = cv2.imdecode(np.frombuffer(jpg_buffer, dtype='uint8'), -1)
    cv2.imshow(image_name, image)
    cv2.waitKey(1)  # wait until a key is pressed
    #image_hub.send_reply(b'OK') # REQ/REP Only


