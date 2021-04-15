# python SpeechCenter.py
# Binds to port 5555 using ZeroMQ, receives speech commands from other scripts
# and sends jaw movement strings to MotorFunctions on 5554.

import time
import zmq
import os
import re
import wave
import contextlib

# Open Host Behavior Matrix on Server Portal Folder:
Host = open('/var/www/html/HostBuilds/ACTIVEHOST.txt', "r")  # On Host Processor
HostLines = Host.readlines()
Host.close

HostIDparts = HostLines[0].split("|")  # HostLines[0] contains the base self attributes, 
V = HostIDparts[5]  # Host Voice in [5]; [1] = system params for OpenCV, [2] - [21] matrix attributes

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")  #Listens for speech to output

print("Connecting to Motor Control")
jawCmd = context.socket(zmq.PUB)
jawCmd.connect("tcp://192.168.1.210:5554") #Sends to MotorFunctions for Jaw Movement

def getPlayTime():  # Checks to see if current file duration has changed
    fname = '/tmp/speech.wav'   # and if yes, sends new duration
    with contextlib.closing(wave.open(fname,'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = round(frames / float(rate), 3)
        speakTime = str(duration)
        return speakTime

def set_voice(V,T,H):
    T2 = '"' + T + '"'
    audioFile = "/tmp/speech.wav"  # /tmp set as tmpfs, or RAMDISK to reduce SD Card write ops

    if V == "A":
        voice = "Allison"
    elif V == "B":
        voice = "Belle"
    elif V == "C":
        voice = "Callie"
    elif V == "D":
        voice = "Dallas"
    elif V == "V":
        voice = "David"
    else:
        voice = "Belle"

    os.system("swift -n " + voice + " -o " + audioFile + " " +T2) # Record audio
    tailTrim = .5                                                 # Calculate Jaw Timing
    speakTime = eval(getPlayTime())                               # Start by getting playlength
    speakTime = round((speakTime - tailTrim), 2)                             # Chop .5 s for trailing silence
    wordList = T.split()
    jawString = []
    for index in range(len(wordList)):
        wordLen = len(wordList[index])
        jawString.append(wordLen)
    jawString = str(jawString)
    speakTime = str(speakTime)
    jawString = speakTime + "|" + jawString + "|" + H  # 3.456|[4, 2, 7, 4, 2, 9, 3, 4, 3, 6]|('yes', 3, 'no', 8) - will split on "|"
    jawCmd.send_string(jawString)
    os.system("pacmd suspend-source 1 1")  #Mutes Mic
    os.system("aplay " + audioFile)                               # Play audio
    os.system("pacmd suspend-source 1 0")  #Unmutes Mic

pronunciationDict = {'teh':'the','shine':'zhine','shiney':'zhiney','shining':'zhining','process':'prawcess','Maeve':'Mayve','Mariposa':'May-reeposah','Lila':'Lala','Trump':'Ass hole'}

def adjustResponse(response):     # Adjusts spellings in output string to create better speech output.
    for key, value in pronunciationDict.items():
        if key in response or key.lower() in response:
            response = re.sub(key, value, response, flags=re.I)
    return response

def extractCommands(stwc): # Extracts & sends {movement commands} embedded in SpeakText With Commands
    commands = re.findall(r'\{.*?\}', stwc)
    for i in range(len(commands)):
        commands[i] = re.sub(r'\W+', '', str(commands[i]))
    cmdPos = [i+1 for i,w in enumerate(stwc.split()) if "{" in w]
    headString = sum(zip(commands, cmdPos), ())
    print(headString) # Ex. ('yes', 3, 'no', 8) (Dev Only)
    text = re.sub(r'\{[^}]*\}\s', '', stwc)
    return text, headString

SpeakText="Speech center connected and online."
set_voice(V,SpeakText,"()") # Cepstral  Voices: A = Allison; B = Belle; C = Callie; D = Dallas; V = David;

while True:
    SpeakText = socket.recv().decode('utf-8') # .decode gets rid of the b' in front of the string
    SpeakText, headString = extractCommands(SpeakText)
    SpeakTextX = adjustResponse(SpeakText)    # Run the string through the pronunciation dictionary
    print("SpeakText = ",SpeakTextX) # Dev Only
    if headString == "":
        headString = "()"
    set_voice(V,SpeakTextX,str(headString))
    print("Received request: %s" % SpeakTextX) # Dev Only
    socket.send_string(str(SpeakTextX))        # Send data back to source for confirmation

# Combining Parameters:

# NOTE:  Using {} curly braces around words seems to add an emphasis.  Try others.

# This is the usual way, <prosody pitch='low'>unless you want to be a little unconventional,
# in which case</prosody>, <emphasis level='strong'><prosody pitch='+90%'>GO</prosody> for it!</emphasis>
# I can't emphasize enough how <emphasis level='strong'>powerful</emphasis> these new attributes can be,
# <prosody volume='-50%'>But don't tell anybody</prosody>.

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
