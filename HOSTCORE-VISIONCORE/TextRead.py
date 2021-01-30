import cv2
import pytesseract
#from picamera.array import PiRGBArray
#from picamera import PiCamera
import numpy as np
import threading
from threading import Thread
import imutils
from imutils.video import VideoStream
import zmq
import imagezmq
from time import sleep

context = zmq.Context()

dev = 1 #1 shows image on screen, 0 does not.  0 *should* be faster...

print("Connecting to Speech Center")
socket = context.socket(zmq.REQ)
socket.connect("tcp://192.168.1.201:5555")   #5556 is visual, 5558 is language, 555 dir to speech

def set_voice(msg):
    socket.send_string(msg)
    #message = socket.recv().decode('utf-8')

if dev == 1:
    test_img = np.zeros(shape=(300,400,3)).astype('uint8')
    cv2.namedWindow('Txt Frame', cv2.WINDOW_GUI_NORMAL)
    cv2.imshow('Txt Frame',test_img)
    cv2.moveWindow('Txt Frame',75,25)
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

    def receive(self, timeout=600.0):
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

# Receive from broadcast
hostname = "192.168.1.210"  # Use to receive from other computer
port = 5560
receiver = VideoStreamSubscriber(hostname, port)

while True:
    winName, frame = receiver.receive()
    image = cv2.imdecode(np.frombuffer(frame, dtype='uint8'), -1)
    cv2.imshow("Txt Frame", image)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("s"):
        print("'S' Received...")
        speakText = pytesseract.image_to_string(image)
        speakText = speakText.replace("|", "I")
        speakText = speakText.replace("’", "'")
        print(speakText)
        thread = Thread(target = set_voice, args = (speakText, ))
        thread.start()
        cv2.imshow("Txt Frame", image)
        cv2.waitKey(0)
        break

cv2.destroyAllWindows()
