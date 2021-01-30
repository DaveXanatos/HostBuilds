#!/bin/bash -x
# CRITICAL NOTE:  Scripts run from this launcher must use FULL PATH REFERENCES to any
# files referenced WITHIN the script being run, otherwise that script will error out
# for file not found.

sleep 10  # Just giving time for other stuff to settle in.
/usr/bin/python3 /home/pi/Desktop/HOSTCORE/SpeechCenter.py &
#Listens (binds) to :5555 for speech to output
sleep 5

lxterminal -e /usr/bin/python3 /home/pi/Desktop/HOSTCORE/visionCommandTest.py
#Talks to :5555 for speech to output
sleep 5

/usr/bin/python3 /home/pi/Desktop/HOSTCORE/SpeechRecognition.py 2> /dev/null &
#Connects to :5558 to send speech for processing (:5555 for testing)
sleep 5

lxterminal -e /usr/bin/python3 /home/pi/Desktop/HOSTCORE/LanguageProcessor-1.py &>/tmp/LPError.txt
#Binds to :5558 and listens for speech utterance from SR to process, 
#connects to :5555 to output responses as speech
sleep 5

#python /home/pi/Desktop/HOSTCORE/VoiceID.py &
#sleep 15

python /home/pi/Desktop/HOSTCORE/SoftSleep.py &
sleep 1

set +x




