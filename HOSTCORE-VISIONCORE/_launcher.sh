#!/bin/bash -x
# CRITICAL NOTE:  Scripts run from this launcher must use FULL PATH REFERENCES to any
# files referenced WITHIN the script being run, otherwise that script will error out
# for file not found.


python /home/pi/Desktop/HOSTCORE/visionBroadcastL.py &
sleep 5
# When run from _launcher.sh, throws error "ImportError: No module named imutils.video", but runs if locally called.

# Try This:
#import sys
#sys.path.append('my/path/to/module/folder')

#import module-of-interest




python /home/pi/Desktop/HOSTCORE/visionBroadcastR.py &
sleep 5

#nohup python /home/pi/Desktop/HOSTCORE/FaceRecognition.py \
#    --cascade /home/pi/Desktop/HOSTCORE/haarcascade_frontalface_default.xml \
#    --encodings /home/pi/Desktop/HOSTCORE/encodings.pickle &
#sleep 20

python /home/pi/Desktop/HOSTCORE/MotorFunctions.py &
#sleep 15

#python /home/pi/Desktop/HOSTCORE/SoftSleep.py &
#sleep 1

#set +x

# python /home/pi/Desktop/HOSTCORE/real-time-object-detection/real_time_object_detection.py \
#    --prototxt MobileNetSSD_deploy.prototxt.txt \
#    --model MobileNetSSD_deploy.caffemodel

# python /home/pi/Desktop/HOSTCORE/human-activity-recognition/human_activity_reco_deque.py \
#    --model resnet-34_kinetics.onnx \
#    --classes action_recognition_kinetics.txt



