# python SpeechCenter.py - Connects to port 5555 using ZeroMQ, receives speech commands from other scripts

import time
import zmq
import os
import re

# Open Host Behavior Matrix on Server Portal Folder:
Host = open('/var/www/html/HostBuilds/ACTIVEHOST.txt', "r")  # On Host Processor
HostLines = Host.readlines()
Host.close

HostIDparts = HostLines[0].split("|")  # HostLines[0] contains the base self attributes, [1] contains system parameters for OpenCV, etc., [2] - [21] contain the matrix attributes
V = HostIDparts[5]  # Host Voice

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

def set_voice(V,T):
    audioFile = "/home/pi/Desktop/HOSTCORE/tmp.wav"
    if V == "A":
        os.system("swift -n Allison -o " + audioFile + " " +T+ " && aplay -D plughw:1,0 " + audioFile) 
    if V == "B":
        os.system("swift -n Belle -o " + audioFile + " " +T+ " && aplay -D plughw:1,0 " + audioFile) 
    if V == "C":
        os.system("swift -n Callie -o " + audioFile + " " +T+ " && aplay -D plughw:1,0 " + audioFile) 
    if V == "D":
        os.system("swift -n Dallas -o " + audioFile + " " +T+ " && aplay -D plughw:1,0 " + audioFile) 
    if V == "V":
        os.system("swift -n David -o " + audioFile + " " +T+ " && aplay -D plughw:1,0 " + audioFile) 

pronunciationDict = {'Maeve':'Mayve','Mariposa':'May-reeposah','Lila':'Lie-la','Trump':'Ass hole'}

def adjustResponse(response):     # Adjusts spellings in verbal output string only to create better speech output, things like Maeve and Mariposa
    for key, value in pronunciationDict.items():
        if key in response or key.lower() in response:
            response = re.sub(key, value, response, flags=re.I)
    return response

SpeakText="Speech center connected and online."
set_voice(V,SpeakText) # Cepstral  Voices: A = Allison; B = Belle; C = Callie; D = Dallas; V = David;
print(SpeakText)

while True:
    SpeakText = socket.recv().decode('utf-8') # .decode gets rid of the b' in front of the string
    SpeakText = re.sub("'", "", SpeakText)
    SpeakTextX = adjustResponse(SpeakText)    # Run the string through the pronunciation dictionary
    set_voice(V,SpeakTextX)
    print("Received request: %s" % SpeakText)
    socket.send_string(str(SpeakText))        # Send data back to source for confirmation