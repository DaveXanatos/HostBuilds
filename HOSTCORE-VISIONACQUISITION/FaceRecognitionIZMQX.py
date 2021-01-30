# USAGE
# python FaceRecognitionIZMQX.py --cascade haarcascade_frontalface_default.xml --encodings encodings.pickle

# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import threading
from threading import Thread
import argparse
import imutils
import pickle
import time
import numpy as np
import cv2
import zmq
import os
import imagezmq

context = zmq.Context()
framecount = 0
global newName
newName = ""

print("Connecting Visual Center to Speech Center")
socket = context.socket(zmq.REQ)
socket.connect("tcp://192.168.1.201:5555")

socketV = context.socket(zmq.REP)  # This one listens for commands such as introduction names.  Note port 5556.
socketV.bind("tcp://192.168.1.210:5556")

def watchCmd():
    while 1 == 1:
        message = socketV.recv()
        global newName
        newName = message.decode('utf-8')
        #print("Received reply %s " % (newName))
        socketV.send_string(newName)

thread = Thread(target = watchCmd)
thread.start()

def set_voice(msg):
    socket.send_string(msg)
    message = socket.recv().decode('utf-8')
    ##message = message.decode('utf-8')
    #if message == msg:
    #    print(">")
    #else:
    #    print("<")

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
#vs = VideoStream(src=0).start()
#vs = VideoStream(usePiCamera=True).start()
#time.sleep(2.0)
#image_hub = imagezmq.ImageHub(open_port='tcp://192.168.1.210:5560', REQ_REP=False)

# start the FPS counter
fps = FPS().start()

greetedPeople = []

SpeakText = "Visual Centers Acquiring."
socket.send_string(SpeakText)
message = socket.recv()

# loop over frames from the video file stream
while True:
    image_hub = imagezmq.ImageHub(open_port='tcp://192.168.1.210:5560', REQ_REP=False)

    # grab the frame from the threaded video stream and resize it
    # to 500px (to speedup processing)
    #frame = vs.read()
    winName, frame = image_hub.recv_image()
    #winNname, jpg_buffer = image_hub.recv_jpg()
    #frame = cv2.imdecode(np.frombuffer(jpg_buffer, dtype='uint8'), -1)

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
    cv2.circle(frame,(200,150),5,(0,0,255))  # Images are 400 x 300 #Commented for speed?

    # OpenCV returns bounding box coordinates in (x, y, w, h) order
    # but we need them in (top, right, bottom, left) order, so we
    # need to do a bit of reordering
    boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

    if boxes != []:   # Center is 250, 188
        print(rects)  # [[185 121 135 135]]  X Y W H  - NOTE NO COMMAS!
        print(boxes)  # [(121, 320, 256, 185)] T, R, B, L
        # NOTE:  The values shown are for boxes that are roughly centered.

    # compute the facial embeddings for each face bounding box
    encodings = face_recognition.face_encodings(rgb, boxes)
    names = []

    # loop over the facial embeddings
    for encoding in encodings:
        # attempt to match each face in the input image to our known
        # encodings
        matches = face_recognition.compare_faces(data["encodings"],
            encoding)
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
        cv2.rectangle(frame, (left, top), (right, bottom),(0, 255, 0), 2) # Commented to see if it affects speed
        y = top - 15 if top - 15 > 15 else top + 15
        if name == "Unknown":
            framecount = framecount + 1
            if newName == "":
                showName = "Unknown " + str(framecount)
            else:
                showName = newName + " " + str(framecount)

            cv2.putText(frame, showName, (left, y), cv2.FONT_HERSHEY_SIMPLEX,0.75, (0, 255, 0), 2)
        else:
            showName = name
            cv2.putText(frame, showName, (left, y), cv2.FONT_HERSHEY_SIMPLEX,0.75, (0, 255, 0), 2)

    # display the image to our screen
    cv2.imshow("FR Frame", frame)
    key = cv2.waitKey(1) & 0xFF
    #image_hub.send_reply(b'OK') # REQ/REP Only

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break

    # update the FPS counter
    fps.update()

# stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()
