# Uncommitted receiver for RIGHT eye stream.  Just displays the images.

import sys

import socket
import traceback
import cv2
from imutils.video import VideoStream
import imagezmq
import threading
import numpy as np
from time import sleep

test_img = np.zeros(shape=(300,400,3)).astype('uint8')
cv2.namedWindow('RIGHT', cv2.WINDOW_GUI_NORMAL)
cv2.imshow('RIGHT',test_img)
cv2.moveWindow('RIGHT',425,0)
cv2.waitKey(1)

class VideoStreamSubscriber:

    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port
        self._stop = False
        self._data_ready = threading.Event()
        self._thread = threading.Thread(target=self._run, args=())
        self._thread.daemon = True
        self._thread.start()

    def receive(self, timeout=15.0):
        flag = self._data_ready.wait(timeout=timeout)
        if not flag:
            raise TimeoutError(
                "Timeout while reading from subscriber tcp://{}:{}".format(self.hostname, self.port))
        self._data_ready.clear()
        return self._data

    def _run(self):
        receiver = imagezmq.ImageHub("tcp://{}:{}".format(self.hostname, self.port), REQ_REP=False)
        while not self._stop:
            self._data = receiver.recv_jpg()
            self._data_ready.set()
        # Close socket here, not implemented in ImageHub :(
        # zmq_socket.close()

    def close(self):
        self._stop = True

if __name__ == "__main__":
    # Receive from broadcast
    # There are 2 hostname styles; comment out the one you don't need
    #hostname = "127.0.0.1"  # Use to receive from localhost
    hostname = "192.168.1.210"  # Use to receive from other computer
    port = 5561
    receiver = VideoStreamSubscriber(hostname, port)

    try:
        while True:
            msg, frame = receiver.receive()
            image = cv2.imdecode(np.frombuffer(frame, dtype='uint8'), -1)
            cv2.imshow("RIGHT", image)
            cv2.waitKey(1)
    except (KeyboardInterrupt, SystemExit):
        print('Exit due to keyboard interrupt')
    except Exception as ex:
        print('Python error with no Exception handler:')
        print('Traceback error:', ex)
        traceback.print_exc()
    finally:
        receiver.close()
        sys.exit()

