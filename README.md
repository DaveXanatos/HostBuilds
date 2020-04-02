# HostBuilds
Initial Repository for Host Builds.  These are very lifelike humanoid robot builds designed to look, move, interact, speak and respond in as human-like fashion as possible.

This repository works directly with the Behavior Pad Interface I created at https://github.com/DaveXanatos/Westworld-Style-Behavior-Pad-Interface  Note that while the interface has MANY "Westworld" hosts in it for fun... the one that works with the system here is the host called Base Host, which can be accessed by the selector in the interface's upper-right box.  The other hosts are for fun and fans only.

Non-proprietary files here only - LanguageProcessor.py contains very sophisticated code that outperforms everything available to date, and until I determine how to protect my work on this it'll have to remain offline.

These scripts are built on top of many dependencies and are Python 3.5 and up.  My build distro is Debian (Raspbian) Stretch (currently).  PyZMQ (ZeroMQ) is required for the scripts to send data between each other. 0MQ ROCKS!

SpeechCenter requires Cepstral Voices (licenses must e purchased) Belle, Allison, David, Dallas and a few others.  But it would work just as well with eSpeak or the T2S engine of your choice.  I chose Cepstral because the voices are the least robotic and have some character.  Belle and Dallas have southern accents!

Speech Recognition is built on the Python SpeechRecognition package, and you must have CMUSphinx and PocketSphinx installed, along with the Python Packages.  You also need to know how to configure audio sources in your distro.

LanguageProcessor is filled to the brim with dependencies including NLTK, BERT, Python RexExps, and a bunch of stuff I've created to both extend and fix the limitations and shortcomings of the initial packages I used.  Its performance, while still not indistinguishable from a human, is superior to anything else I've seen demonstrated anywhere on the web or tradeshows.  Watch for links to YouTube videos when I finish this part off.

FaceRecognition requires OpenCV and is based on the initial work of Adrian Rosebock (https://www.pyimagesearch.com/author/adrian/).  I've modified it extensively to publish video frames and send data out about face center positioning (made available to the MotorFunctions script for eyeball and head/neck positioning, etc.) and who has been recognized, etc.

MotorFunctions does just what you'd think... it basically controls banks of 16 channel I2C controlled servo controllers, with custom code for fluidic, lifelike movement.

VoiceID is speaker diarization loosely based on PyWho.

SoftSleep is a hardware orderly shutdown button implemented through GPIO so if I need to shut down in the event of a loss of comm connectivity, or when the robots are operating autonomously and I cannot connect for some reason, I still have the ability to perform a non-hazardous shutdown (one that doesn't risk corruption of the disk image).

This is a work in progress, but it is an amazing one.  Thanks for watching.  Progress may be slow at times, but, as Belle would say, My Goodness what an interesting thing you have there! :)

