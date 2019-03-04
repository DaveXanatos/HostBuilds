# python SpeechRecognition.py
# Listens for speech, converts it to text and sends it via ZeroMQ port 5555 or 5558

import speech_recognition as sr
import time
import zmq

context = zmq.Context()

print("Connecting to Speech Center")
socketSDir = context.socket(zmq.REQ)
socketSDir.connect("tcp://localhost:5555") # 5555 direct to speech, announcements, etc

print("Connecting to Speech Center")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5558") # 5558 to language processor

r = sr.Recognizer()
with sr.Microphone() as source:
    print("Calibrating microphone")
    r.adjust_for_ambient_noise(source, duration=2)
    #r.energy_threshold = 2000

keepAwake = 1

SpeakText = "Speech Recognition Online."
socketSDir.send_string(SpeakText)
message = socketSDir.recv()

def main():
    while True:
        print("Ready")
        with sr.Microphone() as source:
            SpeakText = r.recognize_sphinx(r.listen(source))
            SpeakText = SpeakText.replace("'","")  # Apostrophes cause no speech output from SpeechCenter

            #SpeakTextD = "I think I heard, " + SpeakText + "."
            #socketSDir.send_string(SpeakTextD)
            #messageD = socketSDir.recv()

            try:
                socket.send_string(SpeakText)
                message = socket.recv(20000)  # Should timeout with EAGAIN error after 20 secs.
                print("Received reply %s " % (message))
            except:
                message = "Oops, reply lost"
                print("Received reply %s " % (message))

if keepAwake == 1:
    main()
