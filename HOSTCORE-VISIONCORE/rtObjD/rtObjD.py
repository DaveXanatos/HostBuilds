# USAGE
# python rtObjD.py --prototxt MobileNetSSD_deploy.prototxt.txt --model MobileNetSSD_deploy.caffemodel

# import the necessary packages
import sys
import socket
import threading
from threading import Thread
import imutils
from imutils.video import VideoStream
import pickle
import time
import numpy as np
import cv2
import zmq
import imagezmq
import argparse

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--prototxt", required=True,
	help="path to Caffe 'deploy' prototxt file")
ap.add_argument("-m", "--model", required=True,
	help="path to Caffe pre-trained model")
ap.add_argument("-c", "--confidence", type=float, default=0.5,
	help="minimum probability to filter weak detections") # default was 0.2
args = vars(ap.parse_args())

dev = 1 #1 shows image on screen, 0 does not.  0 *should* be faster...

context = zmq.Context()
framecount = 0
global newName
newName = ""
global sendName
sendName = ""

#Connect to SpeechCenter 5555
print("[INFO] Connecting Object Recognition to Speech Center")
socket = context.socket(zmq.REQ)
socket.connect("tcp://192.168.1.201:5555")

# initialize the list of class labels MobileNet SSD was trained to
# detect, then generate a set of bounding box colors for each class
CLASSES = ["background", "airplane", "bicycle", "bird", "boat",
	"bottle", "bus", "car", "cat", "chair", "cow", "table",
	"dog", "horse", "motorbike", "person", "pottedplant", "sheep",
	"sofa", "train", "monitor"]
#COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

# load our serialized model from disk
print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

if dev == 1:
    test_img = np.zeros(shape=(300,400,3)).astype('uint8')
    cv2.namedWindow('OD Frame', cv2.WINDOW_GUI_NORMAL)
    cv2.imshow('OD Frame',test_img)
    cv2.moveWindow('OD Frame',525,0)
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

def set_voice(msg):
    socket.send_string(msg)
    #message = socket.recv().decode('utf-8')

# loop over the frames from the video stream
#while True:
if __name__ == "__main__":
    # Receive from broadcast
    # There are 2 hostname styles; comment out the one you don't need
    #hostname = "127.0.0.1"  # Use to receive from localhost
    hostname = "192.168.1.210"  # Use to receive from other computer
    port = 5561 # Right Eye.  Left Eye is 5560.  Arbitrary for now.
    receiver = VideoStreamSubscriber(hostname, port)

    try:
        while True:
            winName, image = receiver.receive()
            frame = cv2.imdecode(np.frombuffer(image, dtype='uint8'), -1)

            # grab the frame dimensions and convert it to a blob
            (h, w) = frame.shape[:2]
            blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
                0.007843, (300, 300), 127.5)

            # pass the blob through the network and obtain the detections and
            # predictions
            net.setInput(blob)
            detections = net.forward()

            # loop over the detections
            for i in np.arange(0, detections.shape[2]):
                # extract the confidence (i.e., probability) associated with
                # the prediction
                confidence = detections[0, 0, i, 2]

                # filter out weak detections by ensuring the `confidence` is
                # greater than the minimum confidence
                if confidence > args["confidence"]:
                    # extract the index of the class label from the
                    # `detections`, then compute the (x, y)-coordinates of
                    # the bounding box for the object
                    idx = int(detections[0, 0, i, 1])
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (startX, startY, endX, endY) = box.astype("int")

                    # draw the prediction on the frame
                    label = "{}: {:.2f}%".format(CLASSES[idx],
                        confidence * 100)
                    cv2.rectangle(frame, (startX, startY), (endX, endY),
                        (0, 255, 0), 1)
                    y = startY - 15 if startY - 15 > 15 else startY + 15
                    cv2.putText(frame, label, (startX, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 1)

            # show the output frame
            cv2.imshow("OD Frame", frame)
            key = cv2.waitKey(1) & 0xFF

            # if the `q` key was pressed, break from the loop
            if key == ord("q"):
                break

    except:
        pass
