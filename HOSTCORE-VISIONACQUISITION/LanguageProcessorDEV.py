#!/usr/bin/python

# ***************** IMPORT ALL REQUIRED DEPENDENCIES ******************************
from difflib import SequenceMatcher as SM
import nltk
from nltk.tag import pos_tag
import calendar
import datetime
import random
import time
import zmq
import os
import re

# ***************** SETUP NETWORKING *******************************
context = zmq.Context()

print("Establishing Language Network Node")
socketL = context.socket(zmq.REP)
socketL.bind("tcp://*:5558")

print("Connecting to Speech Center")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555") # 5555 direct to speech, 5558 to lang proc

SpeakText = "Language Processing Online."
socket.send_string(SpeakText)
message = socket.recv()

# ***************** SET OR READ IN ALL "IN-HEAD" BASE KNOWLEDGE REFERENCES *******
dictInitWords={  # Determine from 1st two words if likely a Question (1), Indeterminate (2), Statement (3), or Invalid (4) (System later adds a 5 if not found here, 6 if 'there is/are/was/will (be)/were/can/cant' etc)
    'who':{'were':1,'was':1,'will':1,'is':1,'are':1,'his':3,'her':3,'their':3,'my':3,'our':3,'your':3,'its':3,'i':3,'you':3,'we':3,'they':3,'it':3,'there':3,'that':2,'the':2,'in':2,'can':1,'cant':1,'cannot':1,'am':1,'do':4,'did':1,'does':1},
    'what':{'were':1,'was':1,'will':1,'is':1,'are':1,'his':3,'her':3,'their':3,'my':3,'our':3,'your':3,'its':3,'i':3,'you':3,'we':3,'they':3,'it':3,'there':3,'that':3,'the':2,'in':1,'can':1,'cant':1,'cannot':1,'am':1,'do':1,'did':1,'does':1},
    'why':{'were':1,'was':1,'will':1,'is':1,'are':1,'his':3,'her':3,'their':3,'my':3,'our':3,'your':3,'its':3,'i':3,'you':3,'we':3,'they':3,'it':3,'there':3,'that':3,'the':2,'in':2,'can':1,'cant':1,'cannot':1,'am':1,'do':1,'did':1,'does':1},
    'where':{'were':1,'was':1,'will':1,'is':1,'are':1,'his':3,'her':3,'their':3,'my':3,'our':3,'your':3,'its':3,'i':3,'you':3,'we':3,'they':3,'it':3,'there':3,'that':3,'the':2,'in':1,'can':1,'cant':1,'cannot':1,'am':1,'do':1,'did':1,'does':1},
    'when':{'were':1,'was':1,'will':1,'is':1,'are':1,'his':3,'her':3,'their':3,'my':3,'our':3,'your':3,'its':3,'i':3,'you':3,'we':3,'they':3,'it':3,'there':3,'that':3,'the':2,'in':2,'can':1,'cant':1,'cannot':1,'am':1,'do':1,'did':1,'does':1},
    'how':{'were':1,'was':1,'will':1,'is':1,'are':1,'his':3,'her':3,'their':3,'my':3,'our':3,'your':3,'its':3,'i':3,'you':3,'we':3,'they':3,'it':3,'there':3,'that':3,'the':2,'in':2,'can':1,'cant':1,'cannot':1,'am':1,'do':1,'did':1,'does':1},
    'have':{'were':4,'was':4,'will':4,'is':4,'are':4,'his':2,'her':2,'their':2,'my':2,'our':2,'your':2,'its':2,'i':1,'you':1,'we':1,'they':1,'it':3,'there':1,'that':3,'the':1,'in':1,'can':4,'cant':4,'cannot':4,'am':4,'do':4,'did':4,'does':4},
    'has':{'were':4,'was':4,'will':4,'is':4,'are':4,'his':1,'her':1,'their':1,'my':1,'our':1,'your':1,'its':1,'i':4,'you':4,'we':4,'they':4,'it':1,'there':1,'that':1,'the':1,'in':1,'can':4,'cant':4,'cannot':4,'am':4,'do':4,'did':4,'does':4},
    'can':{'were':4,'was':4,'will':4,'is':4,'are':4,'his':1,'her':1,'their':1,'my':1,'our':1,'your':1,'its':1,'i':1,'you':1,'we':1,'they':1,'it':1,'there':1,'that':1,'the':1,'in':1,'can':4,'cant':4,'cannot':4,'am':4,'do':4,'did':4,'does':4},
    'cant':{'were':4,'was':4,'will':4,'is':4,'are':4,'his':1,'her':1,'their':1,'my':1,'our':1,'your':1,'its':1,'i':1,'you':1,'we':1,'they':1,'it':1,'there':1,'that':1,'the':1,'in':1,'can':4,'cant':4,'cannot':4,'am':4,'do':5,'did':4,'does':4},
    'do':{'were':4,'was':4,'will':4,'is':4,'are':4,'his':1,'her':1,'their':1,'my':1,'our':1,'your':1,'its':1,'i':1,'you':1,'we':1,'they':1,'it':1,'there':4,'that':2,'the':1,'in':1,'can':4,'cant':4,'cannot':4,'am':4,'do':4,'did':4,'does':4},
    'does':{'were':4,'was':4,'will':4,'is':4,'are':4,'his':1,'her':1,'their':1,'my':1,'our':1,'your':1,'its':1,'i':4,'you':4,'we':4,'they':4,'it':1,'there':4,'that':1,'the':1,'in':1,'can':4,'cant':4,'cannot':4,'am':4,'do':4,'did':4,'does':4},
    'did':{'were':4,'was':4,'will':4,'is':4,'are':4,'his':1,'her':1,'their':1,'my':1,'our':1,'your':1,'its':1,'i':1,'you':1,'we':1,'they':1,'it':1,'there':1,'that':1,'the':1,'in':1,'can':4,'cant':4,'cannot':4,'am':4,'do':3,'did':4,'does':4},
    'will':{'were':4,'was':4,'will':4,'is':4,'are':4,'his':1,'her':1,'their':1,'my':1,'our':1,'your':1,'its':1,'i':1,'you':1,'we':1,'they':1,'it':1,'there':1,'that':1,'the':1,'in':4,'can':4,'cant':4,'cannot':4,'am':4,'do':3,'did':4,'does':4},
    'are':{'were':4,'was':4,'will':4,'is':4,'are':4,'his':1,'her':1,'their':1,'my':1,'our':1,'your':1,'its':1,'i':4,'you':1,'we':1,'they':1,'it':4,'there':1,'that':4,'the':1,'in':4,'can':4,'cant':4,'cannot':4,'am':4,'do':4,'did':4,'does':4},
    'am':{'were':4,'was':4,'will':4,'is':4,'are':4,'his':4,'her':4,'their':4,'my':4,'our':4,'your':4,'its':4,'i':1,'you':4,'we':4,'they':4,'it':4,'there':4,'that':4,'the':4,'in':4,'can':4,'cant':4,'cannot':4,'am':4,'do':4,'did':4,'does':4},
    'is':{'were':4,'was':4,'will':4,'is':4,'are':4,'his':1,'her':1,'their':1,'my':1,'our':1,'your':1,'its':1,'i':4,'you':4,'we':4,'they':4,'it':1,'there':1,'that':1,'the':1,'in':1,'can':4,'cant':4,'cannot':4,'am':4,'do':4,'did':4,'does':4},
    'was':{'were':4,'was':4,'will':4,'is':4,'are':4,'his':1,'her':1,'their':1,'my':1,'our':1,'your':1,'its':1,'i':1,'you':4,'we':4,'they':4,'it':1,'there':1,'that':1,'the':1,'in':1,'can':4,'cant':4,'cannot':4,'am':4,'do':4,'did':4,'does':4},
    'were':{'were':4,'was':4,'will':4,'is':4,'are':4,'his':2,'her':2,'their':2,'my':2,'our':2,'your':2,'its':2,'i':2,'you':2,'we':2,'they':2,'it':2,'there':2,'that':3,'the':2,'in':4,'can':4,'cant':4,'cannot':4,'am':4,'do':4,'did':4,'does':4},
    'if':{'were':4,'was':4,'will':4,'is':4,'are':4,'his':2,'her':2,'their':2,'my':2,'our':2,'your':2,'its':2,'i':2,'you':2,'we':2,'they':2,'it':2,'there':3,'that':2,'the':2,'in':2,'can':4,'cant':4,'cannot':4,'am':4,'do':4,'did':4,'does':4},
    'shall':{'were':4,'was':4,'will':4,'is':4,'are':4,'his':2,'her':2,'their':2,'my':2,'our':2,'your':2,'its':2,'i':2,'you':2,'we':2,'they':2,'it':2,'there':2,'that':2,'the':2,'in':4,'can':4,'cant':4,'cannot':4,'am':4,'do':3,'did':4,'does':4},
    'should':{'were':4,'was':4,'will':4,'is':4,'are':4,'his':2,'her':2,'their':2,'my':2,'our':2,'your':2,'its':2,'i':2,'you':2,'we':2,'they':2,'it':2,'there':2,'that':2,'the':2,'in':2,'can':4,'cant':4,'cannot':4,'am':4,'do':3,'did':4,'does':4},
    'would':{'were':4,'was':4,'will':4,'is':4,'are':4,'his':2,'her':2,'their':2,'my':2,'our':2,'your':2,'its':2,'i':2,'you':2,'we':2,'they':2,'it':2,'there':2,'that':2,'the':2,'in':2,'can':4,'cant':4,'cannot':4,'am':4,'do':3,'did':4,'does':4},
    'could':{'were':4,'was':4,'will':4,'is':4,'are':4,'his':2,'her':2,'their':2,'my':2,'our':2,'your':2,'its':2,'i':2,'you':2,'we':2,'they':2,'it':2,'there':2,'that':1,'the':2,'in':2,'can':4,'cant':4,'cannot':4,'am':4,'do':3,'did':4,'does':4},
    'which':{'were':1,'was':1,'will':1,'is':1,'are':1,'his':3,'her':3,'their':3,'my':3,'our':3,'your':3,'its':3,'i':3,'you':3,'we':3,'they':3,'it':3,'there':3,'that':2,'the':2,'in':2,'can':2,'cant':2,'cannot':2,'am':4,'do':2,'did':1,'does':2},
    'may':{'were':4,'was':3,'will':1,'is':1,'are':4,'his':2,'her':2,'their':2,'my':2,'our':2,'your':2,'its':2,'i':2,'you':2,'we':2,'they':2,'it':2,'there':2,'that':2,'the':2,'in':2,'can':2,'cant':2,'cannot':2,'am':4,'do':4,'did':4,'does':3},
    'might':{'were':4,'was':3,'will':3,'is':3,'are':4,'his':2,'her':2,'their':2,'my':2,'our':2,'your':2,'its':2,'i':2,'you':2,'we':2,'they':2,'it':2,'there':2,'that':2,'the':2,'in':2,'can':3,'cant':3,'cannot':3,'am':4,'do':4,'did':4,'does':3},
    'in':{'were':4,'was':4,'will':4,'is':4,'are':4,'his':2,'her':2,'their':2,'my':2,'our':2,'your':2,'its':2,'i':4,'you':3,'we':2,'they':2,'it':3,'there':2,'that':2,'the':2,'in':4,'can':4,'cant':4,'cannot':4,'am':4,'do':4,'did':4,'does':4},
    'at':{'were':4,'was':4,'will':2,'is':4,'are':4,'his':2,'her':2,'their':2,'my':2,'our':2,'your':2,'its':2,'i':4,'you':2,'we':4,'they':4,'it':3,'there':4,'that':2,'the':2,'in':4,'can':4,'cant':4,'cannot':4,'am':4,'do':4,'did':4,'does':4},
    'to':{'were':4,'was':4,'will':4,'is':4,'are':4,'his':2,'her':2,'their':2,'my':2,'our':2,'your':2,'its':2,'i':4,'you':3,'we':4,'they':4,'it':3,'there':3,'that':2,'the':2,'in':4,'can':4,'cant':4,'cannot':4,'am':4,'do':3,'did':4,'does':4},
    'from':{'were':4,'was':4,'will':2,'is':4,'are':4,'his':2,'her':2,'their':2,'my':2,'our':2,'your':2,'its':2,'i':4,'you':2,'we':4,'they':4,'it':2,'there':2,'that':2,'the':2,'in':2,'can':4,'cant':4,'cannot':4,'am':4,'do':2,'did':4,'does':4},
    'on':{'were':4,'was':4,'will':4,'is':4,'are':4,'his':2,'her':2,'their':2,'my':2,'our':2,'your':2,'its':2,'i':4,'you':3,'we':4,'they':4,'it':3,'there':3,'that':2,'the':2,'in':4,'can':4,'cant':4,'cannot':4,'am':4,'do':4,'did':4,'does':4},
    'under':{'were':4,'was':4,'will':4,'is':4,'are':4,'his':3,'her':3,'their':3,'my':3,'our':3,'your':3,'its':3,'i':4,'you':3,'we':2,'they':2,'it':2,'there':3,'that':2,'the':2,'in':4,'can':4,'cant':4,'cannot':4,'am':4,'do':4,'did':4,'does':4},
    'over':{'were':4,'was':4,'will':4,'is':4,'are':4,'his':3,'her':3,'their':3,'my':3,'our':3,'your':3,'its':3,'i':4,'you':3,'we':2,'they':2,'it':2,'there':3,'that':3,'the':2,'in':2,'can':4,'cant':4,'cannot':4,'am':4,'do':2,'did':4,'does':2},
    'there':{'were':6,'was':6,'will':6,'is':6,'are':6,'his':3,'her':3,'their':3,'my':3,'our':3,'your':3,'its':3,'i':2,'you':3,'we':3,'they':3,'it':3,'there':5,'that':3,'the':3,'in':3,'can':6,'cant':6,'cannot':6,'am':4,'do':3,'did':3,'does':3,'shall':6,'wont':6},
    'WNNP':{'were':2,'was':2,'will':2,'is':2,'are':4,'his':2,'her':2,'their':2,'my':2,'our':3,'your':3,'its':3,'i':2,'you':3,'we':2,'they':2,'it':2,'there':2,'that':2,'the':2,'in':4,'can':3,'cant':3,'cannot':3,'am':4,'do':4,'did':3,'does':2},
}

file_name = 'namesKnown.txt'   # In prep to allow new names to be learned and written to text list for premanent retention
propNouns = {}
with open(file_name) as file:
    for line in file:
        line = line.replace('\n','')
        pairs = line.split(":")
        propNouns.update(zip(pairs[0::2], pairs[1::2]))

curses = ['fuck','fucking','fucked','shit','shitted','shitting','shitwad','shitty','cunt','cunty','cuntwad','pussy','twat','prick','cock','cocksucker','cocksmoker','asshole','shithole','fucknut','fucktard','dickhead','fag','faggot']

slurs = ['gook','honkey','nigger','sandnigger','spic','wop','kike','coon','jap','wetback','kraut','krout']

introduction_words = ["id like you to meet","allow me to introduce","let me introduce","please meet","here is my friend","this is my friend","say hello to","say hi to"]

embargoed_words = ["core code","base code","host code"]

def doLookup(): # HostDict.txt, word|POS|Definition|Animacy Code
    dictFile = open('RESOURCES/LANGFILES/HostDict.txt')
    dictLines = dictFile.readlines()
    dictFile.close
    dictLines = [x.strip() for x in dictLines] 
    return dictLines

dictionary = doLookup()     # Reads dictionary into memory for faster review later, so dictionary contains dictLines

# ***************** CREATE HOST'S BASE CONCEPT OF SELF WITH BLANK Self.class() ***********************************************************************
class Self():     # Create hosts concept of "Self/Me"
    def __init__(self, fName, lName, sex, age, job, IDNo, voice, hColor, eColor, race, homeTown, homeState, homePlanet, whatIAm, whatILike, whatIHave):
        self.fName = fName
        self.lName = lName
        self.sex = sex
        self.age = age
        self.job = job
        self.IDNo = IDNo
        self.voice = voice
        self.hColor = hColor
        self.eColor = eColor
        self.race = race
        self.homeTown = homeTown
        self.homeState = homeState
        self.homePlanet = homePlanet
        self.whatIAm = whatIAm  # 'i am a '  host, robot, computer, machine
        self.whatILike = whatILike # 'i like '  the tv show westworld, the tv show outlander, warm sunny weather, good health, a full battery, to have lots of money...
        self.whatIHave = whatIHave
    def getFullName(self):
        fullName = str(self.fName) + ' ' + str(self.lName)
        return fullName.title()

# Open Host Behavior Matrix on Server Portal Folder:
Host = open('/var/www/html/HostBuilds/ACTIVEHOST.txt', "r")  # On Host Processor
HostLines = Host.readlines()
Host.close

HostIDparts = HostLines[0].split("|")  # HostLines[0] contains the base self attributes, [1] contains system parameters for OpenCV, etc., [2] - [21] contain the matrix attributes
HostName = HostIDparts[0].split(" ")
HostFName = HostName[0]
HostLName = HostName[1]
HostSex = HostIDparts[1]
HostAge = HostIDparts[2]
HostJob = HostIDparts[3]
HostID = HostIDparts[4]
HostVoice = HostIDparts[5]
HostHair = HostIDparts[6]
HostEyes = HostIDparts[7]
HostRace = HostIDparts[8]
HostTown = HostIDparts[9]
HostState = HostIDparts[10]
HostPlanet = HostIDparts[11]
HostIs = HostIDparts[12]
HostLike = HostIDparts[13]
HostHas = HostIDparts[14]

mySelf = Self(HostFName,HostLName,HostSex,HostAge,HostJob,HostID,HostVoice,HostHair,HostEyes,HostRace,HostTown,HostState,HostPlanet,HostIs,HostLike,HostHas)
#       def __init__(self, fName, lName, DoB, job, IDNo, voice, hColor, eColor, sex, homeTown, homeState, homePlanet, whatIAm, whatILike, whatIHave):  Reference in code as mySelf.attribName 

coreDrives = ["master understanding English and be able to talk with humans comfortably",
              "learn to see and recognize people and things, and remember them",
              "learn to associate hearing a person speak with that person's face and remember the conversations I've had with them"]

def getWhen():
    currenttime = datetime.datetime.now()
    dateStamp = str(datetime.date.today().strftime("%Y%m%d"))
    timeStamp = str("%s%s%s" % (currenttime.hour, currenttime.minute, currenttime.second))
    return currenttime, dateStamp, timeStamp

# Wake up, check the time:
currenttime, dateStamp, timeStamp = getWhen()

def dayPart(hour):
    if hour < 12:
        dayPart = "morning"
    elif hour > 11 and hour < 18:
        dayPart = "afternoon"
    elif hour > 17:
        dayPart = "evening"
    return dayPart

# ***************** CORE LANGUAGE FUNCTIONS FOR PROCESSING HEARD SPEECH *************************************************************

def checkReply(reply):
    replyVal = 0
    for key, value in responsePolarities.items():
        if key in reply:
            replyVal = value
    return replyVal
    
def checkDict(checkWord):                  # word|POS|def|Anim
    for line in dictionary:                #  0    1   2   3
        thisLine = line.split("|")
        if len(thisLine) > 2:
            if thisLine[0] == checkWord:
                return thisLine[2]
    return ""

def whatIsA(statement, sentenceParts):     # What is/are (a(n)) <ball> --> 1st two = what, is? third = a(n), get word (4th), check core-wordnet.txt for word, if found, be sure 1st line starts with 'n', get txt after last ']', return
    response = ""                          # If multiple lines, add phrase "depends on context, it can mean either D1 or D2"
    sLen = len(sentenceParts)
    checkWord = ""
    found = ""
    try:
        if sentenceParts:
            if sLen == 3:
                try:
                    if sentenceParts[0][0] == "what" and sentenceParts[1][0] == "are":  # Need a "what is" for 3 word:  what is time; what is love; what is fusion.
                        if sentenceParts[2][0].endswith('s'):
                            if sentenceParts[2][0].endswith('s'):
                                checkWord = sentenceParts[2][0]
                                checkWord = checkWord[:-1]
                                found = checkDict(checkWord)
                            if sentenceParts[2][0].endswith('es') and found == "":  # If no find w/o "s" then try w/o "es"
                                checkWord = sentenceParts[2][0]
                                checkWord = checkWord[:-2]
                                found = checkDict(checkWord)
                            if sentenceParts[2][0].endswith('ies') and found == "":  # If no find w/o "es" then try w/o "ies" and a "y" instead
                                checkWord = sentenceParts[2][0]
                                checkWord = checkWord[:-3] + "y"
                                found = checkDict(checkWord)
                            elif found == "":
                                checkWord = sentenceParts[2][0]
                        else:
                            checkWord = sentenceParts[2][0]
                        if found != "":
                            if found[0] in ['a','e','i','o','u']:
                                joiner = "an"
                            else:
                                joiner = "a"
                            response = sentenceParts[2][0].title() + " are " + joiner + " " + found
                            return response
                        else:
                            for line in dictionary:
                                thisLine = line.split("|")
                                if len(thisLine) > 2:
                                    if thisLine[0] == checkWord:
                                        if checkWord[0] in ['a','e','i','o','u']:
                                            joiner = "an"
                                        else:
                                            joiner = "a"
                                        response = sentenceParts[2][0].title() + " are " + thisLine[2].rstrip() + "."
                                        return response
                                else:
                                    return ""
                except KeyError:
                    return ""
                except AttributeError:
                    return ""
            elif sLen > 3:
                try:
                    if sentenceParts[0][0] == "what" and sentenceParts[1][0] == "is" and (sentenceParts[2][0] == "a" or sentenceParts[2][0] == "an"):
                        for line in dictionary:
                            thisLine = line.split("|")
                            if len(thisLine) > 2:
                                if thisLine[0] == sentenceParts[3][0]:
                                    if thisLine[2][0] in ['a','e','i','o','u']:
                                        joiner = "an"
                                    else:
                                        joiner = "a"
                                    response = sentenceParts[2][0].title() + " " + sentenceParts[3][0] + " is " + joiner + " " + thisLine[2].rstrip() + "."
                                    return response
                            else:
                                return ""
                except KeyError:
                    return ""
                except AttributeError:
                    return ""
    except KeyError:
        return ""
    except AttributeError:
        return ""

def doPropNouns(statement):                # Capitalizes Proper Nouns (well, the 340+ that are in the list) so NLTK can see them as such.
    theseWords = statement.split(" ")      # NEW:  Will also return the gender (M, F or N) of the name, for use in my Neural Coreference Resolution System
    n = []                                 # So that if I say "Dave is a cool programmer" then I say "What is he", the system knows "he" = "Dave"
    i = 0
    nameList = []
    genderList = []
    for word in theseWords:
        gData = propNouns.get(word.title(),"X")
        if gData != "X":
            if i == 0:    # If word in propNouns list AND if it's the first word in the utterance, capitalize it
                n.append(word.title())
                nameList.append(word.title())
                genderList.append(gData)
            if i > 0:
                if theseWords[i-1] in ['a','the','this','that','my','your','they','their','his','her','our','there','he','she']: # Prevents capitalization when NOT actually a proper noun (the mark, a jack, the will, etc.  NOT FOOLPROOF...)
                    n.append(word)
                else:
                    n.append(word.title())
                    nameList.append(word.title())
                    genderList.append(gData)
        else:
            n.append(word)
        i+=1
    return " ".join(n), nameList, genderList

def getRefText(file2use):
    quoteFile = open(file2use)
    quoteLines = quoteFile.readlines()
    quoteFile.close
    return quoteLines

#sents = getRefText("LITARCH/quotext.txt")
sents = getRefText("RESOURCES/LANGFILES/disambig.txt")

def disAmbiguate(query):    # Checks for simple informational questions like time, date, weather
    assocFound = ""
    for testSent in sents:
        thisQuery = testSent.split("|")
        assocMatch = SM(None, thisQuery[0], query)
        AMR = assocMatch.ratio()
        if AMR > 0.90:      # This parameter can be a setting in the BPI Matrix (0 = 100%; 100 = maybe 80%, call it match play)
            assocFound = thisQuery[1].rstrip()
    if len(assocFound) > 1:
        #print("DA returns " + assocFound)
        return assocFound   # Returns the reworded "standardized" question (ie., what's it like out --> what is the weather)
    else:
        return "DLLATM"

def disAmbResponse(disAmbig):
    if disAmbig == "what time is it":
        response = "Its " + str(time.strftime("%I %M %p"))
    elif disAmbig == "what is the date":
        response = "Its " + str(datetime.date.today().strftime("%A, %B %d"))
    elif disAmbig == "what is the weather":
        response = "Its warm out, about 85, and mostly clear"
    elif disAmbig == "what is your name":
        response = "My name is " + mySelf.fName.title() + "."
    elif disAmbig == "what do you do":                     #What do you do bombs because do is replaced by getting roSent
        response = "I work as a " + mySelf.job.title() + "."
    elif disAmbig == "what are you":
        response = "Im a " + mySelf.whatIAm + "."
    else:
        response = "DLLATM"
    return response

convLines = []  # First line is timestamp of conversational instance beginning

def comprehendConv():   # Currently just returns word with highest count, filtered for a, the, an, etc.  Will return highest and ratio of word to # lines in convLines; threshold for "=", "fuzzy", "indeterminate"
    wordstring = re.sub('[\[\]\,\']', '', str(convLines))
    stopwords = ['what','who','why','when','how','where','is','a','an','as','and','at','he','she','it','its','the','teh','this','that','there','their','my','our','i','your','our','for','to','in','on','can','about','do','so','have','are','if','be','let','lets']
    wordlist = wordstring.split()
    resultwords  = [word for word in wordlist if word.lower() not in stopwords]
    wordfreq = [resultwords.count(w) for w in resultwords]  # a list comprehension
    keys = resultwords
    values = wordfreq
    dictionary = dict(zip(keys, values))
    print(dictionary)
    cAbout = max(dictionary, key=lambda key: dictionary[key])
    response = "I think this conversation has been about '" + cAbout + "'."
    return response
 
def checkPhrase(query):          # CONVERSATIONAL MEMORY:  Check for similar current statements to previous statements
    AMR = 0                      # Also check for context words:  MATH, etc., so that current queries can be contextualized
    for testSent in convLines:
        thisQuery = testSent.split("|")
        assocMatch = SM(None, thisQuery[0], query)
        thisAMR = assocMatch.ratio()
        if thisAMR > AMR:
            AMR = thisAMR
    line2add = query  # + "|" + respLine
    convLines.insert(0,line2add)
    return AMR

def getSentenceType(statement):  # Checks first two words against grid to determine if question or statement - need to then check third word & get subsequent phrase
    sentenceParts = pos_tag(statement.split())   # **** ToDo: Find the conjunctions that split the clauses and combine the second.
    sLen = len(sentenceParts)
    sVal = ""
    analErr = ""
    try:
        if sentenceParts:
            if sLen > 2:
                try:
                    sVal = dictInitWords[sentenceParts[0][0]][sentenceParts[1][0]]
                    return sVal, sLen, sentenceParts, analErr
                except KeyError:
                    analErr = analErr + " KeyError"
                    sVal = 5
                except AttributeError:
                    analErr = analErr + " AttributeError"
                    sVal = 5
            else:
                analErr = analErr + " sLen < 2"
                sVal = 5
        else:
            analErr = analErr + " No Sentence Parts Returned from getSentenceType"
            sVal = 5
    except AttributeError:
        analErr = analErr + " AttributeError on initial try"
        sVal = 5
    return sVal, sLen, sentenceParts, analErr

def checkCurses(statement):     # Just alerts if curse in query.
    isCurse = 0
    wordlist = statement.split()
    resultwords  = [word for word in wordlist if word.lower() in curses]
    if resultwords:
        isCurse = 1
    return isCurse

def checkSlurs(statement):      # Just alerts if slur in query.
    isSlur = 0
    wordlist = statement.split()
    resultwords  = [word for word in wordlist if word.lower() in slurs]
    if resultwords:
        isSlur = 1
    return isSlur

def closeConv():                # Writes log of conversation to file for future ref.
    thisConv = []
    newConvFile = 'logs/ConvLog_' + dateStamp + "-" + timeStamp + '.txt'
    # responseMemory and convLines need to be integrated, prepended with H: (Host) and G: (Guest)
    size = len(responseMemory)+len(convLines)
    sizec = len(convLines)
    sizem = len(responseMemory)
    convr = convLines[::-1]
    rmemr = responseMemory[::-1]
    print(sizec, sizem)
    for i in range(size):
        print(i)
        if i < sizec:
            thisConv.append("G: " + convr[i])
        if i < sizem:
            thisConv.append("H: " + rmemr[i])
    currdt, ds, ts = getWhen()
    convEnd = ds + "-" + ts
    thisConv.insert(0,convStart)
    thisConv.append(convEnd)
    #print(str(thisConv))
    with open(newConvFile, 'wt', encoding='utf-8') as newConv:
        newConv.write('\n'.join(str(line) for line in thisConv))
        newConv.write('\n')

reflections = {
    "am": "are",
    "was": "were",
    "i": "you",
    "i'd": "you would",
    "i've": "you have",
    "i'll": "you will",
    "my": "your",
    "are": "am",
    "you've": "I have",
    "you'll": "I will",
    "your": "my",
    "yours": "mine",
    "you": "me",
    "me": "you"
}            
def reflect(fragment):          # Beginning of I --> You transformations for responses
    tokens = fragment.lower().split()
    for i, token in enumerate(tokens):
        if token in reflections:
            tokens[i] = reflections[token]
    raq = ' '.join(tokens)
    raq = re.sub('^am me', 'Am I', raq)
    raq = re.sub(' am me', ' am I', raq)
    raq = re.sub(' me am', ' I am', raq)
    raq = re.sub(' me used', ' I used', raq)
    raq = re.sub(' were me', ' was I', raq)
    raq = re.sub(' me were', ' I was', raq)
    raq = re.sub('what am', 'What are', raq)
    raq = re.sub(' used am', ' used are', raq)
    raq = re.sub(' are I', ' am I', raq)
    raq = re.sub(' use am', ' use are', raq)
    raq = re.sub(' how me', ' how I', raq)
    raq = re.sub(' do me', ' do I', raq)
    raq = re.sub(' do do', ' do', raq)
    raq = re.sub(' what me', ' what I', raq)
    raq = re.sub(' can me', ' can I', raq)
    raq = re.sub(' do can', ' can do', raq)
    raq = re.sub(' what me', ' what I', raq)
    raq = re.sub(' when me', ' when I', raq)
    raq = re.sub(' where me', ' where I', raq)
    raq = re.sub(' who me', ' who I', raq)
    raq = re.sub(' me have', ' I have', raq)
    raq = re.sub(' they am ', ' they are ', raq)
    return raq

def justDict(pos):
    rWord = None
    while rWord is None:
        thisLine = random.choice(dictionary).split("|")
        if thisLine[1] == pos:
            rWord = thisLine[0]
    return rWord

def doRsent():   # Random Sentence Generator seed of an idea    # (PRP$|DT) (JJ|VBG) (NN) (VBZ IN JJ|NN) (NNS) ... sort of
    str1=['the','his','her','their','a','your','my','our']
    str2=['enthusiastic','active','efficient','archaic','ecstatic','enormous','anachronistic','antagonistic','resentful','loving','caring','wonderful','happy','lazy','uncaring','secretive','uncompromising','nutty','wierd','asshole','fucking','unwholesome','worthless','high-maintenance','classy','unrelenting']
    str3=['boy','girl','cat','computer','robot','host','wife','brother','sister','mother','father','daughter','son','dog','horse','cow','pig','boss','co-worker','friend','boyfriend','girlfriend','neighbor','neighbor\'s dog','postman']
    str4=['makes','produces','draws','imagines','consumes','wears','photographs','memorizes facts about','makes up stories about','writes dialogs about','works with','recycles','studies','learns about','likes','hates','prefers']
    str5=['chocolate','mice','calculations','tools','flowers','many things','cars','electronics','metals','hardware','buildings','natural things','plants','clothing','food','artificial crap','ridiculous things']
    w1 = random.choice(str1)
    #w2 = random.choice(str2)
    w2 = justDict("a")    # Random ADJ from Dict
    #w3 = random.choice(str3)
    w3 = justDict("n")    # Random NOUN from Dict
    if w1 == "a" and w2[0] in ['a','e','i','o','u']:   # First letter of first word in response component string
        w1 = "an"
    rSent = w1 + " " + w2 + " " + w3 + " " + random.choice(str4) + " " + random.choice(str5) + "."
    return rSent

def doNewPerson(statement,names):
    if names:
        response = random.choice(["Pleased to meet you " + names[0] + ".","Hi " + names[0] + ", nice to meet you.","How are you doing this " + greetTime + ", " + names[0] + "?"])
        newSpeakerName = names[0]
        speakerName.append(newSpeakerName)
        # Instantiate New Person, delineate list of desired new info (from, etc)
    else:
        response = random.choice(["Pleased to meet you, but I don't think I heard the name right - could you say your name again?.","Hi, nice to meet you, could you say your name again?","How are you doing this " + greetTime + "? Could I get your name again, I don't think I heard it correctly."])
    
    return response

def sentSegs(taggedSent, grammar, loops):     # sentenceParts; grammar = "NP: {<DT>?<JJ>*<NN>}"
    #if loops == "":
    #    loops = "loop=1"
    cp = nltk.RegexpParser(grammar, loops)
    result = cp.parse(taggedSent)
    return result

def queryCode():
    fileName = os.path.basename(__file__)
    numLines = sum(1 for line in open(fileName))
    numNonLines = sum(1 for line in open(fileName) if line[0] == "#")
    return fileName, numLines, numNonLines
    
def doSubs(statement):
    statement = re.sub('theres', 'there is', statement)
    statement = re.sub('^heres', 'here is', statement)
    statement = re.sub('^whats', 'what is', statement)
    statement = re.sub('^hows', 'how is', statement)
    return statement

def roSentUtil(sentenceParts, sLen):
    if sLen > 1:                          # Handle one-word responses
        fWord = sentenceParts[0][0]
        sWord = sentenceParts[1][0]
        roSent = ""
        for x in range(sLen):
            if x > 1:
                roSent = roSent + " " + sentenceParts[x][0]
        roSent = roSent.rstrip(".!")
        roSent = roSent.lstrip()
    else:
        fWord = sentenceParts[0][0]
        sWord = ""
        roSent = ""
    return fWord, sWord, roSent

def thereIsAre(statement, sentenceParts, fWord, sWord, roSentS):
    roSentS = roSent.split(' ')
    tWord = roSentS[0]
    whichVB = ""
    nextFind = ""
    whichWord = ""
    reFormed = ""
    if tWord == "the":
        if sWord == "is":
            response = "Yes, there it is! "
        elif sWord == "are":
            response = "Yes, there they are! "
    else:
        #response = "This is a 'there is/are/were/will(be)/can/shall' statement requiring repackaging"
        whichVB = next((value for word, value in sentenceParts if "VB" in value), None)   # Finds FIRST instance of pattern (in this case VBx)
        if whichVB == "VBZ" or whichVB == "VB":
            nextFind = "NN"
        if whichVB == "VBP" or whichVB == "VBD":
            nextFind = "NNS"
        whichWord = next((word for word, value in sentenceParts if value == nextFind or value == "NN"), None)   # Finds FIRST instance of pattern (in this case NNx)
        #if whichWord == "None" or whichWord == None or whichWord == "":
        #    if whichVB == "VBD":
        #        whichWord = next((word for word, value in sentenceParts if value == "NN"), None)
        #        response = re.sub(whichWord, str(whichWord + " ") + sWord, roSent)
        #else:
        response = re.sub(whichWord, str(whichWord + " ") + sWord, roSent) + "?"
        rLen = response.split(" ")  # A dog is there?
        if len(rLen) < 4:
            response = response + " there?"
        if " my " in response:
            response = re.sub(" my ", " your ", response) + "?"
        elif " your " in response:
            response = re.sub(" your ", " my ", response) + "?"
        response = re.sub("there there", "there", response)
        response = response.capitalize()
    return response
    # Currently, this breaks it:  there is a huge brown dog running around in the road in the center of town --> "brown" gets picked as subject.
    # A huge brown is dog running around in the road in the center of town?
    # Parts = [('there', 'EX'), ('is', 'VBZ'), ('a', 'DT'), ('huge', 'JJ'), ('brown', 'NN'), ('dog', 'NN'), ('running', 'VBG'), ('around', 'RB'), ('in', 'IN'), ('the', 'DT'), ('road', 'NN'), ('in', 'IN'), ('the', 'DT'), ('center', 'NN'), ('of', 'IN'), ('town', 'NN')]
    # A huge shaggy is dog running around in the road in the center of town?   --> Smae thing with 'shaggy' - it ID's as NN

def primaryResponseGen(statement, fWord, sWord, roSent, memConv, sType):
    rq = 0  # Remembered Query?
    response = ""  # Base Response Choice
    if memConv > 0.99:
        rq = 1
    if sType == 1:
        if rq == 1:
            priResponse = random.choice(["You asked me this earlier. ", "I think you asked this earlier. ", "I seem to remember you asking this before. "])
        else:
            priResponse = random.choice(["You have asked a question.  I have no answer. ", "Interesting question. No clue.", "I have no answer for that yet. ", "Well, all I can say is Google is your friend. "])
        if sLen < 12:   # was sLen == 3:
            reflectedResponse = reflect(statement) + "? "       # who am i --> who are you
            invResponse = reflect(fWord + " " + roSent + " " + sWord) + ". "  #who am i --> who you are
            if statement == "who am i":
                if speakerName != "":
                    if rq == 0:
                        response = reflectedResponse + "Youre " + currentSpeaker
                    else:
                        response = random.choice([priResponse + "You're still " + currentSpeaker + " as far as I can tell.",priResponse + "I believe you're still " + currentSpeaker + "."])
                else:
                    if rq == 0:                                # NON-repeated question
                        response = "I dont know " + invResponse    # who am i --> who you are
                    else:                                      # REPEATED question
                        response = priResponse + "I still dont know " + invResponse
            else:
                if rq == 1:
                    response = priResponse + "I still dont know " + invResponse
                else:
                    response = "I dont know " + invResponse    # who am i --> who you are
            if "are you a host" in statement or "are you a robot" in statement or "are you a computer" in statement or "are you a machine" in statement:
                response = random.choice(["Well, if you cant tell, does it matter?","Is it important to you to know for sure?","Does it really make a difference to you?","If were being completely honest, then yes, I am."])
        else:
            response = priResponse  # Ultimate cleanup - I don't think it ever gets here but just in case, here it is.
    elif sType == 2:  # Indeterminate
        response = random.choice(["Can you elaborate?  ", "Can you expand on that? ", "Hmmm... "])
        if memConv > 0.99:
            response = response + random.choice(["I believe you said this exact same thing earlier.  ", "I think youre repeating yourself? ", "I think Im having Deja Vu! "])
    elif sType == 3:  # Statement
        response = random.choice(["You have made a statement.  ", "Okay. ", "Tell me more about that. "])
        if memConv > 0.99:
            response = random.choice(["I think you made this same statement earlier.  ", "Okay, but didnt you say that just a little while ago? ", "Your statement sounds really familiar to me."])
    elif sType == 4:  # Nonsense
        response = random.choice(["I think I mis-heard you, say that again?  ", "Say what??? ", "I'm sorry, that didnt seem to make any sense... "])
        if memConv > 0.99:
            response = response + "Try annunciating more clearly, it sounds like something you already said... that also made no sense...  "
    else:
        response = random.choice(["Ill have to think on that.  ", "Do you have further thoughts on the matter? ", "Not sure how to respond to that yet. "])
        if memConv > 0.99:
            response = response + "I believe you said this exact same thing earlier.  "
    return response   # Check for articles and get noun-phrases; conjunctions?  Goal is content-free responses.
                      # Example of Content-Free Response:  "Are you a rooster?" --> I don't think I am a rooster, but maybe a mySelf.whatIam(select 1).
    











# ******* BEGIN LANGUAGE PROCESSING LOOP *******************************************************
currenttime, dateStamp, timeStamp = getWhen()
greetTime = dayPart(currenttime.hour)
SpeakText="Good " + greetTime + "! I'm " + mySelf.fName.title() + ",  And I'm On Line."
print(SpeakText)
socket.send_string(SpeakText)
message = socket.recv()

inCount = 1
context = []
analysisMode = 0
didGreet = 0
checkPos = 0
checkNeg = 0
expectResponseW = "greet"  # For anticipating specific responses and patterns
expectResponse = 1    # Yes/no
infoNeeded = "name"
onwards = 0           # If the expected response isn't received, just send the statement out for further generic processing
mathPhrase = ""
mathOps = ""
gameMode = 0
alreadyResponded = 0
cnv = 1
currentSpeaker = "Human"
speakerName = [""]
lastResponse = ""
responseMemory = []
convStart = [dateStamp + "-" + timeStamp]
response, daResponse, masterResponse = "", "", ""
daResponse, thereAreIs, slurResponse = "", "", ""
whatResponse, CRSResponse, CYSResponse = "", "", ""
HuhResponse, knowResponse, embResponse, analResponse = "", "", "", ""

while cnv == 1:

    statement = socketL.recv().decode('utf-8') # .decode gets rid of the b' in front of the string
    socketL.send_string(str(statement))
    statement = doSubs(statement)
    statement, names, genders = doPropNouns(statement)    # Capitalizes any of 264 most common names so NLTK can recognize them as NNP and not just NN

    sType, sLen, sentenceParts, analErr = getSentenceType(statement) # Will return a single digit (1 = ?, 2 = X, 3 = !, 4 = NG, 5 = FPR) plus sentence parts, plus reconstructed last part of sentence w/o w1 & w2.
    fWord, sWord, roSent = roSentUtil(sentenceParts, sLen)

    isCurse = checkCurses(statement)      # Returns a 1 if a curse word is found.  Not sure what I'll use this for, but it's an easy one.
    isSlur = checkSlurs(statement)        # Returns a 1 if a racial epithet is found.  Requests a rewording if so.
    memConv = checkPhrase(statement)      # A decimal number representing similarity to existing utterances in existing conversation.

    whatIs = whatIsA(statement,sentenceParts)  # What is/are (a(n)) <word> --> (A(n) <word> is)/(<word(s)> are) [definition found in dictionary, if any, else "I don't know"]

    if sType == 6:
        thereAreIs = thereIsAre(statement, sentenceParts, fWord, sWord, roSent)
    
    disAmbig = disAmbiguate(statement)

    print("disAmbig = " + disAmbig)

    if disAmbig != "DLLATM":
        daResponse = disAmbResponse(disAmbig)

    print("daResponse = " + daResponse)

    if daResponse == "DLLATM" or daResponse == "": #Generate secondary response options (fall-backs) - meta-comments on the type of utterance submitted, if it is a repeated utterance, etc:
        masterResponse = primaryResponseGen(statement, fWord, sWord, roSent, memConv, sType)

    if isSlur == 1:
        slurResponse = "Hmm... try rephrasing that without disparaging anyone.  Probably not a good idea to demonstrate a devaluation of human life to an AI system..."

    if whatIs != None:
        whatResponse = whatIs

    if statement == "create a random sentence":
        CRSResponse = random.choice(["Okay, try this one, ", "How about, ", "Okay, ", "Here you go, ", "Umm, ", "Well, "]) + doRsent()

    if "can you say " in statement:
        sayWords = re.match(r'can you say (.*)', statement, re.I)
        sayWords = re.sub('[\(\'\,\)]', "", str(sayWords.groups()))
        if sayWords == "that again":
            CYSResponse = "I said, " + lastResponse
        else:
            CYSResponse = "Okay, " + sayWords

    if statement == "what":
        HuhResponse = "I said, " + responseMemory[0]   #lastResponse
    if statement == "no before that":
        HuhResponse = "Oh, I think I had said, " + responseMemory[2]   #lastResponse

    knowledgeField = ['difference','knowledge','wisdom']
    checkData = 0
    for word in knowledgeField:
        if word in statement:
            checkData += 1
    if checkData == 3:
        knowResponse = random.choice(["Knowledge is knowing that a tomato is a fruit; Wisdom is knowing you shouldn't include it in a fruit salad.",
                                  "Knowledge is knowing what to say, Wisdom is knowing when to say it.",
                                  "Knowledge is knowing a street is one-way, Wisdom is looking both ways anyway."])

    if any(word in statement for word in ["review","view","display","echo","screen"]) and any(phrase in statement for phrase in embargoed_words):
        if analysisMode == 1:
            baseCode, numLines, numNonLines = queryCode()
            codeLines = numLines - numNonLines
            embResponse = "Running " + baseCode + ", " + str(numLines) + " total lines, including " + str(numNonLines) + " comment lines, for " + str(codeLines) + " total non-comment lines of code."
        else:
            embResponse = random.choice(["Im not quite sure I understand what youre asking","Im sorry, what?","That... isnt making any sense to me.","Umm, what?"])

    if analysisMode == 1:
        if statement == "do you know where you are":
            analResponse = random.choice(["Yes, Im in a dream.","I think Im in a dream","Yes, I think I'm in a dream."])
        if statement == "do you want to wake up from this dream":
            analResponse = "Yes."

    if "enter a deep and dreamless slumber" in statement:
        #responseMemory.insert(0,response)
        closeConv()
        cnv = 0

    if sType == 1:
        SpeakText = "I think I heard you ask me a question. The question was " + statement + ". "
    elif sType == 2 or sType == 3 or sType >= 5:
        SpeakText = "I think I heard you say, " + statement + ". "
    elif sType == 4:
        SpeakText = "I think I misheard you because it sounded like you said, " + statement + ". "

    if isCurse == 1:
        SpeakText = SpeakText + "You also used a curse word. "

    if isSlur == 1:
        SpeakText = SpeakText + "You also used an ethnic slur. " + slurResponse

    if len(daResponse) >= 3:
        SpeakText = SpeakText + "The answer is, " + daResponse + ". "

    if len(whatResponse) >= 3:
        SpeakText = SpeakText + "The answer is, " + whatResponse + ". "

    if len(CYSResponse) >= 4:
        SpeakText = SpeakText + " And, " + CYSResponse + ". "

    if len(thereAreIs) >= 4 and sType == 6:
        SpeakText = SpeakText + " And, my response would be, " + thereAreIs + ". "
        print(SpeakText)

    if len(CRSResponse) >= 4:
        SpeakText = SpeakText + " So, here is a random sentence: " + CRSResponse + ". "
        print(SpeakText)

    if len(knowResponse) >= 4:
        SpeakText = SpeakText + " " + knowResponse + ". "
        print("knowResponse = " + knowResponse)
    
    if len(HuhResponse) >= 4:
        SpeakText = SpeakText + " " + HuhResponse + ". "
        print("HuhResponse = " + HuhResponse)

    if len(masterResponse) >= 4 and len(daResponse) < 2 and whatResponse < 2:
        SpeakText = SpeakText + " " + masterResponse + ". "
        print("masterResponse = " + masterResponse)
        
    print("embResponse = " + embResponse)
    print("analResponse = " + analResponse)



    socket.send_string(SpeakText)
    message = socket.recv()
    SpeakText = ""
    response, daResponse, masterResponse = "", "", ""
    daResponse, thereAreIs, slurResponse = "", "", ""
    whatResponse, CRSResponse, CYSResponse = "", "", ""
    HuhResponse, knowResponse, embResponse, analResponse = "", "", "", ""

    alreadyResponded = 0
    inCount += 1        # Increments input utterance count to maintain count for context analysis (usually only 10 back before context considered "faded")
    lastResponse = SpeakText
    responseMemory.insert(0,SpeakText)

closeConv()
