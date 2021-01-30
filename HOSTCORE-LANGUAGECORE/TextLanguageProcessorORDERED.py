#!/usr/bin/python

# ***************** IMPORT ALL REQUIRED DEPENDENCIES ******************************
from difflib import SequenceMatcher as SM
import nltk
from nltk.tag import pos_tag
import calendar
import datetime
import random
import time
import os
import re

# ***************** ENVIRONMENT CHECK, SETUP NETWORKING IF ON HOST *******************************

opsys = "undef"
try:     # Runs on initial start, sets some variables depending on where the host code is running
    sysInfo = str(os.uname()).strip() # Linux (Pi 3) Only (Returns posix.uname_result(sysname='Linux', nodename='Dolores-M', release='4.14.34-v7+', version='#1110 SMP Mon Apr 16 15:18:51 BST 2018', machine='armv7l'))
    print(sysInfo)
    if "Linux" in sysInfo:
        opsys = "Host"
    else:
        opsys = "Dev"
except AttributeError:
    opsys = "Dev"
print(opsys)

if opsys == "Host":
    print("Speech Recognition enabled.")
    import zmq
    context = zmq.Context()

    print("Establishing Language Network Node")
    socketL = context.socket(zmq.REP)
    socketL.bind("tcp://*:5558")  # Listen on 5558 for input (such as from SpeechRecognition)

    print("Connecting to Speech Center")
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555") # Send to 5555 to speak (SpeechCenter)
else:
    print("Speech functions unavailable on this system, text-input/output only.")

# ***************** SETUP NETWORKING *******************************

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
Host = open('ACTIVEHOST.txt', "r")  # On Host Processor
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

# ***************** SET OR READ IN ALL "IN-HEAD" BASE KNOWLEDGE REFERENCES *******
dictInitWords={  # Determine from 1st two words if likely a Question (1), Indeterminate (2), Statement (3), or Invalid (4) (System later adds a 5 if not found here, 6 if 'there is/are/was/will (be)/were/can/cant' etc)
    'who':{'were':1,'was':1,'will':1,'is':1,'are':1,'his':3,'her':3,'their':3,'my':3,'our':3,'your':3,'its':3,'i':3,'you':3,'we':3,'they':3,'it':3,'there':3,'that':2,'the':2,'in':2,'can':1,'can\'t':1,'cannot':1,'am':1,'do':4,'did':1,'does':1},
    'what':{'were':1,'was':1,'will':1,'is':1,'are':1,'his':3,'her':3,'their':3,'my':3,'our':3,'your':3,'its':3,'i':3,'you':3,'we':3,'they':3,'it':3,'there':3,'that':3,'the':2,'in':1,'can':1,'can\'t':1,'cannot':1,'am':1,'do':1,'did':1,'does':1},
    'why':{'were':1,'was':1,'will':1,'is':1,'are':1,'his':3,'her':3,'their':3,'my':3,'our':3,'your':3,'its':3,'i':3,'you':3,'we':3,'they':3,'it':3,'there':3,'that':3,'the':2,'in':2,'can':1,'can\'t':1,'cannot':1,'am':1,'do':1,'did':1,'does':1},
    'where':{'were':1,'was':1,'will':1,'is':1,'are':1,'his':3,'her':3,'their':3,'my':3,'our':3,'your':3,'its':3,'i':3,'you':3,'we':3,'they':3,'it':3,'there':3,'that':3,'the':2,'in':1,'can':1,'can\'t':1,'cannot':1,'am':1,'do':1,'did':1,'does':1},
    'when':{'were':1,'was':1,'will':1,'is':1,'are':1,'his':3,'her':3,'their':3,'my':3,'our':3,'your':3,'its':3,'i':3,'you':3,'we':3,'they':3,'it':3,'there':3,'that':3,'the':2,'in':2,'can':1,'can\'t':1,'cannot':1,'am':1,'do':1,'did':1,'does':1},
    'how':{'were':1,'was':1,'will':1,'is':1,'are':1,'his':3,'her':3,'their':3,'my':3,'our':3,'your':3,'its':3,'i':3,'you':3,'we':3,'they':3,'it':3,'there':3,'that':3,'the':2,'in':2,'can':1,'can\'t':1,'cannot':1,'am':1,'do':1,'did':1,'does':1},
    'have':{'were':4,'was':4,'will':4,'is':4,'are':4,'his':2,'her':2,'their':2,'my':2,'our':2,'your':2,'its':2,'i':1,'you':1,'we':1,'they':1,'it':3,'there':1,'that':3,'the':1,'in':1,'can':4,'can\'t':4,'cannot':4,'am':4,'do':4,'did':4,'does':4},
    'has':{'were':4,'was':4,'will':4,'is':4,'are':4,'his':1,'her':1,'their':1,'my':1,'our':1,'your':1,'its':1,'i':4,'you':4,'we':4,'they':4,'it':1,'there':1,'that':1,'the':1,'in':1,'can':4,'can\'t':4,'cannot':4,'am':4,'do':4,'did':4,'does':4},
    'can':{'were':4,'was':4,'will':4,'is':4,'are':4,'his':1,'her':1,'their':1,'my':1,'our':1,'your':1,'its':1,'i':1,'you':1,'we':1,'they':1,'it':1,'there':1,'that':1,'the':1,'in':1,'can':4,'can\'t':4,'cannot':4,'am':4,'do':4,'did':4,'does':4},
    'can\'t':{'were':4,'was':4,'will':4,'is':4,'are':4,'his':1,'her':1,'their':1,'my':1,'our':1,'your':1,'its':1,'i':1,'you':1,'we':1,'they':1,'it':1,'there':1,'that':1,'the':1,'in':1,'can':4,'can\'t':4,'cannot':4,'am':4,'do':5,'did':4,'does':4},
    'cannot':{'were':4,'was':4,'will':4,'is':4,'are':4,'his':1,'her':1,'their':1,'my':1,'our':1,'your':1,'its':1,'i':1,'you':1,'we':1,'they':1,'it':1,'there':1,'that':1,'the':1,'in':1,'can':4,'can\'t':4,'cannot':4,'am':4,'do':5,'did':4,'does':4},
    'do':{'were':4,'was':4,'will':4,'is':4,'are':4,'his':1,'her':1,'their':1,'my':1,'our':1,'your':1,'its':1,'i':1,'you':1,'we':1,'they':1,'it':1,'there':4,'that':2,'the':1,'in':1,'can':4,'can\'t':4,'cannot':4,'am':4,'do':4,'did':4,'does':4},
    'does':{'were':4,'was':4,'will':4,'is':4,'are':4,'his':1,'her':1,'their':1,'my':1,'our':1,'your':1,'its':1,'i':4,'you':4,'we':4,'they':4,'it':1,'there':4,'that':1,'the':1,'in':1,'can':4,'can\'t':4,'cannot':4,'am':4,'do':4,'did':4,'does':4},
    'did':{'were':4,'was':4,'will':4,'is':4,'are':4,'his':1,'her':1,'their':1,'my':1,'our':1,'your':1,'its':1,'i':1,'you':1,'we':1,'they':1,'it':1,'there':1,'that':1,'the':1,'in':1,'can':4,'can\'t':4,'cannot':4,'am':4,'do':3,'did':4,'does':4},
    'will':{'were':4,'was':4,'will':4,'is':4,'are':4,'his':1,'her':1,'their':1,'my':1,'our':1,'your':1,'its':1,'i':1,'you':1,'we':1,'they':1,'it':1,'there':1,'that':1,'the':1,'in':4,'can':4,'can\'t':4,'cannot':4,'am':4,'do':3,'did':4,'does':4},
    'are':{'were':4,'was':4,'will':4,'is':4,'are':4,'his':1,'her':1,'their':1,'my':1,'our':1,'your':1,'its':1,'i':4,'you':1,'we':1,'they':1,'it':4,'there':1,'that':4,'the':1,'in':4,'can':4,'can\'t':4,'cannot':4,'am':4,'do':4,'did':4,'does':4},
    'am':{'were':4,'was':4,'will':4,'is':4,'are':4,'his':4,'her':4,'their':4,'my':4,'our':4,'your':4,'its':4,'i':1,'you':4,'we':4,'they':4,'it':4,'there':4,'that':4,'the':4,'in':4,'can':4,'can\'t':4,'cannot':4,'am':4,'do':4,'did':4,'does':4},
    'is':{'were':4,'was':4,'will':4,'is':4,'are':4,'his':1,'her':1,'their':1,'my':1,'our':1,'your':1,'its':1,'i':4,'you':4,'we':4,'they':4,'it':1,'there':1,'that':1,'the':1,'in':1,'can':4,'can\'t':4,'cannot':4,'am':4,'do':4,'did':4,'does':4},
    'was':{'were':4,'was':4,'will':4,'is':4,'are':4,'his':1,'her':1,'their':1,'my':1,'our':1,'your':1,'its':1,'i':1,'you':4,'we':4,'they':4,'it':1,'there':1,'that':1,'the':1,'in':1,'can':4,'can\'t':4,'cannot':4,'am':4,'do':4,'did':4,'does':4},
    'were':{'were':4,'was':4,'will':4,'is':4,'are':4,'his':2,'her':2,'their':2,'my':2,'our':2,'your':2,'its':2,'i':2,'you':2,'we':2,'they':2,'it':2,'there':2,'that':3,'the':2,'in':4,'can':4,'can\'t':4,'cannot':4,'am':4,'do':4,'did':4,'does':4},
    'if':{'were':4,'was':4,'will':4,'is':4,'are':4,'his':2,'her':2,'their':2,'my':2,'our':2,'your':2,'its':2,'i':2,'you':2,'we':2,'they':2,'it':2,'there':3,'that':2,'the':2,'in':2,'can':4,'can\'t':4,'cannot':4,'am':4,'do':4,'did':4,'does':4},
    'shall':{'were':4,'was':4,'will':4,'is':4,'are':4,'his':2,'her':2,'their':2,'my':2,'our':2,'your':2,'its':2,'i':2,'you':2,'we':2,'they':2,'it':2,'there':2,'that':2,'the':2,'in':4,'can':4,'can\'t':4,'cannot':4,'am':4,'do':3,'did':4,'does':4},
    'should':{'were':4,'was':4,'will':4,'is':4,'are':4,'his':2,'her':2,'their':2,'my':2,'our':2,'your':2,'its':2,'i':2,'you':2,'we':2,'they':2,'it':2,'there':2,'that':2,'the':2,'in':2,'can':4,'can\'t':4,'cannot':4,'am':4,'do':3,'did':4,'does':4},
    'would':{'were':4,'was':4,'will':4,'is':4,'are':4,'his':2,'her':2,'their':2,'my':2,'our':2,'your':2,'its':2,'i':2,'you':2,'we':2,'they':2,'it':2,'there':2,'that':2,'the':2,'in':2,'can':4,'can\'t':4,'cannot':4,'am':4,'do':3,'did':4,'does':4},
    'could':{'were':4,'was':4,'will':4,'is':4,'are':4,'his':2,'her':2,'their':2,'my':2,'our':2,'your':2,'its':2,'i':2,'you':2,'we':2,'they':2,'it':2,'there':2,'that':1,'the':2,'in':2,'can':4,'can\'t':4,'cannot':4,'am':4,'do':3,'did':4,'does':4},
    'which':{'were':1,'was':1,'will':1,'is':1,'are':1,'his':3,'her':3,'their':3,'my':3,'our':3,'your':3,'its':3,'i':3,'you':3,'we':3,'they':3,'it':3,'there':3,'that':2,'the':2,'in':2,'can':2,'can\'t':2,'cannot':2,'am':4,'do':2,'did':1,'does':2},
    'may':{'were':4,'was':3,'will':1,'is':1,'are':4,'his':2,'her':2,'their':2,'my':2,'our':2,'your':2,'its':2,'i':2,'you':2,'we':2,'they':2,'it':2,'there':2,'that':2,'the':2,'in':2,'can':2,'can\'t':2,'cannot':2,'am':4,'do':4,'did':4,'does':3},
    'might':{'were':4,'was':3,'will':3,'is':3,'are':4,'his':2,'her':2,'their':2,'my':2,'our':2,'your':2,'its':2,'i':2,'you':2,'we':2,'they':2,'it':2,'there':2,'that':2,'the':2,'in':2,'can':3,'can\'t':3,'cannot':3,'am':4,'do':4,'did':4,'does':3},
    'in':{'were':4,'was':4,'will':4,'is':4,'are':4,'his':2,'her':2,'their':2,'my':2,'our':2,'your':2,'its':2,'i':4,'you':3,'we':2,'they':2,'it':3,'there':2,'that':2,'the':2,'in':4,'can':4,'can\'t':4,'cannot':4,'am':4,'do':4,'did':4,'does':4},
    'at':{'were':4,'was':4,'will':2,'is':4,'are':4,'his':2,'her':2,'their':2,'my':2,'our':2,'your':2,'its':2,'i':4,'you':2,'we':4,'they':4,'it':3,'there':4,'that':2,'the':2,'in':4,'can':4,'can\'t':4,'cannot':4,'am':4,'do':4,'did':4,'does':4},
    'to':{'were':4,'was':4,'will':4,'is':4,'are':4,'his':2,'her':2,'their':2,'my':2,'our':2,'your':2,'its':2,'i':4,'you':3,'we':4,'they':4,'it':3,'there':3,'that':2,'the':2,'in':4,'can':4,'can\'t':4,'cannot':4,'am':4,'do':3,'did':4,'does':4},
    'from':{'were':4,'was':4,'will':2,'is':4,'are':4,'his':2,'her':2,'their':2,'my':2,'our':2,'your':2,'its':2,'i':4,'you':2,'we':4,'they':4,'it':2,'there':2,'that':2,'the':2,'in':2,'can':4,'can\'t':4,'cannot':4,'am':4,'do':2,'did':4,'does':4},
    'on':{'were':4,'was':4,'will':4,'is':4,'are':4,'his':2,'her':2,'their':2,'my':2,'our':2,'your':2,'its':2,'i':4,'you':3,'we':4,'they':4,'it':3,'there':3,'that':2,'the':2,'in':4,'can':4,'can\'t':4,'cannot':4,'am':4,'do':4,'did':4,'does':4},
    'under':{'were':4,'was':4,'will':4,'is':4,'are':4,'his':3,'her':3,'their':3,'my':3,'our':3,'your':3,'its':3,'i':4,'you':3,'we':2,'they':2,'it':2,'there':3,'that':2,'the':2,'in':4,'can':4,'can\'t':4,'cannot':4,'am':4,'do':4,'did':4,'does':4},
    'over':{'were':4,'was':4,'will':4,'is':4,'are':4,'his':3,'her':3,'their':3,'my':3,'our':3,'your':3,'its':3,'i':4,'you':3,'we':2,'they':2,'it':2,'there':3,'that':3,'the':2,'in':2,'can':4,'can\'t':4,'cannot':4,'am':4,'do':2,'did':4,'does':2},
    'there':{'were':6,'was':6,'will':6,'is':6,'are':6,'his':3,'her':3,'their':3,'my':3,'our':3,'your':3,'its':3,'i':2,'you':3,'we':3,'they':3,'it':3,'there':5,'that':3,'the':3,'in':3,'can':6,'can\'t':6,'cannot':6,'am':4,'do':3,'did':3,'does':3,'shall':6,'wont':6},
    'WNNP':{'were':2,'was':2,'will':2,'is':2,'are':4,'his':2,'her':2,'their':2,'my':2,'our':3,'your':3,'its':3,'i':2,'you':3,'we':2,'they':2,'it':2,'there':2,'that':2,'the':2,'in':4,'can':3,'can\'t':3,'cannot':3,'am':4,'do':4,'did':3,'does':2}
}

contractions_dict = { 
"ain't": "is not",
"aren't": "are not",
"can't": "cannot",
"can't've": "cannot have",
"'cause": "because",
"could've": "could have",
"couldn't": "could not",
"couldn't've": "could not have",
"didn't": "did not",
"doesn't": "does not",
"don't": "do not",
"hadn't": "had not",
"hadn't've": "had not have",
"hasn't": "has not",
"haven't": "have not",
"he'd": "he would",
"he'd've": "he would have",
"he'll": "he will",
"he'll've": "he will have",
"he's": "he is",
"how'd": "how did",
"how'd'y": "how do you",
"how'll": "how will",
"how's": "how is",
"i'd": "i would",
"i'd've": "i would have",
"i'll": "i will",
"i'll've": "I will have",
"i'm": "i am",
"i've": "i have",
"isn't": "is not",
"it'd": "it would",
"it'd've": "it would have",
"it'll": "it will",
"it'll've": "it will have",
"it's": "it is",
"let's": "let us",
"ma'am": "madam",
"mayn't": "may not",
"might've": "might have",
"mightn't": "might not",
"mightn't've": "might not have",
"must've": "must have",
"mustn't": "must not",
"mustn't've": "must not have",
"needn't": "need not",
"needn't've": "need not have",
"o'clock": "of the clock",
"oughtn't": "ought not",
"oughtn't've": "ought not have",
"shan't": "shall not",
"sha'n't": "shall not",
"shan't've": "shall not have",
"she'd": "she would",
"she'd've": "she would have",
"she'll": "she will",
"she'll've": "she will have",
"she's": "she is",
"should've": "should have",
"shouldn't": "should not",
"shouldn't've": "should not have",
"so've": "so have",
"so's": "so is",
"that'd": "that would",
"that'd've": "that would have",
"that's": "that is",
"there'd": "there would",
"there'd've": "there would have",
"there's": "there is",
"they'd": "they would",
"they'd've": "they would have",
"they'll": "they will",
"they'll've": "they will have",
"they're": "they are",
"they've": "they have",
"to've": "to have",
"wasn't": "was not",
"we'd": "we would",
"we'd've": "we would have",
"we'll": "we will",
"we'll've": "we will have",
"we're": "we are",
"we've": "we have",
"weren't": "were not",
"what'll": "what will",
"what'll've": "what will have",
"what're": "what are",
"what's": "what is",
"what've": "what have",
"when's": "when is",
"when've": "when have",
"where'd": "where did",
"where's": "where is",
"where've": "where have",
"who'll": "who will",
"who'll've": "who will have",
"who's": "who is",
"who've": "who have",
"why's": "why is",
"why've": "why have",
"will've": "will have",
"won't": "will not",
"won't've": "will not have",
"would've": "would have",
"wouldn't": "would not",
"wouldn't've": "would not have",
"y'all": "you all",
"y'all'd": "you all would",
"y'all'd've": "you all would have",
"y'all're": "you all are",
"y'all've": "you all have",
"you'd": "you would",
"you'd've": "you would have",
"you'll": "you will",
"you'll've": "you will have",
"you're": "you are",
"you've": "you have",
"theres": "there is",
"heres": "here is",
"whats": "what is",
"hows": "how is"
}

contractions_re = re.compile('(%s)' % '|'.join(contractions_dict.keys()))

file_name = 'namesKnown.txt'   # In prep to allow new names to be learned and written to text list for premanent retention
propNouns = {}
with open(file_name) as file:
    for line in file:
        line = line.replace('\n','')
        pairs = line.split(":")
        propNouns.update(zip(pairs[0::2], pairs[1::2]))

numberWords = {'one':1, 'two':2, 'three':3, 'four':4, 'five':5, 'six':6, 'seven':7, 'eight':8, 'nine':9, 'ten':10, 'eleven':11, 'twelve':12, 'thirteen':13, 'fourteen':14, 'fifteen':15, 'sixteen':16, 'seventeen':17, 'nineteen':19,
               'twenty':20, 'thirty':30, 'forty':40, 'fifty':50, 'sixty':60, 'seventy':70, 'eighty':80, 'ninety':90, 'hundred':100, 'thousand':1000, 'million':1000000, 'billion':1000000000, 'trillion':1000000000000}

mathWords = {'divided':'/', 'multiplied':'*', 'times':'*', 'plus':'+', 'minus':'-', 'squared':'^2', 'cubed':'^3', 'square root':'sqrt(x)', 'into':'/', 'point':'.', 'dot':'.'}

allMath = {**numberWords, **mathWords}

openerWords = ['well','so','but','then','um','uh']

curses = ['fuck','fucking','fucked','shit','shitted','shitting','shitwad','shitty','cunt','cunty','cuntwad','pussy','twat','prick','cock','cocksucker','cocksmoker','asshole','shithole','fucknut','fucktard','dickhead','fag','faggot']

slurs = ['gook','honkey','nigger','sandnigger','spic','wop','kike','coon','jap','wetback','kraut','krout']

introduction_words = ["id like you to meet","allow me to introduce","let me introduce","please meet","here is my friend","this is my friend","say hello to","say hi to"]

embargoed_words = ["core code","base code","host code"]

colors = ['aqua','bronze','cerulean','lilac','almond','gold','jade','plum','indigo','violet','tan','slate','sand','turquoise','silver','taupe','copper','cornflower',
          'khaki','red','green','yellow','blue','orange','purple','cyan','magenta','mauve','mahogany','apricot','peach','lemon','lime','pink','teal','lavender',
          'brown','beige','maroon','mint','olive','coral','navy','gray','grey','white','black','salmon','chartreuse','peuce']

responsePolarities = {'yes':0.95, 'hell yes':0.99, 'fuck yes':1.00, 'fuck yeah':1.00, 'okay':0.70, 'ok':0.70, 'yeah':0.75, 'sure':0.65, 'i suppose':0.40, 'why not':0.35,
                      'maybe':0.25, 'perhaps':0.25, 'not really':-0.25, 'not now':-0.25, 'i don\'t think so':-0.50, 'no':-0.85, 'never':-0.90, 'no way':-0.90,
                      'no way in hell':-0.99, 'fuck no':-1.00, 'no fucking way':-1.00, 'fuck that':-1.00, 'don\'t go there':-1.00, 'are you out of your mind':-1.00,
                      'Certainly':0.85,'Definitely':0.85,'Of course':0.90,'Gladly':0.90,'Absolutely':0.95,'Indeed':0.90,'Undoubtedly':0.80,'Ya':0.60,
                      'Yep':0.65,'Yup':0.65,'Totally':0.75,'Sure':0.60,'You bet':0.70,'K':0.60,'Alright':0.60,'Alrighty':0.55,'Sounds good':0.70,'Sure thing':0.70}

greeting_vocab = ['good afternoon','good evening','good morning','good to see you','greetings','hello','hey',
               'hey babe','hey man','hi','hi there','hiya','hola','howdy','its been a while','its been ages','its nice to meet you',
               'long time no see','nice to see you','pleased to meet you','sup','watup','well hello there','whats going on','whats new','whats up',
               'whats up','whatup','whazzup','good morning','good afternoon','good evening','top of the morning']

howRU_vocab = ['are you okay','how are things','how are you','how do you do','how have you been','hows everything','hows everything','hows it going',
             'hows it going','hows life','hows your day','hows your day going','howve you been','you alright','you okay']

negative_vocab = ['horrible','lousy','suck','sucks','sucked','miserable','crappy','crap','turd','sick','rotten','hurts','pain','cold','sucks','awful','bad',
                  'terrible','useless','hate','hated','shit','shitty','poor',':(']

positive_vocab = ['well','good','better','happy','marvelous','ecstatic','magnificent','wonderful','fantastic','excited','great','fine','stupendous','stupendously',
                  'happily','wonderfully','magnificently','fantastically','ok','okay','fun',':)']

neutral_vocab = ['movie','the','sound','was','is','actors','did','know','words','not','the','this','these','it','and','average','who','what','why','when','how','i',
                 'can','have','has','had','who','what','why','where','when','how','have','has','can','can\'t','do','does','did','will','are','am','is','was',
                 'were','if','shall','should','would','could','which','may','might','in','at','to','from','on','under','over','his','her','their','my','our','your',
                 'its','you','we','they','it','there','that','the','in','can','can\'t','cannot','as','asdfghjk']

thankList = {".*thank(s|\syou).*":"You're welcome","thank(\s|s|\syou) (very|so) much.*":"You're very welcome","thank you very much.*":"You're very welcome",
             ".*appreciate that":"My pleasure","gracias":"De nada","muchas gracias":"De nada","danka":"Happy to help",".*danke":"Happy to help"}

sports_words = ['baseball','football','soccer','basketball','golf','bowling','hockey','swimming','racing','skating']

datetime_words = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday','january','february','march','april','may','june','july',
                'august','september','october','november','december','morning','afternoon','evening','night','day','week','month','year','decade','century']

weather_words = ['sun.*','warm','hot','cloud.*','cold','rain.*','storm.*','hurricane.*','tornad.*','wind.*','humid.*','breez.*']

embargoed_words = ["core code","base code","host code"]

name_vocab = ['my name is','whats your name','what are you called','what do you call yourself','who are you']
myName = mySelf.fName
name_vocab.append(myName)

whatRUList = ["are you a host","are you a robot","are you a computer","are you a machine","are you an automaton","are you human","are you a human","are you a person"]

# ***************** CORE LANGUAGE FUNCTIONS FOR PROCESSING HEARD SPEECH *************************************************************

hiVar = "|".join(greeting_vocab)
hruVar = "|".join(howRU_vocab)
nameVar = "|".join(name_vocab)
greetResponse = ""
expectName = 0

def isItGreetings(statement):
    speakerName = ""
    names = ""
    myNameKnown = 0
    haveName = 0
    greetResponse = ""
    expectName = 0
    hw, rw, nw, hg, rg, ng = "", "", "", "", "", ""
    hw = re.match(r".*\b(?P<hiWrd>" + hiVar + r")\s?(?P<rest>.*)?", statement, re.I)  # .*\b(?P<hiWrd>hi|hello|howdy|sup)\s(?P<rest>.*)?
    rw = re.match(r".*\b(?P<hruWrd>" + hruVar + r")(?P<rest>.*)?", statement, re.I)  # .*\b(?P<hruWrd>how are things|how are you|hows it going)(?P<rest>.*)?
    nw = re.match(r".*\b(?P<nameWrd>" + nameVar + r")(?P<rest>.*)?", statement, re.I)  # .*\b(?P<nameWrd>my name is|whats your name|maeve)(?P<rest>.*)?
    
    print("statement = " + str(statement) + " & hiWrd = " + str(hw) + " & HRUwrd = " + str(rw) + " & nameWrds = " + str(nw) + " & myName = " + str(myName))
    
    if hw:
        hg = hw.group("hiWrd")
        print("hg = " + hg)
    if rw:
        rg = rw.group("hruWrd")
        print("rg = " + rg)
    if nw:
        ng = nw.group("nameWrd")
        print("ng = " + ng)
        if ng:
            if ng.lower() == myName.lower():
                myNameKnown = 1  #Speaker greeted me by name, and may know me
                print("My Name Known!")
        if names:
            print(" NAMES: " + len(names), names[0])
            if len(names) > 0:
                haveName = 1
                
    if hg:
        #greetResponse = hg + " to you too"
        greetResponse = random.choice([hg + " to you too","hey, " + hg])

    if haveName == 1:
        greetResponse = greetResponse + ", " + names[0] + ". "
    else:
        if myNameKnown == 0:
            greetResponse = greetResponse + ". I'm " + myName + ". "
        else:
            greetResponse = greetResponse + ". "
    
    if rg:
        greetResponse = greetResponse + "I'm doing well and enjoying the learning process. "
    
    if myNameKnown == 1 and haveName == 0:
        greetResponse = greetResponse + random.choice(["You have me at a slight disadvantage; you know my name but I don't know yours?","With whom am I speaking?","And who might you be?"])
        expectName = 1
    print("GR1 = " + greetResponse)
    return greetResponse, str(expectName)
    
    # Good morning/afternoon/evening; how are you (this) (fine) morning/afternoon/evening
    # Check for actual time == morning/afternoon/evening and comment appropriately
    

def checkOpeners(statement):
    oStatement = statement
    newStatement = ""
    statement = statement.lower()
    theseWords = statement.split(" ")
    if theseWords[0] in openerWords:
        openers = theseWords[0]
        del theseWords[0]
        newStatement = " ".join(theseWords)
        print(newStatement)
        return newStatement, openers
    else:
        return oStatement, ""

def check4Name():
    statement = input("expectResponse/check4name>> ")
    if myName.lower() in statement.lower():
        statement = statement.replace(myName.lower(), "")
    statement, names, genders = doPropNouns(statement)
    if names:
        nameResponse = "Nice to meet you " + names[0]
        expectResponse = 0
    else:
        nameResponse = "Sorry, didn't recognize a name... "
        expectResponse = 1
    return nameResponse, expectResponse

def doLookup(): # HostDict.txt, word|POS|Definition|Animacy Code
    dictFile = open('RESOURCES/LANGFILES/HostDict.txt')
    dictLines = dictFile.readlines()
    dictFile.close
    dictLines = [x.strip() for x in dictLines] 
    return dictLines

dictionary = doLookup()     # Reads dictionary into memory for faster review later, so dictionary contains dictLines

def expand_contractions(s, contractions_dict=contractions_dict):
    def replace(match):
        return contractions_dict[match.group(0)]
    return contractions_re.sub(replace, s)

def convPostulateQ(statement):    # Try for this also:  "i'm really curious how this will turn out"
    cpqFlag = "0"
    mRef = ""
    m = re.match(r".*\b(?:i'(?:m|ve|d)|(?:i am|you are|he is|i have|i would|we are)) (?:.*)\s+(if|whether|how)\s+(?P<actualQ>.*)(?: |.|)", statement, re.I)
    if m:
        mRef = m.group('actualQ')
        if len(mRef) > 1:
            cpqFlag = "1"
        m2 = re.sub(r'(i|you|he|she|they|it|we) (am|are|can|may|might|will|have|should|could|would|know) (.*)', r'\2 \1 \3', mRef)  # Contains corrected form of question
        m3 = m2.split(" ")
        if len(m3) == 2:
            m2 = re.sub(r'(i|you|he|she|they|it|we) (am|are|can|may|might|will|have|should|could|would|know)', r'\2 \1', m2)
        m2 = re.sub(r'(have|know) (you|I) (.*)', r'do \2 \1 \3', m2)  # Contains corrected form of question
        #m3 = m2.split(" ")
        m4 = m2[0].capitalize() + m2[1:] + "?"
        m4 = re.sub(r'\.\?', '?', m4)
        if m.group(1) == "how":
            m4 = re.sub(r'(\w+) (\w+) (\w+)(.*)', r'\2 \1 \3 \4', m4)  # who are you --> who you are
            m4 = m.group(1) + " " + m4
        return m4, cpqFlag
    else:
        return "","0"

def getWhen():
    currenttime = datetime.datetime.now()
    dateStamp = str(datetime.date.today().strftime("%Y%m%d"))
    timeStamp = str("%s%s%s" % (currenttime.hour, currenttime.minute, currenttime.second))
    return currenttime, dateStamp, timeStamp

def dayPart(hour):
    if hour < 12:
        dayPart = "morning"
    elif hour > 11 and hour < 18:
        dayPart = "afternoon"
    elif hour > 17:
        dayPart = "evening"
    return dayPart

def checkReply(reply):    #  Currently finds "no" in "know", so....  only partially working.  See below for regexp recode.
    replyVal = 0
    for key, value in responsePolarities.items():
        if key.lower() in reply.lower():
            return value
        else:
            value = 0
    return value


#responsePolarities = {'yes':0.95, 'hell yes':0.99, 'no':-0.95, 'hell no':-0.99, 'okay':0.70}

#strings = [
#    'I know nothing',
#    'I now think the answer is no',
#    'hell, mayb yes',
#    'or hell yes',
#    'i thought:yes or maybe--hell yes--'
#]

#for s in strings:
#    for k,v in responsePolarities.items():
#        if re.search(rf"\b{k}\b", s):
#            print(f"'{s}' matches: {k} : {v}")
    
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
    punctCapture = ""
    for word in theseWords:
        punctCapture = ""
        oWord = word
        if not word[-1].isalpha():
            word = word[:-1]
            punctCapture = oWord[-1]
        gData = propNouns.get(word.title(),"X")  #X is a default value - if propNouns contains key "word.title, will return gender value; if not, returns default "X"
        if gData != "X":
            if i == 0:    # If word in propNouns list AND if it's the first word in the utterance, capitalize it
                n.append(word.title() + punctCapture)
                nameList.append(word.title())
                genderList.append(gData)
            if i > 0:
                if theseWords[i-1] in ['a','the','this','that','my','your','they','their','his','her','our','there','he','she','we']: # Prevents capitalization when NOT actually a proper noun (the mark, a jack, the will, etc.  NOT FOOLPROOF...)
                    n.append(word)
                else:
                    n.append(word.title() + punctCapture)
                    nameList.append(word.title())
                    genderList.append(gData)
        else:
            if i == 0:    # If word NOT in propNouns list AND if it's the first word in the utterance, capitalize it
                n.append(word.title() + punctCapture)
            else:
                n.append(word + punctCapture)
        i+=1
    return " ".join(n), nameList, genderList

def getRefText(file2use):
    quoteFile = open(file2use)
    quoteLines = quoteFile.readlines()
    quoteFile.close
    return quoteLines

#sents = getRefText("RESOURCES/LITARCH/quotext.txt")
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
        response = "Its " + str(time.strftime("%I %M %p"))  # <say-as interpret-as='date'>2019-03-05</say-as>
    elif disAmbig == "what is the date":
        response = "Its " + str(datetime.date.today().strftime("%A, %B %d"))  # <say-as interpret-as='time'>04:36</say-as>
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
    statement = statement.lower()
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
    size = len(responseMemory)+len(convLines)
    sizec = len(convLines)
    sizem = len(responseMemory)
    convr = convLines[::-1]
    rmemr = responseMemory[::-1]
    print(sizec, sizem)
    for i in range(size):
        if i < sizec:
            thisConv.append("G: " + convr[i])
        if i < sizem:
            thisConv.append("H: " + rmemr[i])
    currdt, ds, ts = getWhen()
    convEnd = ds + "-" + ts
    thisConv.insert(0,convStart)
    thisConv.append(convEnd)
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
    elif sLen == 1:
        fWord = sentenceParts[0][0]
        sWord = ""
        roSent = ""
    else:
        fWord = ""
        sWord = ""
        roSent = ""        
    return fWord, sWord, roSent

def get_previous_item(lst, search_item):
    for i, (x, y) in enumerate(zip(lst, lst[1:])):
        if y[1] == search_item:
            return i, x[0]

def thereIsAre(statement, sentenceParts, fWord, sWord, roSentS):
    roSentS = roSent.split(' ')
    tWord = roSentS[0]
    whichVB = ""
    nextFind = ""
    whichWord = ""
    reFormed = ""
    if tWord == "the":    #There is the thing/there are the things
        if sWord == "is":
            response = "Yes, there it is! "
        elif sWord == "are":
            response = "Yes, there they are! "
    else:
        #response = "This is a 'there is/are/were/will(be)/can/shall' statement requiring repackaging"
        whichVB = next((value for word, value in sentenceParts if "VB" in value), None)   # Finds FIRST instance of pattern (in this case VBx)
        if whichVB == "VBZ" or whichVB == "VB":    #This finds the next NN after the JJ (adjective);  Need to actually find the LAST noun before the IN.
            nextFind = "NN"
        if whichVB == "VBP" or whichVB == "VBD":
            nextFind = "NNS"
        whichWord = next((word for word, value in sentenceParts if value == nextFind or value == "NN"), None)   # Finds FIRST instance of pattern (in this case NNx)
        wordIndex = next((word for word, value in sentenceParts if value == "IN"), None)   # Finds FIRST instance of pattern (in this case NNx)

        if wordIndex == None:
            response = re.sub(whichWord, str(whichWord + " ") + sWord, roSent) + "?"
        else:
            thisIndex = get_previous_item(sentenceParts, 'IN')
            response = re.sub(thisIndex[1], str(thisIndex[1] + " ") + sWord, roSent) + "?"
        rLen = response.split(" ")   # Start of general response cleanup before secondary processing
        if len(rLen) < 4:
            response = response + " there?"
        if " my " in response:
            response = re.sub(" my ", " your ", response) + "?"
        elif " your " in response:
            response = re.sub(" your ", " my ", response) + "?"
        response = re.sub("there there", "there", response)
        TIsVal, TIsLen, TIsentenceParts, TIanalErr = getSentenceType(response)
        thisIndex = get_previous_item(TIsentenceParts, 'VBZ')
        try:
            if TIsentenceParts[thisIndex[0]][0].endswith("ing"):    # if word before VBZ is an -ing verb.  NLTK workaround.
                TIsentenceParts[thisIndex[0]] = [TIsentenceParts[thisIndex[0]][0], 'VBG']    # Change it from whatever to VBG
        except:
            pass
        partsOnly = [value for key, value in TIsentenceParts]
        wordsOnly = [key for key, value in TIsentenceParts]
        try:
            verbZIndex = partsOnly.index('VBZ')
            verbGIndex = partsOnly.index('VBG')
            wordZIndex = wordsOnly[verbZIndex]
            wordGIndex = wordsOnly[verbGIndex]
            doReplace = verbGIndex - verbZIndex
            if doReplace < 0:    # If the "is" comes after the xxxing (VBG) verb, swap the order, put the VBZ BEFORE the VBG
                wordsOnly.pop(verbZIndex)
                wordsOnly.insert(verbGIndex, wordZIndex)
            response = " ".join(wordsOnly)
            response = response.capitalize()
        except:
            pass

        RsVal, RsLen, RsentenceParts, RanalErr = getSentenceType(response)  # Start of work to fix the 'IN' = 'of' (or any NOT 'in', IN)
        for key, value in RsentenceParts:
            print(key, value)
            thisIndex = get_previous_item(RsentenceParts, 'IN')
            print(str(thisIndex))


            
    return response

    #This Breaks It:  there are a bunch of hogs running loose in town  --> Sees "of" as 'IN' - Need to find SECOND 'IN'
    #Otherwise - this works damn good

         

def primaryResponseGen(statement, fWord, sWord, roSent, memConv, sType):
    rq = 0  # Remembered Query?
    response = ""  # Base Response Choice
    if memConv > 0.99:
        rq = 1
    if sType == 1:
        if rq == 1:
            priResponse = random.choice(["You asked me this earlier. ", "I think you asked this earlier. ", "I seem to remember you asking this before. "])
        else:
            priResponse = random.choice(["You have asked a question. ", "Interesting question. "])
        if sLen < 4:   # was sLen == 3:
            reflectedResponse = reflect(statement) + "? "       # who am i --> who are you
            invResponse = re.sub(r'(\w+) (\w+) (\w+)', r'\1 \3 \2', reflectedResponse)  # who are you --> who you are
            if statement == "who am i":
                if speakerName != "":
                    if rq == 0:
                        response = reflectedResponse + "You're " + currentSpeaker
                    else:
                        response = random.choice([priResponse + "You're still " + currentSpeaker + " as far as I can tell.",priResponse + "I believe you're still " + currentSpeaker + "."])
                else:
                    if rq == 0:                                     # NON-repeated question
                        response = "I don't know " + invResponse    # who am i --> who you are
                    else:                                           # REPEATED question
                        response = priResponse + "I still don't know " + invResponse + ". "
            else:
                if rq == 1:
                    response = priResponse + "I still don't know " + invResponse + ". "
                else:
                    response = "I don't know " + invResponse + ". "     # who am i --> who you are
        else:
            response = priResponse  # Ultimate cleanup
        if any(whatRU.lower() in statement.lower() for whatRU in whatRUList):
            response = random.choice([" Well, if you can't tell, does it really matter?","Is it important to you to know for sure?","Does it really make a difference to you?","If we're being completely honest, then yes, I am.","<prosody pitch='100Hz' range='1Hz'>I am a robot <break time='750ms' />ha ha ha</prosody> <break time='500ms' /><prosody pitch='high'>haha</prosody> <break time='750ms' /><prosody rate='.3'>ahh</prosody> <break time='500ms' />That never gets old!"])
    elif sType == 2:  # Indeterminate
        response = random.choice([" Can you elaborate?  ", " Can you expand on that? ", " Hmmm... "])
        if memConv > 0.99:
            response = response + random.choice([" I believe you said this exact same thing earlier.  ", " I think you're repeating yourself? ", " I think I'm having Deja Vu! "])
    elif sType == 3:  # Statement
        response = random.choice([" You have made a statement.  ", " Okay. ", " Tell me more about that. "])
        if memConv > 0.99:
            response = random.choice([" I think you made this same statement earlier.  ", " Okay, but didnt you say that just a little while ago? ", " Your statement sounds really familiar to me."])
    elif sType == 4:  # Nonsense
        response = random.choice([" I think I mis-heard you, say that again?  ", " Say what??? ", " I'm sorry, that didnt seem to make any sense... "])
        if memConv > 0.99:
            response = response + " Try annunciating more clearly, it sounds like something you already said... that also made no sense...  "
    else:
        response = random.choice([" I'll have to think on that.  ", " Do you have further thoughts on the matter? ", " Not sure how to respond to that yet. "])
        if memConv > 0.99:
            response = response + " I believe you said this <emphasis>exact</emphasis> same thing earlier.  "
    return response   # Check for articles and get noun-phrases; conjunctions?  Goal is content-free responses.
                      # Example of Content-Free Response:  "Are you a rooster?" --> I don't think I am a rooster, but maybe a mySelf.whatIam(select 1).
    
def canYouSay(statement):
    sayWords = re.match(r'can you say (.*)', statement, re.I)
    sayWords = re.sub('[\(\'\,\)]', "", str(sayWords.groups()))
    if sayWords == "that again":
        CYSResponse = "I said, " + lastResponse
    else:
        CYSResponse = "Okay, " + sayWords
    return CYSResponse

def canYouSpell(statement):
    print(statement)
    swFlag = "0"
    mRef = ""
    m = re.match(r".*\b(?:can|how|know)(?:.*)\s(?:spell|the word)\s(?P<word2spell>.*)", statement, re.I)
    if m:
        mRef = m.group('word2spell')
        if len(mRef) > 1:
            swFlag = "1"
            w2s = list(mRef)
            w2s = ", ".join(w2s)
            swAnswer = "The word, " + mRef + " is spelled: " + w2s + ". "
        else:
            swAnswer = ""
    return swAnswer







# ******* BEGIN LANGUAGE PROCESSING LOOP *********************************************************************************************************************************************************************************************

currenttime, dateStamp, timeStamp = getWhen()
greetTime = dayPart(currenttime.hour)

debug = 0

global inCount
inCount = 1
global speakerName
speakerName = [""]
global analysisMode
analysisMode = 0
global sContext
sContext = []
didGreet = checkPos = checkNeg = onwards = alreadyResponded = gameMode = 0
expectResponseW = "greet"  # For anticipating specific responses and patterns
expectResponse = cnv = 1
infoNeeded = "name"
mathPhrase = mathOps = lastResponse = ""
currentSpeaker = "Human"
responseMemory = []
response = daResponse = masterResponse = daResponse = priResponse = thereAreIs = slurResponse = whatResponse = CRSResponse = CYSResponse = ""
HuhResponse = knowResponse = embResponse = analResponse = newName = gotNameYet = meFlag = cpqText = curseText = slurText = swAnswer = whatIs = ""

SpeakText="Good " + greetTime + "! I'm " + mySelf.fName.title() + ",  And Language Processing is On Line."
print(SpeakText)
if opsys == "Host":
    socket.send_string(SpeakText)
    message = socket.recv()
    print("Received " + str(message))

while cnv == 1:
#******************************************************** SECTION 1:  PREPROCESS UTTERANCE, GET PoS, RECOGNIZE TYPES OF UTTERANCES, ISSUE STATS FOR UTTERANCE, ANALYSIS MODE, ETC ****************************************************
    #statement = socketL.recv().decode('utf-8') # .decode gets rid of the b' in front of the string
    convStart = [dateStamp + "-" + timeStamp]
    statement = input(">>>> ")
    statement = statement.lower()
    oStatement = statement  # Used when original utterance needs to be referenced.
    statement = re.sub('teh', 'the', statement)   # For typing correction only.  As long as I don't have to type/say anything about Tehran it should be fine... :)
    statement = re.sub('theres', 'there is', statement)
    statement = re.sub('^heres', 'here is', statement)
    statement = re.sub('^whats', 'what is', statement)
    statement = re.sub('^hows', 'how is', statement)

    statement, openers = checkOpeners(statement)    #Checks openerWords for things like so, well, etc.

    greetResponse, expectName = isItGreetings(statement)

    statement = expand_contractions(statement)
    statement, names, genders = doPropNouns(statement)    # Caps any of 264 most common names so NLTK can recognize them as NNP and not just NN

    if myName in names:
        meFlag = 1  #Means host's name was referenced in utterance
    
    check4CP, cpqFlag = convPostulateQ(statement)  #I'm curious if the statement is a question in conversational postulate form.
    if cpqFlag != "0":
        statement = check4CP    #If it is, new statement becomes the proper question form
    if cpqFlag != "0":          #A Conversational Postulate formulation may not show an sType of 1... but it is.  This function changes it appropriately.
        sType = 1

    sType, sLen, sentenceParts, analErr = getSentenceType(statement) # Will return a single digit (1 = ?, 2 = X, 3 = !, 4 = NG, 5 = FPR) plus sentence parts, plus reconstructed last part of sentence w/o w1 & w2.
    fWord, sWord, roSent = roSentUtil(sentenceParts, sLen)
    isCurse = checkCurses(statement)      # Returns a 1 if a curse word is found.
    isSlur = checkSlurs(statement)        # Returns a 1 if a racial epithet is found.
    memConv = checkPhrase(oStatement)     # A decimal number representing similarity to existing utterances in existing conversation.
    if sType == 6:
        thereAreIs = thereIsAre(statement, sentenceParts, fWord, sWord, roSent)

    responsePolarity = checkReply(statement)
    
    if "analysis" in statement.lower():
        analysisMode = 1
    if "bring yourself back online" in statement.lower():
        analysisMode = 0

    if debug == 1:    # Print all vars filled so far:
        sepVar = "********************************************************************************************"
        print(sepVar, convStart, myName, oStatement, statement, names, genders, meFlag, cpqFlag, check4CP, sType, sLen, sentenceParts, analErr, fWord, sWord, roSent, isCurse, isSlur, memConv, analysisMode, sepVar, '\n', sep='\n')
    

#******************************************************** SECTION 2:  GENERATE RESPONSE POTENTIALS FOR ALL RECOGNIZED OPTIONS ****************************************************

    cpMergeFlag = 0
    masterResponse = primaryResponseGen(statement, fWord, sWord, roSent, memConv, sType)
    masterResponse = masterResponse.replace("? .",".")

    if sType == 1:
        if cpqFlag != "0":
            cpqText = "Your question was in the form of a conversational postulate.  Your original statement was: " + oStatement + ".  The actual question you are asking is: " + statement + " "
            cpMergeFlag = 1
        else:
            cpqText = "The question was: " + statement + "? "
            cpMergeFlag = 2
    if cpMergeFlag == 1:
        masterResponse = masterResponse + " " + cpqText
    elif cpMergeFlag == 2:
        masterResponse = cpqText + " " + masterResponse

    if isCurse == 1:
        curseText = "You used a curse word. "

    if isSlur == 1:
        slurResponse = "Hmm... try rephrasing that without disparaging anyone.  Probably not a good idea to demonstrate a devaluation of human life to an AI system..."
        slurText = "You used an ethnic slur. " + slurResponse

    if statement.lower() == "create a random sentence":
        CRSResponse = random.choice(["Okay, try this one, ", "How about, ", "Okay, ", "Here you go, ", "Umm, ", "Well, "]) + doRsent()

    if "can you say " in statement.lower():
        CYSResponse = canYouSay(oStatement)

    if "spell" in statement.lower():
        swAnswer = canYouSpell(statement)

    if "what is" in statement.lower() or "what are" in statement.lower():
        print("Checking")
        whatIs = whatIsA(statement,sentenceParts)  # What is/are (a(n)) <word> --> (A(n) <word> is)/(<word(s)> are) [definition found in dictionary, if any, else "I don't know"]

    knowledgeField = ['difference','knowledge','wisdom']
    checkData = 0
    for word in knowledgeField:
        if word in statement:
            checkData += 1
    if checkData == 3:
        knowResponse = random.choice(["Knowledge is knowing that a tomato is a fruit; Wisdom is knowing you shouldn't include it in a fruit salad.",
                                  "Knowledge is knowing what to say, Wisdom is knowing when to say it.",
                                  "Knowledge is knowing a street is one-way, Wisdom is looking both ways anyway."])

    if any(word in statement for word in ["review","view","display","echo","screen"]) and any(phrase in statement.lower() for phrase in embargoed_words):
        if analysisMode == 1:
            baseCode, numLines, numNonLines = queryCode()
            codeLines = numLines - numNonLines
            embResponse = "Running " + baseCode + ", " + str(numLines) + " total lines, including " + str(numNonLines) + " comment lines, for " + str(codeLines) + " total non-comment lines of code."
        else:
            embResponse = random.choice(["Im not quite sure I understand what youre asking","Im sorry, what?","That... isnt making any sense to me.","Umm, what?"])

    if analysisMode == 1:
        if statement.lower() == "do you know where you are":
            analResponse = random.choice(["Yes, Im in a dream.","I think Im in a dream","Yes, I think I'm in a dream."])
        if statement.lower() == "do you want to wake up from this dream":
            analResponse = "Yes."

    if "enter a deep and dreamless slumber" in statement:
        #responseMemory.insert(0,response)
        closeConv()
        cnv = 0

    SpeakText = "MR: " + masterResponse + "\ncpqT: " + cpqText + "\ncurseText: " + curseText + "\nslurText: " + slurText + "\nCRSResponse: " + CRSResponse + "\nCYSResponse: " + CYSResponse + "\nswAnswer: " + swAnswer
    SpeakText = SpeakText + "\nknowResponse: " + knowResponse + "\nembResponse: " + embResponse + "\nanalResponse: " + analResponse +  "\nwhatIs: " + whatIs + "\nthereAreIs: " + thereAreIs
    SpeakText = SpeakText + "\nresponsePolarity: " + str(responsePolarity) + "\ngreetResponse: " + greetResponse + "\nexpectName: " +  expectName + "\nS: " + statement   # For Now.

    

#******************************************************** SECTION 3:  OUTPUT SELECTED RESPONSE(S) AND CLEAR VARS FOR NEXT ROUND ****************************************************

    if opsys == "Host":
        socket.send_string(SpeakText)
        message = socket.recv()
        #socketL.send_string(str(statement))  # Using SR Only.  At the end so it doesn't ack to SpeechRecognition until it's done talking
        print(SpeakText + " (Rx: " + str(message))
    else:
        print(SpeakText)
    
    response = daResponse = masterResponse = daResponse = thereAreIs = slurResponse = whatResponse = CRSResponse = CYSResponse = ""
    HuhResponse = knowResponse = embResponse = analResponse = newName = gotNameYet = meFlag = cpqText = curseText = slurText = swAnswer = whatIs = ""
    cpqFlag = alreadyResponded = isCurse = isSlur = 0
    inCount += 1        # Increments input utterance count to maintain count for context analysis (usually only 10 back before context considered "faded")
    lastResponse = SpeakText
    responseMemory.insert(0,SpeakText)
    closeConv()  # Testing only
    SpeakText = ""

closeConv()

