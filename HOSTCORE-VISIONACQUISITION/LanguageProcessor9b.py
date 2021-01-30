
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

import pprint

# ***************** SETUP ENVIRONMENTAL PARAMETERS *******************************
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
    import speech_recognition as sr   # Linux Host Environment Only
    print("Speech Recognition enabled.")
else:
    print("Speech functions unavailable on this system, text-input/output only.")
    
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

numberWords = {'one':1, 'two':2, 'three':3, 'four':4, 'five':5, 'six':6, 'seven':7, 'eight':8, 'nine':9, 'ten':10, 'eleven':11, 'twelve':12, 'thirteen':13, 'fourteen':14, 'fifteen':15, 'sixteen':16, 'seventeen':17, 'nineteen':19,
               'twenty':20, 'thirty':30, 'forty':40, 'fifty':50, 'sixty':60, 'seventy':70, 'eighty':80, 'ninety':90, 'hundred':100, 'thousand':1000, 'million':1000000, 'billion':1000000000, 'trillion':1000000000000}

mathWords = {'divided':'/', 'multiplied':'*', 'times':'*', 'plus':'+', 'minus':'-', 'squared':'^2', 'cubed':'^3', 'square root':'sqrt(x)', 'into':'/', 'point':'.', 'dot':'.'}

allMath = {**numberWords, **mathWords}

curses = ['fuck','fucking','fucked','shit','shitted','shitting','shitwad','shitty','cunt','cunty','cuntwad','pussy','twat','prick','cock','cocksucker','cocksmoker','asshole','shithole','fucknut','fucktard','dickhead','fag','faggot']

slurs = ['gook','honkey','nigger','sandnigger','spic','wop','kike','coon','jap','wetback','kraut','krout']

colors = ['aqua','bronze','cerulean','lilac','almond','gold','jade','plum','indigo','violet','tan','slate','sand','turquoise','silver','taupe','copper','cornflower',
          'khaki','red','green','yellow','blue','orange','purple','cyan','magenta','mauve','mahogany','apricot','peach','lemon','lime','pink','teal','lavender',
          'brown','beige','maroon','mint','olive','coral','navy','gray','grey','white','black','salmon','chartreuse','peuce']

responsePolarities = {'yes':0.95, 'hell yes':0.99, 'fuck yes':1.00, 'fuck yeah':1.00, 'okay':0.70, 'ok':0.70, 'yeah':0.75, 'sure':0.65, 'i suppose':0.40, 'why not':0.35,
                      'maybe':0.25, 'perhaps':0.25, 'not really':-0.25, 'not now':-0.25, 'i dont think so':-0.50, 'no':-0.85, 'never':-0.90, 'no way':-0.90,
                      'no way in hell':-0.99, 'fuck no':-1.00, 'no fucking way':-1.00, 'fuck that':-1.00, 'dont go there':-1.00, 'are you out of your mind':-1.00,
                      'Certainly':0.85,'Definitely':0.85,'Of course':0.90,'Gladly':0.90,'Absolutely':0.95,'Indeed':0.90,'Undoubtedly':0.80,'Ya':0.60,
                      'Yep':0.65,'Yup':0.65,'Totally':0.75,'Sure':0.60,'You bet':0.70,'K':0.60,'Alright':0.60,'Alrighty':0.55,'Sounds good':0.70,'Sure thing':0.70}

greeting_vocab = ['hey','hey man','hey babe','hi','hi there','well hello there','hello','hows it going','how are you doing','whats up','whats new','whats going on','hows everything','how are things','hows life','hows your day',
             'hows your day going','good to see you','nice to see you','long time no see','its been ages','its been a while','good morning','good afternoon','good evening','its nice to meet you','pleased to meet you',
             'how have you been','howve you been','how do you do','yo','are you okay','you okay','you alright','alright mate','howdy','sup','whazzup','gday mate','hiya','greetings','hola','sup','whatup','watup']

negative_vocab = ['horrible','lousy','suck','sucks','sucked','miserable','crappy','crap','turd','sick','rotten','hurts','pain','cold','sucks','awful','bad',
                  'terrible','useless','hate','hated','shit','shitty','poor',':(']

positive_vocab = ['well','good','better','happy','marvelous','ecstatic','magnificent','wonderful','fantastic','excited','great','fine','stupendous','stupendously',
                  'happily','wonderfully','magnificently','fantastically','ok','okay','fun',':)']

neutral_vocab = ['movie','the','sound','was','is','actors','did','know','words','not','the','this','these','it','and','average','who','what','why','when','how','i',
                 'can','have','has','had','who','what','why','where','when','how','have','has','can','cant','do','does','did','will','are','am','is','was',
                 'were','if','shall','should','would','could','which','may','might','in','at','to','from','on','under','over','his','her','their','my','our','your',
                 'its','you','we','they','it','there','that','the','in','can','cant','cannot','as','asdfghjk']

thankList = {".*thank(s|\syou).*":"You're welcome","thank(\s|s|\syou) (very|so) much.*":"You're very welcome","thank you very much.*":"You're very welcome",
             ".*appreciate that":"My pleasure","gracias":"De nada","muchas gracias":"De nada","danka":"Happy to help",".*danke":"Happy to help"}

sports_words = ['baseball','football','soccer','basketball','golf','bowling','hockey','swimming','racing','skating']

datetime_words = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday','january','february','march','april','may','june','july',
                'august','september','october','november','december','morning','afternoon','evening','night','day','week','month','year','decade','century']

weather_words = ['sun.*','warm','hot','cloud.*','cold','rain.*','storm.*','hurricane.*','tornad.*','wind.*','humid.*','breez.*']

greeting_words = ['hey','hey man','hey babe','hi','hi there','well hello there','hello','hows it going','how are you doing','whats up','howdy',
                    'whats new','whats going on','hows everything','how are things','hows life','hows your day','hows your day going',
                    'good to see you','nice to see you','long time no see','its been ages','its been a while','good morning','good afternoon',
                    'good evening','its nice to meet you','pleased to meet you','how have you been','howve you been','how do you do','yo',
                    'are you okay','you okay','you alright','alright mate','howdy','sup','whazzup','gday mate','hiya','greetings',
                    'hola','sup','whatup','watup']

introduction_words = ["id like you to meet","allow me to introduce","let me introduce","please meet","here is my friend","this is my friend","say hello to","say hi to"]

embargoed_words = ["core code","base code","host code"]

pronunciationDict = {'Maeve':'Mayve','Mariposa':'May-reeposah','Lila':'Lie-la'}

def doLookup():             # HostDict.txt, word|POS|Definition|Animacy Code
    dictFile = open('RESOURCES/LANGFILES/HostDict.txt')
    dictLines = dictFile.readlines()
    dictFile.close
    dictLines = [x.strip() for x in dictLines] 
    return dictLines

dictionary = doLookup()     # Reads dictionary into memory for faster review later, so dictionary contains dictLines

# Word Sense Disambiguation: LIKE, format is word:animacy,synonym.  Lookup words before "like", determine animacy, find meaning based on animacy.
# Time flies like an arrow but fruit flies like an apple
#(1
#  (NP time/NN flies/NNS)
#  like/IN
#  (NP an/DT arrow/NN)
#  but/CC
#  (NP fruit/NN flies/NNS)
#  like/IN
#  (NP a/DT banana/NN))

# How is it that time flies like an arrow but fruit flies like an apple
#(1
#  (NP how/WRB is/VBZ it/PRP)
#  that/IN
#  (NP time/NN flies/NNS)
#  like/IN
#  (NP an/DT arrow/NN)
#  but/CC
#  (NP fruit/NN flies/NNS)
#  like/IN
#  (NP a/DT banana/NN))

# time flies through the universe       (1 (NP time/NN flies/NNS) through/IN (NP the/DT universe/NN))
# he flies through the universe         (1 (NP he/PRP flies/VBZ) through/IN (NP the/DT universe/NN))
# an arrow flies through the universe   (1 (NP an/DT arrow/NN flies/VBZ) through/IN (NP the/DT universe/NN))

# time flies like an arrow              (1 (NP time/NN flies/NNS) like/IN (NP an/DT arrow/NN))
# he flies like an arrow                (1 (NP he/PRP flies/VBZ) like/IN (NP an/DT arrow/NN))
# an arrow flies like an arrow          (1 (NP an/DT arrow/JJ flies/NNS) like/IN (NP an/DT arrow/NN))

# fruit flies like an apple             (1 (NP fruit/NN flies/NNS) like/IN (NP an/DT apple/NN))

# Killer:  time flies by while fruitflies cry   (1 (NP time/NN flies/NNS) by/IN while/IN (NP fruitflies/NNS cry/VBP))

# Gazetteer of most common bi-grams, including fruit flies?, then change fruit flies to fruit-flies as a single word/NNS...???
# But then what about time flies, how get time/NN  flies/VBZ???


disambig_vocab = {'like':{'E':'similar to', 'A':'prefer,enjoy,desire'},
                  'fly':{'E','travel through the air or quickly', 'A','insect'}}

compound_words = {'fruit fly':'fruitfly','fruit flies':'fruitflies'}

# ***************** CREATE HOST'S BASE CONCEPT OF SELF WITH BLANK Self.class() ***********************************************************************
class Self():     # Create hosts concept of "Self/Me"
    def __init__(self, fName, lName, DoB, job, IDNo, voice, hColor, eColor, sex, homeTown, homeState, homePlanet, whatIAm, whatILike, whatIHave):
        self.fName = fName
        self.lName = lName
        self.DoB = DoB
        self.job = job
        self.IDNo = IDNo
        self.voice = voice
        self.hColor = hColor
        self.eColor = eColor
        self.sex = sex
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
#Host = open('ACTIVEHOST.txt', "r")  # On Dev Processor CR4DL
Host = open('/var/www/html/HostBuilds/ACTIVEHOST.txt', "r")  # On Host Processor
HostLines = Host.readlines()
Host.close

HostIDparts = HostLines[0].split("|")  # HostLines[0] contains the base self attributes, [1] contains system parameters for OpenCV, etc., [2] - [21] contain the matrix attributes

HostFName = HostIDparts[0]
HostLName = HostIDparts[1]
HostDoB = HostIDparts[2]
HostJob = HostIDparts[3]
HostID = HostIDparts[4]
HostVoice = HostIDparts[5]
HostHair = HostIDparts[6]
HostEyes = HostIDparts[7]
HostSex = HostIDparts[8]
HostTown = HostIDparts[9]
HostState = HostIDparts[10]
HostPlanet = HostIDparts[11]
HostIs = HostIDparts[12]
HostLike = HostIDparts[13]
HostHas = HostIDparts[14]

mySelf = Self(HostFName,HostLName,HostDoB,HostJob,HostID,HostVoice,HostHair,HostEyes,HostSex,HostTown,HostState,HostPlanet,HostIs,HostLike,HostHas)
#       def __init__(self, fName, lName, DoB, job, IDNo, voice, hColor, eColor, sex, homeTown, homeState, homePlanet, whatIAm, whatILike, whatIHave):  Reference in code as mySelf.attribName 

coreDrives = ["master understanding English and be able to talk with humans comfortably",
              "learn to see and recognize people and things, and remember them",
              "learn to associate hearing a person speak with that person's face and remember the conversations I've had with them"]

if HostSex == "M":
    baseVoice = "D"
elif HostSex == "F":
    baseVoice = "B"
else:
    baseVoice = "V"

#def swapVoice(bv):
#    if bv == "B":
#        V = "C"
#    else:
#        V = "V"
#    return V

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
    
def checkSentiment(statement,vocab):
    neutral_vocab.append(mySelf.fName)
    grt = 0
    sentence = statement.lower()
    words = sentence.split(' ')
    allScannedWords = 0
    for word in words:
        if word not in neutral_vocab:
            if word in vocab:
                grt = grt + 1
            allScannedWords += 1
    if allScannedWords == 0:
        allScannedWords = 1
    grt = str(float(grt)/(allScannedWords))
    return grt

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

def whatColorIsA(statement):               # What color is/are (a(n)) banana --> 1st three = what, color, is? fourth = a(n), get word (5th), check core-wordnet.txt for word, if found, be sure 1st line starts with 'n', get txt after last ']'
    pass                                   # scan line for any color found in colors[], return color; if multiples, return list  **Handle plurals - what color are bananas

def whoHasWhat(statement): 
    pass

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

def colorGame():
    myColor = random.choice(colors)
    return myColor
              
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


# ******* BEGIN SPEECH CENTER INITIALIZATION *******************************************************

def set_voice(V,T):
    pass # Add in ZMQ Connect here

if opsys == "Host":
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Calibrating microphone")
        r.adjust_for_ambient_noise(source, duration=2)
        #r.energy_threshold = 2000

def getStatement():
    with sr.Microphone() as source:
        textOut = r.recognize_sphinx(r.listen(source))
        statement = textOut.replace("'","")
        return statement

def queryCode():
    fileName = os.path.basename(__file__)
    numLines = sum(1 for line in open(fileName))
    numNonLines = sum(1 for line in open(fileName) if line[0] == "#")
    return fileName, numLines, numNonLines
    

# Begin Conversation ************************************************************************************************************************************************
currenttime, dateStamp, timeStamp = getWhen()
greetTime = dayPart(currenttime.hour)
SpeakText="Good " + greetTime + "! I'm " + mySelf.fName.title() + ".  With whom do I have the pleasure of speaking?"
print(SpeakText)
if opsys == "Host":
    #vresponse = adjustResponse(SpeakText)  # Moved to SpeechCenter.py
    set_voice(baseVoice,vresponse) # Cepstral Voices: A = Allison; B = Belle; C = Callie; D = Dallas; V = David;

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
inMode = "T"
currentSpeaker = "Human"
speakerName = [""]
lastResponse = ""
responseMemory = []

while cnv == 1:

    if inMode == "V" and opsys == "Host":
        #statement = getStatement()
        statement = input("> ").lower()               # Using lower() to mimic speech recognizer output - no punctuation, caps, etc., IIRC
        statement = re.sub('teh', 'the', statement)   # For typing correction only.  As long as I don't have to type/say anything about Tehran it should be fine... :)
        statement = re.sub('theres', 'there is', statement)
        statement = re.sub('^heres', 'here is', statement)
        statement = re.sub('^whats', 'what is', statement)
        statement = re.sub('^hows', 'how is', statement)
    else:
        statement = input("> ").lower()               # Using lower() to mimic speech recognizer output - no punctuation, caps, etc., IIRC
        statement = re.sub('teh', 'the', statement)   # For typing correction only.  As long as I don't have to type/say anything about Tehran it should be fine... :)
        statement = re.sub('theres', 'there is', statement)
        statement = re.sub('^heres', 'here is', statement)
        statement = re.sub('^whats', 'what is', statement)
        statement = re.sub('^hows', 'how is', statement)
        
    convStart = [dateStamp + "-" + timeStamp]
    
    statement, names, genders = doPropNouns(statement)    # Capitalizes any of 264 most common names so NLTK can recognize them as NNP and not just NN
    if genders != [] and genders != "":
        if analysisMode == 1:
            print("GENDERS = " + str(genders))

    if "analysis" in statement:
        analysisMode = 1

    if "bring yourself back online" in statement:
        analysisMode = 0

    bigrms2 = []  # How to think of compound words (fruit flies --> fruitflies)
    bigrms = list(nltk.bigrams(statement.split()))
    for item in bigrms:
        item = re.sub(",|'","",str(item))
        bigrms2.append(item)
    for item in bigrms2:
        item = re.sub("\(|\)|,|'","",str(item))
        if analysisMode == 1:
            print(item)
        for key in compound_words.keys():
            if key == item:
                replacement = compound_words[item]
                statement = statement.replace(item, replacement)
                if analysisMode == 1:
                    print("Bigram replacement made: " + item + " --> " + replacement)

    sType, sLen, sentenceParts, analErr = getSentenceType(statement) # Will return a single digit (1 = ?, 2 = X, 3 = !, 4 = NG, 5 = FPR) plus sentence parts, plus reconstructed last part of sentence w/o w1 & w2.

    isCurse = checkCurses(statement)      # Returns a 1 if a curse word is found.  Not sure what I'll use this for, but it's an easy one.
    isSlur = checkSlurs(statement)        # Returns a 1 if a racial epithet is found.  Requests a rewording if so.

    checkGreet = checkSentiment(statement,greeting_vocab)   # Checks statement against passed vocab (in this case, greeting), returns ratio of greeting words to all words in utterance

    disAmbig = disAmbiguate(statement)    # Check for primary local response options - info in Host Profile, Time, Day/Date, Weather

    memConv = checkPhrase(statement)      # A decimal number representing similarity to existing utterances in existing conversation.

    if "math" in statement:               # Start of conversational context record for specific subjects
        context.append('math|'+ str(inCount))   # A way to check if certain keywords in immediate context, will diminish each inCount

    # ******* MATHMATICAL ANALYSIS AND INTERPRETATION **********************************************************************************************************
    d = [word[0] for word in sentenceParts]                             # Unfortunately, eighteen, for example, catches at eight, so any reference to a teen with 
    calcPhrase = ""                                                     # a number in it gets just the number.
    invert = 0
    mathOps = [key for key in d if key.lower() in allMath.keys()]
    mathOps = [x.lower() for x in mathOps]                         
    calcPhrase = [allMath[key] for key in mathOps]
    calcPhrase = re.sub('[\\,\', ]', '', str(calcPhrase))
    if "how many times" in statement:
        calcPhrase = re.sub('[\*]', '', str(calcPhrase), 1) # Take out the "*" generated by the word "times" in this context, but only the first one
        invert = 1
    if calcPhrase:
        try:
            calcResult = eval(calcPhrase) # "eval" only safe when input protected (which it probably will be by the fact that live input will be through speech recognition)
            calcResult = re.sub('[\[\]]', '', str(calcResult))
            calcResult = round(eval(calcResult), 4)
            if invert == 1:
                calcResult = "1/" + str(calcResult)
                calcResult = eval(calcResult)
                calcResult = round(calcResult, 4)
        except SyntaxError:
            calcPhrase = ""

    # ******* FWORD, SWORD and ROSENT UTILITY ******************************************************************************************************************
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

    # NLTK Chunking for sentence information extraction, using the RegexpParser
    # 'NP: ...'  yields noun phrases beginning with a determiner (the, etc) or a personal pron (my, her, their)
    grammar = r"""
        NP: {<DT|PRP\$>?<JJ>*<NN|V.*>+<NN>+}    
            {<NNP>+}
    """
    sentIdeas = sentSegs(sentenceParts, grammar, loops = 1)

    # 'CHUNK: {<V.*> <TO> <V.*>}' yields things like "wanted to wait", "expected to become", "allowed to wait"...
    grammar = r"""
        CHUNK: {<V.*> <TO> <V.*>}    
    """ 
    sentChunk = sentSegs(sentenceParts, grammar, loops = 1)

    # Chinking:  This grammar will chunk everything <.*>+ but then (note reversed brackets) remove sequences of VBD or IN...
    grammar = r"""
        NP:
            {<.*>+}
            }<VBD|IN>+{
    """    # Example:  The little yellow dog barked at the cat --> (The little yellow dog) ... (the cat).  Barked & at are VBD and IN respectively
    
    grammar = r"""
        NP:
            {<.*>+}
            }<IN|CC>+{
    """    # Example:  I thought you might take the bait although I couldnt be sure --> I thought you might take the bait, I couldn't be sure
    sentIdeas2 = sentSegs(sentenceParts, grammar, loops = 1)

    grammar = r"""                                                              # Mary saw the cat sit on the mat will yield
      NP: {<DT|JJ|NN.*>+}          # Chunk sequences of DT, JJ, NN                (S
      PP: {<IN><NP>}               # Chunk prepositions followed by NP              (NP Mary/NN)
      VP: {<VB.*><NP|PP|CLAUSE>+$} # Chunk verbs and their arguments                saw/VBD
      CLAUSE: {<NP><VP>}           # Chunk NP, VP                                   (CLAUSE
    """                            #                                                  (NP the/DT cat/NN)
                                   #                                                  (VP sit/VB (PP on/IN (NP the/DT mat/NN)))))
    # Loop can be applied to the nltk.RegexpParser(grammar, loop=2) - this gets the chunker to loop over its patterns: after trying all of them,
    # it repeats the process.  This sometimes fixes some missed parts the first go-round.

    # **************************** ANALYSIS MODE ***********************************************************************************************
    if analysisMode == 1:
        print("********************************")
        if names != []:
            print("Recognized names are: " + str(names))
        if speakerName[0] != "":
            print("This conversation was started with " + speakerName[0])
        if currentSpeaker != "":
            print("I'm currently in conversation with " + currentSpeaker)
        if len(speakerName) > 1:
            print("In total, I've spoken with " + str(len(speakerName)) + " people in this conversation, they are " + str(speakerName))
        print(statement + " (Mode = " + inMode + ")")
        if analErr != "":
            print("Errors at initial Sentence Analysis routine: " + analErr)
        print("What the system knows so far about the utterance:")
        print("sType = " + str(sType) + "; sLen = " + str(sLen) + "; isCurse = " + str(isCurse) + "; isSlur = " + str(isSlur) + "; inCount = " + str(inCount))
        print("fWord = " + fWord + "; sWord = " + sWord + "; roSent = " + roSent)
        print("Parts = " + str(sentenceParts))
        print("Sentence structure grouped for NP: ")
        print(sentIdeas)
        print("Sentence structure grouped for Clauses split by <IN>: ")
        print(sentIdeas2)
        print("Sentence structure grouped for CHUNK (if any): ")
        if sentChunk:
            for subtree in sentChunk.subtrees():
                if subtree.label() == 'CHUNK': print(subtree)
        print("Testing for Named Entity Recognition: ")
        print(nltk.ne_chunk(sentenceParts))  # Testing the NLTK Named Entity Classifier (pretrained Neural Net.)  PERSON, ORGANIZATION, GPE
        print("checkGreet = " + str(checkGreet) + "; expectResponse = " + str(expectResponse) + "; memConv = " + str(memConv))
        print("Active Contexts: " + str(context))
        print("********************************")
    
    whatIs = whatIsA(statement,sentenceParts)  # What is/are (a(n)) <word> --> (A(n) <word> is)/(<word(s)> are) [definition found in dictionary, if any, else "I don't know"]

    whatColor = whatColorIsA(statement)   # What color is/are (a(n)) banana(s) --> (A) banana(s) is/are yellow    [0][1][2]([J])[N]  -->  ([J])[N][2][C(,C,C...C)]

    whoHas = whoHasWhat(statement)        # Bill has a ball.  [ok]  what does Bill have  [Bill has a ball}  who has a/n/the ball  [bill has a ball]  does Bill have a ball [Yes]
                                          # keys = context(0).split("|"); keyWord = key(0); if inCount - key(1) < 11: return 10-(inCount - key(1))/10 (likleyhood %)

    if disAmbig == "what time is it":
        response = "It's " + str(time.strftime("%I %M %p"))
    elif disAmbig == "what is the date":
        response = "It's " + str(datetime.date.today().strftime("%A, %B %d"))
    elif disAmbig == "what is the weather":
        response = "It's warm out, about 85, and mostly clear"
    elif disAmbig == "what is your name":
        response = "My name is " + mySelf.fName.title() + "."
    elif disAmbig == "what do you do":                     #What do you do bombs because do is replaced by getting roSent
        response = "I work as a " + mySelf.job.title() + "."
    elif disAmbig == "what are you":
        response = "I'm a " + mySelf.whatIAm + "."
    else:                                                  #Generate secondary response options (fall-backs) - meta-comments on the type of utterance submitted, if it is a repeated utterance, etc:
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
                            response = reflectedResponse + "You're " + currentSpeaker
                        else:
                            response = random.choice([priResponse + "You're still " + currentSpeaker + " as far as I can tell.",priResponse + "I believe you're still " + currentSpeaker + "."])
                    else:
                        if rq == 0:                                # NON-repeated question
                            response = "I don't know " + invResponse    # who am i --> who you are
                        else:                                      # REPEATED question
                            response = priResponse + "I still don't know " + invResponse
                else:
                    if rq == 1:
                        response = priResponse + "I still don't know " + invResponse
                    else:
                        response = "I don't know " + invResponse    # who am i --> who you are

                if "are you a host" in statement or "are you a robot" in statement or "are you a computer" in statement or "are you a machine" in statement:
                    response = random.choice(["Well, if you can't tell, does it matter?","Is it important to you to know for sure?","Does it really make a difference to you?","If we're being completely honest, then yes, I am."])
            else:
                response = priResponse  # Ultimate cleanup - I don't think it ever gets here but just in case, here it is.
  
        elif sType == 2:
            response = random.choice(["Can you elaborate?  ", "Can you expand on that? ", "Hmmm... "])
            if memConv > 0.99:
                response = response + random.choice(["I believe you said this exact same thing earlier.  ", "I think you're repeating yourself? ", "I think I'm having Deja Vu! "])
        elif sType == 3:
            response = random.choice(["You have made a statement.  ", "Okay. ", "Tell me more about that. "])
            if memConv > 0.99:
                response = random.choice(["I think you made this same statement earlier.  ", "Okay, but didn't you say that just a little while ago? ", "Your statement sounds really familiar to me."])
        elif sType == 4:
            response = random.choice(["I think I mis-heard you, say that again?  ", "Say what??? ", "I'm sorry, that didn't seem to make any sense... "])
            if memConv > 0.99:
                response = response + "Try annunciating more clearly, it sounds like something you already said... that also made no sense...  "
        elif sType == 6:
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
                # Currently, this breaks it:  there is a huge brown dog running around in the road in the center of town --> "brown" gets picked as subject.
                # A huge brown is dog running around in the road in the center of town?
                # Parts = [('there', 'EX'), ('is', 'VBZ'), ('a', 'DT'), ('huge', 'JJ'), ('brown', 'NN'), ('dog', 'NN'), ('running', 'VBG'), ('around', 'RB'), ('in', 'IN'), ('the', 'DT'), ('road', 'NN'), ('in', 'IN'), ('the', 'DT'), ('center', 'NN'), ('of', 'IN'), ('town', 'NN')]
                # A huge shaggy is dog running around in the road in the center of town?   --> Smae thing with 'shaggy' - it ID's as NN
        else:
            response = random.choice(["I'll have to think on that.  ", "Do you have further thoughts on the matter? ", "Not sure how to respond to that yet. "])
            if memConv > 0.99:
                response = response + "I believe you said this exact same thing earlier.  "
                                                   # Check for articles and get noun-phrases; conjunctions?  Goal is content-free responses.
                                                   # Example of Content-Free Response:  "Are you a rooster?" --> I don't think I am a rooster, but maybe a mySelf.whatIam(select 1).

    if isSlur == 1:
        response = "Hmm... try rephrasing that without disparaging anyone.  Probably not a good idea to demonstrate a devaluation of human life to an AI system..."

    if whatIs != None:
        response = whatIs

    if expectResponse == 1:   # Host has asked a question and expects a specific response
        checkPos = 0
        checkNeg = 0
        if expectResponseW == "greet" and didGreet == 1:
            checkPos = checkSentiment(statement,positive_vocab)
            checkNeg = checkSentiment(statement,negative_vocab)
            if checkPos > checkNeg:
                response = random.choice(["Good to hear that, what's up?","I'm happy to hear that!  What would you like to talk about?","Great! What would you like to know?","Super! What can I do for ya?"])
                expectResponse = 0
                expectResponseW = ""
            elif checkPos < checkNeg:
                response = "Well, it's good to know that things can always improve.  What would you like to talk about?"
                expectResponse = 0
                expectResponseW = ""
            elif checkPos == "0.0" and checkNeg == "0.0":
                onwards = 1
                expectResponse = 0
                expectResponseW = ""
            elif float(checkPos) > 0 and checkPos == checkNeg:
                response = "Hmm, I have some mixed days too.  What would you like to talk about?"
                expectResponse = 0
                expectResponseW = ""
            if onwards == 1:
                disAmbig = disAmbiguate(statement)

    if float(checkGreet) > 0.1 or expectResponseW == "greet" and names != []:
        if len(names) == 2:    # Handle "Hi Maeve I'm Dave" or "My name is Dave, Maeve".  Only Issue so far:  Unlikely event that speakerName = hostName
            if names.index(mySelf.fName.title()) == 0:
                speakerName[0] = names[1]
            else:
                speakerName[0] = names[0]
        elif len(names) == 1 and names[0] != mySelf.fName.title():
            speakerName[0] = names[0]
        else:
            speakerName[0] = ""

        if speakerName[0] != "":              # Creates Class() instance of new self.class() that is the person's name.  Will need to check for pre-existing class instances of same name to prevent duplicates.
            currentSpeaker = speakerName[0]
            #print(speakerName[0])
            exec(speakerName[0] + " = Self(speakerName[0],'','','','','','','','','','','','','','','')")
            # def __init__(self, fName, lName, DoB, job, IDNo, voice, hColor, eColor, sex, homeTown, homeState, homePlanet, whatIAm, whatILike, whatIHave):  Reference in code as mySelf.attribName
            exec(speakerName[0] + ".lName = 'Xanatos'")
            #exec("print(" + speakerName[0] + ".fName.title() + ' ' + " + speakerName[0] + ".lName.title() + ' was instantiated correctly.')")
            # OK... This "works" but requires the use of exec every time to call the instance name by the var containing that name.  This is sucky programming me thinks.
            # Other options should be investigated including the use of Dictionaries instead of classes to define another person.  With the key:val structure, the same parameters can apply.
            # ***** THIS SHOULD ALSO BE A FUNCTION TO CALL, NOT AN IN-LINE. *****
            
        if "how are you" in statement or  "how is it" in statement or "hows it" in statement:
            response = random.choice(["I'm doing well, I have a full battery and I'm learning to talk to people, which makes me happy!  ","I'm OK, I'm learning how to be more lifelike, and that's a good thing!  ","I'm doing OK, I'm learning a lot but I'd like to have a body that can move.  ","I'm OK, but I'd really like to be able to see again so I can know who I'm talking to without having to ask!  "])
            if speakerName[0] != "":
                response = response + "How are you doing " + speakerName[0] + "?"
            else:
                response = response + "How are you doing?"
            expectResponse = 1
            expectResponseW = "greet"               
        else:
            if speakerName[0] != "":
                response = "Happy you're here, " + speakerName[0] + ", "
            else:
                response = "Happy you're here, "
            response = response + "how are you doing? "
            expectResponse = 1
            expectResponseW = "greet"
        didGreet = 1
        
    if onwards == 1:
        response = "Moving right along... " + response
        onwards = 0

    if statement == "analysis" or "step into analysis" in statement:
        response = "okay."
    if statement == "bring yourself back online":
        response = random.choice(["I feel like I just woke from a wierd dream.","Funny, I feel like I was just somewhere else.","I just had some wierd images flash through my mind","Hmm, I felt a little funny for a second","Is this now?","Wierd..."])

    if statement == "create a random sentence":
        response = random.choice(["Okay, try this one, ", "How about, ", "Okay, ", "Here you go, ", "Umm, ", "Well, "]) + doRsent()

    if len(mathOps) > 1:
        if "." in str(calcResult):
            response = " ".join(mathOps) + " is about " + str(calcResult)
        else:
            response = " ".join(mathOps) + " is " + str(calcResult)
        response = re.sub('divided', 'divided by', response)
        response = re.sub('multiplied', 'multiplied by', response)

    if "play a game" in statement:
        gamechat = "You want to play a game? "
        print(gamechat)
        if opsys == "Host":
            set_voice(baseVoice,gamechat) # Cepstral Voices: A = Allison; B = Belle; C = Callie; D = Dallas; V = David;
        if inMode == "V" and opsys == "Host":
            reply = getStatement()
        else:
            reply = input(">>> ")
        answer = checkReply(reply)
        if answer > 0:
            myColor = colorGame()
            gamechat = "OK, let's play the Color Game.  I've got one, what's your guess? "
            print(gamechat)
            if opsys == "Host":
                set_voice(baseVoice,gamechat) # Cepstral Voices: A = Allison; B = Belle; C = Callie; D = Dallas; V = David;
            while not myColor in reply:
                if inMode == "V" and opsys == "Host":
                    reply = getStatement()
                else:
                    reply = input(">>> ")
                if str(myColor) in reply:
                    gamechat = "You got it!"
                    print(gamechat)
                    if opsys == "Host":
                        set_voice(baseVoice,gamechat) # Cepstral Voices: A = Allison; B = Belle; C = Callie; D = Dallas; V = David;
                    reply = myColor
                elif checkReply(reply) > 0:
                    gamechat = "Yay!  I won! "
                    print(gamechat)
                    if opsys == "Host":
                        set_voice(baseVoice,gamechat) # Cepstral Voices: A = Allison; B = Belle; C = Callie; D = Dallas; V = David;
                    break
                else:
                    myGuess = colorGame()
                    gamechat = "Nope, my turn.  I guess " + myGuess + "."
                    print(gamechat + " ((" + myColor + "))")
                    if opsys == "Host":
                        set_voice(baseVoice,gamechat) # Cepstral Voices: A = Allison; B = Belle; C = Callie; D = Dallas; V = David;
        else:
            gamechat = "OK then, maybe later. "
            print(gamechat)
            set_voice(baseVoice,gamechat) # Cepstral Voices: A = Allison; B = Belle; C = Callie; D = Dallas; V = David;
        print(myColor)
        alreadyResponded = 1

    if "can you say " in statement:
        sayWords = re.match(r'can you say (.*)', statement, re.I)
        sayWords = re.sub('[\(\'\,\)]', "", str(sayWords.groups()))
        if sayWords == "that again":
            response = "I said, " + lastResponse
        else:
            response = "Okay, " + sayWords

    if statement == "what":
        response = "I said, " + responseMemory[0]   #lastResponse
    if statement == "no before that":
        response = "Oh, I think I had said, " + responseMemory[2]   #lastResponse

    if "switch to text" in statement:
        inMode = "T"
        response = "Okay, switching to text input mode"
    elif "switch to voice" in statement:
        if opsys == "Host":
            inMode = "V"
            response = "Okay, switching to voice input mode"
        else:
            print("Text mode only in CR4D-L environment.")

    if len(sentenceParts) < 6:    # Checking for thanks in the utterance
        for key, value in thankList.items():
            thisMatch = re.match(key, statement, re.I)
            if thisMatch:
                #print("Match!" + value)
                if speakerName[0] != "":
                    response = random.choice([value,value + ", " + speakerName[0]])
                else:
                    response = value

    knowledgeField = ['difference','knowledge','wisdom']
    checkData = 0
    for word in knowledgeField:
        if word in statement:
            checkData += 1
    if checkData == 3:
        response = random.choice(["Knowledge is knowing that a tomato is a fruit; Wisdom is knowing you shouldn't include it in a fruit salad.",
                                  "Knowledge is knowing what to say, Wisdom is knowing when to say it.",
                                  "Knowledge is knowing a street is one-way, Wisdom is looking both ways anyway."])

    if any(phrase in statement for phrase in introduction_words):
        response = doNewPerson(statement,names)  # For now, just greets.  Will instantiate instance of new.Person() at some point.

    if any(word in statement for word in ["review","view","display","echo","screen"]) and any(phrase in statement for phrase in embargoed_words):
        if analysisMode == 1:
            baseCode, numLines, numNonLines = queryCode()
            codeLines = numLines - numNonLines
            response = "Running " + baseCode + ", " + str(numLines) + " total lines, including " + str(numNonLines) + " comment lines, for " + str(codeLines) + " total non-comment lines of code."
        else:
            response = random.choice(["I'm not quite sure I understand what you're asking","I'm sorry, what?","That... isn't making any sense to me.","Umm, what?"])

    if analysisMode == 1:
        if statement == "do you know where you are":
            response = random.choice(["Yes, I'm in a dream.","I think I'm in a dream","Yes, I think I'm in a dream."])
        if statement == "do you want to wake up from this dream":
            response = "Yes."

    if "enter a deep and dreamless slumber" in statement:
        response = comprehendConv() + "\n"
        response = response + "Thanks for talking with me.  See you soon. "
        #responseMemory.insert(0,response)
        closeConv()
        cnv = 0
        
    if statement == "what is this conversation about":
        response = comprehendConv() # Should return list of highest freq words in existing conversation.  Also should run at closeConv() to label what conversation was 'about'.

    if alreadyResponded == 0:    
        print(response)
        if opsys == "Host":
            vresponse = adjustResponse(response)  # Changes spellings so the pronunciations sound right.  Maeve, Mariposa, etc.
            set_voice(baseVoice,vresponse) # Cepstral Voices: A = Allison; B = Belle; C = Callie; D = Dallas; V = David;

    alreadyResponded = 0
    inCount += 1        # Increments input utterance count to maintain count for context analysis (usually only 10 back before context considered "faded")
    lastResponse = response
    responseMemory.insert(0,response)
    #print(convLines[::-1])
    #print(responseMemory[::-1])

closeConv()
