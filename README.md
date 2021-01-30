# HostBuilds
Initial Repository for Robotic Host Builds.  These are very lifelike humanoid robot builds designed to look, move, interact, speak and respond in as human-like fashion as possible.

These robots have at their core (literally in their head) a cluster of three Raspberry Pi SBCs.  One of which is an R Pi CM3 mounted on a StereoPi carrier board; the other two are Raspberry Pi 4B 8 gig.  The CM3 is currently running Raspbian Buster, the two Pi 4Bs are running Raspbian OS 64 bit.  This is required for full leveraging of large model applications such as GPT-2 whose 774M and 1558M models are larger than a 32 bit OS can handle (in other words, 2GB).

Review HostBlockDiagram.jpg to see the core architecture.  The three primary nodes communicate via ZMQ.

VISIONACQUISITION acquires video frames from each eyeball and broadcasts them via ImageZMQ to all nodes for processing and action depending on what the hosts see.

VISIONCORE handles things like face detection, recognition, and tracking, as well as object detection, recognition and tracking.

LANGUAGECORE handles speech recognition (StT), speech output (TtS) using Cepstral Voices (not archived here due to file sizes - but they are much better than most anything I've found that's free.  I have licensed five voices: Allison, Belle, Callie, Dallas & David.  The licenses for Raspberry Pi users in a non-commercial/resale environment are $35.00 each and I highly recommend them.)

This repository works directly with the Behavior Pad Interface (BPI) I created at https://github.com/DaveXanatos/Westworld-Style-Behavior-Pad-Interface  Note that while the interface has MANY "Westworld" hosts in it for fun... the one that works with the system here is the host called Base Host, which can be accessed by the selector in the interface's upper-right box.  The BPI edits and stores configuration values that determine the voice used by the host, and certain parameters that have an effect on how the host uses and interprets language.  It does this by writing to a file called ACTIVEHOST.txt, which is just a flat-file pipe-delimited datafile that is read and parsed by several scripts, such as SpeechCenter.py, LanguageProcessor.py and others. 

Non-proprietary files here only - LanguageProcessor.py contains very sophisticated code that outperforms everything available to date, and until I determine how to protect my work on this it'll have to remain offline.  Updates as of April 2020 include leveraging GPT-2 to create even more human-esque speech :)

These scripts are built on top of many dependencies and are Python 3.7.3 and up.  

Speech Recognition is built on the Python SpeechRecognition package, and you must have CMUSphinx and PocketSphinx installed, along with the Python Packages.  You also need to know how to configure audio sources in your distro.

LanguageProcessor is filled to the brim with dependencies including NLTK, BERT, Python RexExps, GPT-2 and a bunch of stuff I've created to both extend and fix the limitations and shortcomings of the initial packages I used.  Its performance, while still not indistinguishable from a human, is superior to anything else I've seen demonstrated anywhere on the web or tradeshows.  Watch for links to YouTube videos when I finish this part off.

FaceRecognition requires OpenCV and is based on the initial work of Adrian Rosebock (https://www.pyimagesearch.com/author/adrian/).  I've modified it extensively to publish video frames and send data out about face center positioning (made available to the MotorFunctions script for eyeball and head/neck positioning, etc.) and who has been recognized, etc.

MotorFunctions does just what you'd think... it basically controls banks of 16 channel I2C controlled servo controllers, with custom code for fluidic, lifelike movement.

VoiceID is speaker diarization loosely based on PyWho.

SoftSleep is a hardware orderly shutdown button implemented through GPIO so if I need to shut down in the event of a loss of comm connectivity, or when the robots are operating autonomously and I cannot connect for some reason, I still have the ability to perform a non-hazardous shutdown (one that doesn't risk corruption of the disk image).

This is a work in progress, but it is an amazing one.  Thanks for watching.  Progress may be slow at times, but, as Belle would say, My Goodness what an interesting thing you have there! :)

