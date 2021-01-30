import time
import zmq
import os

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

SpeakText="Speech center online."
set_voice("C",SpeakText) # Cepstral  Voices: A = Allison; B = Belle; C = Callie; D = Dallas; V = David;
print("Host Online running listenecho.py.")

while True:
    SpeakText = socket.recv()
    SpeakText = str(SpeakText)
    SpeakText = SpeakText[1:]
    set_voice("C",SpeakText) # Cepstral  Voices: A = Allison; B = Belle; C = Callie; D = Dallas; V = David;
    print("Received request: %s" % SpeakText)

    #time.sleep(1)  # Do some work here, like speak

    socket.send_string(str(SpeakText))
    



