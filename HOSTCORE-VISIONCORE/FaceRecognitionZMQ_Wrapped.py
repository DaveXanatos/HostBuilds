# USAGE
# python FaceRecognitionZMQ_Wrapped.py --cascade haarcascade_frontalface_default.xml --encodings encodings.pickle

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
import cv2
import zmq
import os
import imagezmq

context = zmq.Context()
global framecount
framecount = 0
global newName
newName = ""

print("Connecting Visual Center to Speech Center")
socket = context.socket(zmq.REQ)
socket.connect("tcp://192.168.1.201:5555")

socketV = context.socket(zmq.REP)  # This one listens for commands such as intr$
socketV.bind("tcp://*:5556")

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

def processImage(winName,frame):
    # convert the input frame from (1) BGR to grayscale (for face
    # detection) and (2) framefrom BGR to RGB (for face recognition)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # detect faces in the grayscale frame
    rects = detector.detectMultiScale(gray, scaleFactor=1.1, 
        minNeighbors=5, minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE)

    # Center of Everything is RED, to provide a visual for development:
    cv2.circle(frame,(250,188),5,(0,0,255))  # Images are 500 x 375

    # OpenCV returns bounding box coordinates in (x, y, w, h) order
    # but we need them in (top, right, bottom, left) order, so we
    # need to do a bit of reordering
    boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

    if boxes != []:   # Center is 250, 188
        print(rects, boxes)  # [[185 121 135 135]]  X Y W H  - NOTE NO COMMAS!
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
            # Here is where I will add something to greet newly seen faces.
            #print("Threading Activecount = " + str(threading.active_count()))
            if name not in greetedPeople:
                speakText = "Hello there " + name
                print(speakText)
                #set_voice(speakText)
                thread = Thread(target = set_voice, args = (speakText, ))
                thread.start()
                greetedPeople.append(name)
        # update the list of names
        names.append(name)

    # Routine for creating new directory, for new, "Introduced" faces, is:
    # os.makedirs(directoryName) # where directoryName is name of "introduced" pers$
    # Added the above way up top to keep it out of the loop

    #directoryName = "/home/pi/Desktop/HOSTCORE/NEWFACES/" + newName
    if newName != "":
        if not os.path.exists("/home/pi/Desktop/HOSTCORE/NEWFACES/" + newName):
            os.makedirs("/home/pi/Desktop/HOSTCORE/NEWFACES/" + newName)
            speakText = "Hello there " + newName
            print(speakText)
            thread = Thread(target = set_voice, args = (speakText, ))
            thread.start()
            greetedPeople.append(newName)

    # loop over the recognized faces
    for ((top, right, bottom, left), name) in zip(boxes, names):
        # draw the predicted face name on the image
        cv2.rectangle(frame, (left, top), (right, bottom),(0, 255, 0), 2)
        y = top - 15 if top - 15 > 15 else top + 15
        framecount = 0
        if name == "Unknown":
            framecount = framecount + 1
            if newName == "":
                showName = "Unknown " + str(framecount)
            else:
                showName = newName + " " + str(framecount)
            if framecount % 5 == 0:
                if newName != "":
                    cv2.imwrite('/home/pi/Desktop/HOSTCORE/NEWFACES/' + newName + "/" + str(framecount) + '.jpg', frame)

            cv2.putText(frame, showName, (left, y), cv2.FONT_HERSHEY_SIMPLEX,0.75, (0, 255, 0), 2)
        else:
            showName = name
            cv2.putText(frame, showName, (left, y), cv2.FONT_HERSHEY_SIMPLEX,0.75, (0, 255, 0), 2)

    # display the image to our screen
    cv2.imshow(winName, frame)
    key = cv2.waitKey(1) & 0xFF


greetedPeople = []

SpeakText = "Visual Centers Acquiring."
socket.send_string(SpeakText)
message = socket.recv()

# Create a hub for receiving images from cameras
image_hub = imagezmq.ImageHub(open_port='tcp://192.168.1.210:5560', REQ_REP=False)

# Create a PUB server to send images for monitoring purposes in a non-blocking mode
#stream_monitor = imagezmq.ImageSender(connect_to = 'tcp://*:5566', REQ_REP = False)

# Start main loop
while True:
    #rpi_name, image = image_hub.recv_image()
    (winName, frame) = image_hub.recv_image()
    frame = imutils.resize(frame, width=500)
    processImage(winName,frame)
#    stream_monitor.send_image(rpi_name, image)
