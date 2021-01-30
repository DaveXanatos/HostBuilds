# USAGE
# python FaceRecognition.py --cascade haarcascade_frontalface_default.xml --encodings encodings.pickle
# Remember to chmod perms to run from launcher.sh otherwise won't find imutils, etc.

# import the necessary packages
import sys
import socket
import face_recognition
import threading
from threading import Thread
import argparse
import imutils
from imutils.video import VideoStream
import pickle
import time
import numpy as np
import cv2
import zmq
import imagezmq
from time import sleep

dev = 1 #1 shows image on screen, 0 does not.  0 *should* be faster...

context = zmq.Context()
framecount = 0
global newName
newName = ""
global sendName
sendName = ""

#Connect to SpeechCenter 5555
print("Connecting Visual Center to Speech Center")
socket = context.socket(zmq.REQ)
socket.connect("tcp://192.168.1.201:5555")

#Bind to 5556 to receive instructions from LanguageCORE
socketV = context.socket(zmq.REP)  # This one listens for commands such as introduction names.  Note port 5556.
socketV.bind("tcp://192.168.1.210:5556")

#Connect to MotorFunctions 5558 to send eye movement data
socketM = context.socket(zmq.PUB)
socketM.bind("tcp://192.168.1.210:5558")
time.sleep(2)

if dev == 1:
    test_img = np.zeros(shape=(300,400,3)).astype('uint8')
    cv2.namedWindow('FR Frame', cv2.WINDOW_GUI_NORMAL)
    cv2.imshow('FR Frame',test_img)
    cv2.moveWindow('FR Frame',125,0)
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

def set_voice(msg):
    socket.send_string(msg)
    #message = socket.recv().decode('utf-8')

def set_eyes(faceCenter):
    socketM.send_string(faceCenter)
    #message = socketM.recv().decode('utf-8')

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--cascade", required=True,
    help = "path to where the face cascade resides")
ap.add_argument("-e", "--encodings", required=True,
    help="path to serialized db of facial encodings")
args = vars(ap.parse_args())

# load the known faces and embeddings along with OpenCV's Haar
# cascade for face detection
print("[INFO] loading encodings + face detector...")
data = pickle.loads(open(args["encodings"], "rb").read())
detector = cv2.CascadeClassifier(args["cascade"])

# initialize the video stream and allow the camera sensor to warm up
print("[INFO] starting video stream...")

greetedPeople = []

SpeakText = "Visual Centers Acquiring."
socket.send_string(SpeakText)
message = socket.recv()

if __name__ == "__main__":
    # Receive from broadcast
    # There are 2 hostname styles; comment out the one you don't need
    #hostname = "127.0.0.1"  # Use to receive from localhost
    hostname = "192.168.1.210"  # Use to receive from other computer
    port = 5560
    receiver = VideoStreamSubscriber(hostname, port)

    try:
        while True:
            winName, image = receiver.receive()
            frame = cv2.imdecode(np.frombuffer(image, dtype='uint8'), -1)

            # convert the input frame from (1) BGR to grayscale (for face
            # detection) and (2) from BGR to RGB (for face recognition)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # detect faces in the grayscale frame
            rects = detector.detectMultiScale(gray, scaleFactor=1.1,
                minNeighbors=5, minSize=(30, 30),
                flags=cv2.CASCADE_SCALE_IMAGE)

            # Center of Everything is RED, to provide a visual for development:
            #cv2.circle(frame,(250,188),5,(0,0,255))  # Images are 500 x 375
            if dev == 1:
                cv2.circle(frame,(200,150),5,(0,0,255))  # Images are 400 x 300

            # OpenCV returns bounding box coordinates in (x, y, w, h) order
            # but we need them in (top, right, bottom, left) order, so we
            # need to do a bit of reordering
            boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]
            faceCenter = [(x+w/2, y+h/2) for (x, y, w, h) in rects]

            # compute the facial embeddings for each face bounding box
            encodings = face_recognition.face_encodings(rgb, boxes)
            names = []

            # loop over the facial embeddings
            for encoding in encodings:
                # attempt to match each face in the input image to our known encodings
                matches = face_recognition.compare_faces(data["encodings"], encoding)
                name = "Unknown"

                # check to see if we have found a match
                if True in matches:
                    # find the indexes of all matched faces then initialize a
                    # dictionary to count the total number of times each face
                    # was matched
                    matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                    counts = {}

                    # loop over the matched indexes and maintain a count for
                    # each recognized face face
                    for i in matchedIdxs:
                        name = data["names"][i]
                        counts[name] = counts.get(name, 0) + 1

                    # determine the recognized face with the largest number
                    # of votes (note: in the event of an unlikely tie Python
                    # will select first entry in the dictionary)
                    name = max(counts, key=counts.get)
                # update the list of names
                names.append(name)

            # loop over the recognized faces
            for ((top, right, bottom, left), name) in zip(boxes, names):
                # draw the predicted face name on the image
                if dev == 1:
                    cv2.rectangle(frame, (left, top), (right, bottom),(0, 255, 0), 1)
                y = top - 15 if top - 15 > 15 else top + 15
                if name == "Unknown":
                    framecount = framecount + 1
                    if newName == "":
                        showName = "Unknown " + str(framecount)
                    else:
                        showName = newName + " " + str(framecount)

                    if dev ==1:
                        cv2.putText(frame, showName, (left, y), cv2.FONT_HERSHEY_SIMPLEX,0.75, (0, 255, 0), 1)
                else:
                    showName = name
                    sendName = name
                    if dev == 1:
                        cv2.putText(frame, showName, (left, y), cv2.FONT_HERSHEY_SIMPLEX,0.75, (0, 255, 0), 1)

            # display the image to our screen
            if boxes != []:   # Center is 250, 188
                #print(rects, boxes, showName)  # [[185 121 135 135]]  X Y W H  - NOTE NO COMMAS!
                #rects: x, y, w, h; boxes: y, x+w, y+h, x; FaceCenters: x+w/2, y+h/2
                #set_eyes(faceCenter) # ERROR: TypeError: unicode/str objects only
                print("Face Center: ", faceCenter, showName)
                faceString = str(faceCenter[0][0])+"|"+str(faceCenter[0][1])
                print("Isolated: ", faceString)
                set_eyes(faceString)
            if dev == 1:
                cv2.imshow("FR Frame", frame)
                key = cv2.waitKey(1) & 0xFF

            # if the `q` key was pressed, break from the loop
            #if key == ord("q"):
                #break

        # do a bit of cleanup
        #cv2.destroyAllWindows()

    except (KeyboardInterrupt, SystemExit):
        print('Exit due to keyboard interrupt')
    except Exception as ex:
        print('Python error with no Exception handler:')
        print('Traceback error:', ex)
        traceback.print_exc()
    finally:
        receiver.close()
        sys.exit()

