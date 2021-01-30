# python SpeechRecognition.py
# Listens for speech, converts it to text and sends it via ZeroMQ port 5555 or 5558

import speech_recognition as sr
import time
import zmq

noiseList = ['up','up up','poop','pope','the pope','pop','duped','Pat','yep','the the','the pop pop','the','uh']

context = zmq.Context()

#print("Connecting to Language Processing")
#socket = context.socket(zmq.REQ)
#socket.connect("tcp://localhost:5558")   #5556 is visual, 5558 is language processor, 5555 is direct to speech

print("Connecting to Speech Center")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")   #5556 is visual, 5558 is language process$

r = sr.Recognizer()
with sr.Microphone() as source:
    print("Calibrating microphone")
    r.adjust_for_ambient_noise(source, duration=4)
    #r.energy_threshold = 2000

keepAwake = 1

SpeakText = "Speech Recognition Online."
socket.send_string(SpeakText)
message = socket.recv()

def main():
    while True:
        print("Ready")
        with sr.Microphone() as source:
            try:
                SpeakText = r.recognize_sphinx(r.listen(source))
            except sr.UnknownValueError:
                #print("U V E")
                SpeakText="" #"What?"
            if SpeakText=="enter a deep and dreamless slumber":
                exit()
            if SpeakText in noiseList:   #split SpeakText//len(SpeakText)//for word in SpeakText if word in noiseList increment count +1// if count = len(speaktext) #(meaning all words are noise) then change SpeakText to BG Noise.
                SpeakText = "" #"I hear background noise"
            if SpeakText != "":
                try:
                    socket.send_string(SpeakText)
                    message = socket.recv(5000)  # Should timeout with EAGAIN error after 20 secs.
                    message = message.decode('utf-8')
                    print("%s " % (message))
                except:
                    message = "Oops, reply lost"
                    print("Received reply %s " % (message))

if keepAwake == 1:
    main()
