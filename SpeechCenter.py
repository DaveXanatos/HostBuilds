# python SpeechCenter.py
# Connects to port 5555 using ZeroMQ, receives speech commands from other scripts

import time
import zmq
import os
import re

# Open Host Behavior Matrix on Server Portal Folder:
Host = open('/var/www/html/HostBuilds/ACTIVEHOST.txt', "r")  # On Host Processor
HostLines = Host.readlines()
Host.close

HostIDparts = HostLines[0].split("|")  # HostLines[0] contains the base self attributes, [1] contains system parameters for OpenCV, etc., [2] - [21] contain the matrix attributes
V = HostIDparts[5]  # Host Voice

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

def set_voice(V,T):
    T = '"' + T + '"'
    audioFile = "/home/pi/Desktop/HOSTCORE/tmp.wav"
    if V == "A":
        os.system("swift -n Allison -o " + audioFile + " " +T+ " && aplay -D plughw:1,0 " + audioFile) 
    if V == "B":
        os.system("swift -n Belle -o " + audioFile + " " +T+ " && aplay -D plughw:1,0 " + audioFile) 
    if V == "C":
        os.system("swift -n Callie -o " + audioFile + " " +T+ " && aplay -D plughw:1,0 " + audioFile) 
    if V == "D":
        os.system("swift -n Dallas -o " + audioFile + " " +T+ " && aplay -D plughw:1,0 " + audioFile) 
    if V == "V":
        os.system("swift -n David -o " + audioFile + " " +T+ " && aplay -D plughw:1,0 " + audioFile) 

pronunciationDict = {'Maeve':'Mayve','Mariposa':'May-reeposah','Lila':'Lie-la','Trump':'Ass hole'}

def adjustResponse(response):     # Adjusts spellings in verbal output string only to create better speech output, things like Maeve and Mariposa
    for key, value in pronunciationDict.items():
        if key in response or key.lower() in response:
            response = re.sub(key, value, response, flags=re.I)
    return response

SpeakText="Speech center connected and online."
set_voice(V,SpeakText) # Cepstral  Voices: A = Allison; B = Belle; C = Callie; D = Dallas; V = David;

while True:
    SpeakText = socket.recv().decode('utf-8') # .decode gets rid of the b' in front of the string
    SpeakTextX = adjustResponse(SpeakText)    # Run the string through the pronunciation dictionary
    set_voice(V,SpeakTextX)
    print("Received request: %s" % SpeakTextX)
    socket.send_string(str(SpeakTextX))        # Send data back to source for confirmation

# Adjusting Voice Speed

# I am now <prosody rate='x-slow'>speaking at half speed.</prosody>
# I am now <prosody rate='slow'>speaking at 2/3 speed.</prosody>
# I am now <prosody rate='medium'>speaking at normal speed.</prosody>
# I am now <prosody rate='fast'>speaking 33% faster.</prosody>
# I am now <prosody rate='x-fast'>speaking twice as fast</prosody>
# I am now <prosody rate='default'>speaking at normal speed.</prosody>
# I am now <prosody rate='.42'>speaking at 42% of normal speed.</prosody>
# I am now <prosody rate='2.8'>speaking 2.8 times as fast</prosody>
# I am now <prosody rate='-0.3'>speaking 30% more slowly.</prosody>
# I am now <prosody rate='+0.3'>speaking 30% faster.</prosody>

# Adjusting Voice Pitch 

# <prosody pitch='x-low'>This is half-pitch</prosody>
# <prosody pitch='low'>This is 3/4 pitch.</prosody>
# <prosody pitch='medium'>This is normal pitch.</prosody>
# <prosody pitch='high'>This is twice as high.</prosody>
# <prosody pitch='x-high'>This is three times as high.</prosody>
# <prosody pitch='default'>This is normal pitch.</prosody>
# <prosody pitch='-50%'>This is 50% lower.</prosody>
# <prosody pitch='+50%'>This is 50% higher.</prosody>
# <prosody pitch='-6st'>This is six semitones lower.</prosody>
# <prosody pitch='+6st'>This is six semitones higher.</prosody>
# <prosody pitch='-25Hz'>This has a pitch mean 25 Hertz lower.</prosody>
# <prosody pitch='+25Hz'>This has a pitch mean 25 Hertz higher.</prosody>
# <prosody pitch='75Hz'>This has a pitch mean of 75 Hertz.</prosody>

# Adjusting Output Volume

# <prosody volume='silent'>This is silent.</prosody>
# <prosody volume='x-soft'>This is 25% as loud.</prosody>
# <prosody volume='soft'>This is 50% as loud.</prosody>
# <prosody volume='medium'>This is the default volume.</prosody>
# <prosody volume='loud'>This is 50% louder.</prosody>
# <prosody volume='x-loud'>This is 100% louder.</prosody>
# <prosody volume='default'>This is the default volume.</prosody>
# <prosody volume='-33%'>This is 33% softer.</prosody>
# <prosody volume='+33%'>This is 33% louder.</prosody>
# <prosody volume='33%'>This is 33% louder.</prosody>
# <prosody volume='33'>This is 33% of normal volume.</prosody>

# Adding Emphasis to Speech

# This is <emphasis level='strong'>stronger</emphasis> than the rest.
# This is <emphasis level='moderate'>stronger</emphasis> than the rest.
# This is <emphasis level='none'>the same as</emphasis> than the rest.

# I can't emphasize enough how <emphasis level='strong'>powerful</emphasis> these new attributes can be  <prosody volume='-90%'>But don't tell anybody</prosody>.


