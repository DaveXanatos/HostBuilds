#!/bin/bash -x

sleep 5
python /home/pi/Desktop/HOSTCORE/SpeechCenter.py &
sleep 12
#python /home/pi/Desktop/HOSTCORE/LanguageProcessor_9b.py &
#sleep 12
python /home/pi/Desktop/HOSTCORE/FaceRecognition.py --cascade /home/pi/Desktop/HOSTCORE/haarcascade_frontalface_default.xml --encodings /home/pi/Desktop/HOSTCORE/encodings.pickle &
sleep 20
#python /home/pi/Desktop/HOSTCORE/SpeechRecognition.py &
#sleep 12
#python /home/pi/Desktop/HOSTCORE/MotorFunctions.py &
#sleep 15
python /home/pi/Desktop/HOSTCORE/SoftSleep.py &
sleep 1

set +x




