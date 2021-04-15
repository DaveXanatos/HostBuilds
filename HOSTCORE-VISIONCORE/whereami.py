# USAGE
# python whereami.py
# Remember to chmod perms to run from launcher.sh otherwise won't find imutils, etc.
# This file operates on startup from launcher.sh and functions to:
#    a) Identify location of robot based on video frame capture and comparison (via hashing and Hamming Distance)
#    b) If location unidentified, robot asks location name and builds hashed image library (17x16) and adds
#       hashes to locationsKnown.txt

# import the necessary packages
import os
import sys
import socket
import threading
from threading import Thread
import argparse
import imutils
from imutils.video import VideoStream
import time
import datetime
import numpy as np
import cv2
import zmq
import imagezmq
from time import sleep

dev = 1 #1 shows image on screen, 0 does not.  0 *should* be faster...

frameInterval = 50
maxLines = 100

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
#socketV = context.socket(zmq.REP)  # This one listens for commands such as introduction names.  Note port 5556.
#socketV.bind("tcp://192.168.1.202:5556")

if dev == 1:
    test_img = np.zeros(shape=(300,400,3)).astype('uint8')
    cv2.namedWindow('LOC Frame', cv2.WINDOW_GUI_NORMAL)
    cv2.imshow('LOC Frame',test_img)
    cv2.moveWindow('LOC Frame',125,0)
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
    message = socket.recv().decode('utf-8')

def dhash(image, hashSize=16):
    # resize the input image, adding a single column (width) for the horizontal gradient
    resized = cv2.resize(image, (hashSize + 1, hashSize))

    # compute the (relative) horizontal gradient between adjacent column pixels
    diff = resized[:, 1:] > resized[:, :-1]

    # convert the difference image to a hash
    return sum([2 ** i for (i, v) in enumerate(diff.flatten()) if v]), resized

def hamming(h1, h2):
    d = h1^h2
    res = bin(d).count('1')
    return res

def getTStampWhen():
    currenttime = datetime.datetime.now()
    dateStamp = str(datetime.date.today().strftime("%Y%m%d"))
    timeStamp = str("%s%s%s" % (currenttime.hour, currenttime.minute, currenttime.second))
    fileStamp = dateStamp + "-" + timeStamp
    return fileStamp

while True:
    # Receive from broadcast
    hostname = "192.168.1.210"  # Use to receive from other computer
    port = 5560
    receiver = VideoStreamSubscriber(hostname, port)
    try:
        currentLoc = ""  # If blank, check new frames against locationsKnown.txt; will set to match else ask "where am I"
        newLoc = ""  # For Development Purposes.  Will be dynamically generated.
        flashCount = 0 # Count of initial "where am I" images
        matchCount = 0 # How many images in locationsKnown match flashcount images
        newLocCandidate = []  # Images that hash within 40 of flashcount images
        whereAmI = [] # Final determination of location, if any
        homeDir = "/home/pi/Desktop/HOSTCORE/"
        while True:
            winName, image = receiver.receive()
            frame = cv2.imdecode(np.frombuffer(image, dtype='uint8'), -1)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            if newLoc != "":
                print("Remembering new location " + newLoc)
                if not os.path.exists(homeDir + "/NEWLOC/" + newLoc):
                    os.makedirs(homeDir + "/NEWLOC/" + newLoc)
                if framecount % frameInterval == 0:
                    print(newLoc,str(framecount))
                    imageHash, resized = dhash(gray)
                    fileStamp = getTStampWhen()
                    cv2.imwrite(homeDir + "/NEWLOC/" + newLoc + "/" + fileStamp + '.jpg', resized) # Hash-sized image (17x16, etc.)
                    with open(homeDir + "locationsKnown.txt", "a") as file_object:
                        file_object.write(str(imageHash) + "|" + newLoc + "|" + fileStamp + "\n")
                    if dev == 1:
                        cv2.imshow("LOC Frame", gray)
                        key = cv2.waitKey(1) & 0xFF
                if framecount >= (frameInterval * maxLines):
                    break

            if currentLoc == "":   # Location unknown
                if flashCount == 0:
                    print("Determining Current Location")
                if flashCount < 4:
                    if framecount % 10 == 0:
                        imageHash, resized = dhash(gray)  # Take 3 shots, 10 frames apart for some variability, get their hash values
                        whereAmI.append(imageHash)        # and append them into a list.
                        flashCount = flashCount + 1       # Increment image count.
                        if dev == 1:
                            cv2.imshow("LOC Frame", gray) # Show on screen only in dev mode
                            key = cv2.waitKey(1) & 0xFF
                if flashCount >= 3:  # Once we have 3 images
                    locFile = open(homeDir + 'locationsKnown.txt', 'r')  # Open locationsKnown, read file lines into array, close
                    Lines = locFile.readlines()
                    locFile.close()
                    for hashes in whereAmI:  # Check the three hash values in whereAmI against the hash values from locationsKnown
                        for line in Lines:
                            thisHash = line.split("|") # locationsKnown.txt format:  hash_value|location name|timestamp
                            hd = hamming(int(thisHash[0]),hashes)
                            if hd <= 100:  # Lower number is more discriminating
                                #matchCount = matchCount + 1
                                newLocCandidate.append(thisHash[1])
                    if len(newLocCandidate) > 0:  # We have at least one match
                        currentLoc = [loc for loc in newLocCandidate if newLocCandidate.count(loc) >= 2]  # Will only add a location if that location's count exceeds specified number
                        msg = "I appear to be in the " + currentLoc[0]
                        print(msg)
                        set_voice(msg)
                        break
                    else:   # We have no matches, need to ask
                        msg = "Where am I?"
                        print(msg)
                        set_voice(msg)
                        whereResponse = input("Where am I? ")  # Development Only.
                        currentLoc = whereResponse
                        newLoc = whereResponse
                        # Needs to wait here for a response in the form of "you are|you're in|at|on the|my" + whereResponse
                        # Then set CurrentLoc to whereResponse word ("Porch", "Office", etc.)
                        # set newLoc = whereResponse, then newLoc will run.  
                        # msg needs to be sent to LanguageCORE LangGen.py so it will know where it is
                        #break
            framecount = framecount + 1

    except (KeyboardInterrupt, SystemExit):
        print('Exit due to keyboard interrupt')
    except Exception as ex:
        print('Python error with no Exception handler:')
        print('Traceback error:', ex)
        traceback.print_exc()
    finally:
        receiver.close()
        sys.exit()


