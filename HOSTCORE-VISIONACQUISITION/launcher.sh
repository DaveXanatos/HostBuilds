#!/bin/bash -x
# CRITICAL NOTE:  Scripts run from this launcher must use FULL PATH REFERENCES to any
# files referenced WITHIN the script being run, otherwise that script will error out
# for file not found.

sleep 10  # Just giving time for other stuff to settle in.
/usr/bin/python3 /home/pi/Desktop/HOSTCORE/visionBroadcastLJ.py &
sleep 5
/usr/bin/python3 /home/pi/Desktop/HOSTCORE/visionBroadcastRJ.py &
sleep 5

/usr/bin/python3 /home/pi/Desktop/HOSTCORE/MotorFunctions-Visual.py &
sleep 10

lxterminal -e /usr/bin/python3  /home/pi/Desktop/HOSTCORE/Orientation.py
sleep 3

/usr/bin/python3 /home/pi/Desktop/HOSTCORE/SoftSleep.py &
sleep 1

# python3 /home/pi/Desktop/HOSTCORE/real-time-object-detection/real_time_object_detection.py \
#    --prototxt MobileNetSSD_deploy.prototxt.txt \
#    --model MobileNetSSD_deploy.caffemodel

# python3 /home/pi/Desktop/HOSTCORE/human-activity-recognition/human_activity_reco_deque.py \
#    --model resnet-34_kinetics.onnx \
#    --classes action_recognition_kinetics.txt

set +x

