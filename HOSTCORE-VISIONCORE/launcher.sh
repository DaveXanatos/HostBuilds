#!/bin/bash -x
# CRITICAL NOTE:  Scripts run from this launcher must use FULL PATH REFERENCES to any
# files referenced WITHIN the script being run, otherwise that script will error out
# for file not found.

sleep 5
/usr/bin/python3 /home/pi/Desktop/HOSTCORE/FaceRecognition.py \
    --cascade /home/pi/Desktop/HOSTCORE/haarcascade_frontalface_default.xml \
    --encodings /home/pi/Desktop/HOSTCORE/encodings.pickle &
sleep 5

/usr/bin/python3 /home/pi/Desktop/HOSTCORE/rtObjD/rtObjD.py \
    --prototxt /home/pi/Desktop/HOSTCORE/rtObjD/MobileNetSSD_deploy.prototxt.txt \
    --model /home/pi/Desktop/HOSTCORE/rtObjD/MobileNetSSD_deploy.caffemodel &
sleep 5

/usr/bin/python3 /home/pi/Desktop/HOSTCORE/SoftSleep.py &
sleep 1

set +x




