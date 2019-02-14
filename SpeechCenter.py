# python SpeechCenter.py
# Connects to port 5555 using ZeroMQ, receives speech commands from other scripts

import time
import zmq
import os
import re

# Open Host Behavior Matrix on Server Portal Folder:
#Host = open('/var/www/html/HostBuilds/MAEVE.txt', "r")
#HostLines = Host.readlines()
#Host.close

#HostIDparts = HostLines[0].split("|")

#HostName = HostIDparts[0]
#HostSex = HostIDparts[1]
#HostAge = HostIDparts[2]
#HostOccupation = HostIDparts[3]
#HostID = HostIDparts[4]

#if HostSex == "M":
#    baseVoice = "D"
#elif HostSex == "F":
#    baseVoice = "B"
#else:
#    baseVoioce = "V"

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

def set_voice(V,T):
    if V == "A":
        os.system("swift -n Allison -o tmp.wav "+T+" && aplay -D plughw:1,0 tmp.wav") 
    if V == "B":
        os.system("swift -n Belle -o tmp.wav "+T+" && aplay -D plughw:1,0 tmp.wav") 
    if V == "C":
        os.system("swift -n Callie -o tmp.wav "+T+" && aplay -D plughw:1,0 tmp.wav") 
    if V == "D":
        os.system("swift -n Dallas -o tmp.wav "+T+" && aplay -D plughw:1,0 tmp.wav") 
    if V == "V":
        os.system("swift -n David -o tmp.wav "+T+" && aplay -D plughw:1,0 tmp.wav") 

pronunciationDict = {'Maeve':'Mayve','Mariposa':'May-reeposah','Lila':'Lie-la','Trump':'Ass hole'}

def adjustResponse(response):     # Adjusts spellings in verbal output string only to create better speech output, things like Maeve and Mariposa
    for key, value in pronunciationDict.items():
        if key in response or key.lower() in response:
            response = re.sub(key, value, response, flags=re.I)
    return response

SpeakText="Speech center connected and online."
set_voice("B",SpeakText) # Cepstral  Voices: A = Allison; B = Belle; C = Callie; D = Dallas; V = David;
print(SpeakText)

while True:
    SpeakText = socket.recv().decode('utf-8') # Get rid of the b' in front of teh string
    SpeakTextX = adjustResponse(SpeakText)    # Run the string through the pronunciation dictionary
    set_voice("B",SpeakTextX)
    print("Received request: %s" % SpeakText)
    socket.send_string(str(SpeakText))  # Send data back to source for confirmation
