#!/usr/bin/python
# Updated 6/30/2019 in Maine to read from ACTIVEHOST.txt in \var\www\html (controlled by BPM)
# Set up for option to use zmq with SpeakCenter.py
# Note that SpeechCenter.py can't be F5'd to run from IDLE else running this TLP code will
# eclipse the SpeechCenter.py code.  SpeechCenter.py must be run from a Terminal Window by
# running "python SpeechCenter.py &"

# ***************** IMPORT ALL REQUIRED DEPENDENCIES ******************************
from difflib import SequenceMatcher as SM
import nltk
from nltk.tag import pos_tag
import calendar
import datetime
from dateutil.relativedelta import relativedelta
#from datetime import timedelta
import random
import time
import zmq
import os
import re

# ***************** SETUP NETWORKING *******************************
context = zmq.Context()

print("Establishing Language Network Node")
socketL = context.socket(zmq.REP)
socketL.bind("tcp://*:5558")  # Listen on 5558 for input - usually from the Speech Recognizer.

print("Connecting to Speech Center")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555") # Send to 5555 to speak

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
    'WNNP':{'were':2,'was':2,'will':2,'is':2,'are':4,'his':2,'her':2,'their':2,'my':2,'our':3,'your':3,'its':3,'i':2,'you':3,'we':2,'they':2,'it':2,'there':2,'that':2,'the':2,'in':4,'can':3,'cant':3,'cannot':3,'am':4,'do':4,'did':3,'does':2}
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

file_name = '/home/pi/Desktop/HOSTCORE/namesKnown.txt'   # In prep to allow new names to be learned and written to text list for premanent retention
propNouns = {}
with open(file_name) as file:
    for line in file:
        line = line.replace('\n','')
        pairs = line.split(":")
        propNouns.update(zip(pairs[0::2], pairs[1::2]))

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

disambig_vocab = {'like':{'E':'similar to', 'A':'prefer,enjoy,desire'},
                  'fly':{'E','travel through the air or quickly', 'A','insect'}}

compound_words = {'fruit fly':'fruitfly','fruit flies':'fruitflies'}

def doLookup(): # HostDict.txt, word|POS|Definition|Animacy Code
    dictFile = open('/home/pi/Desktop/HOSTCORE/RESOURCES/LANGFILES/HostDict.txt')
    dictLines = dictFile.readlines()
    dictFile.close
    dictLines = [x.strip() for x in dictLines] 
    return dictLines

dictionary = doLookup()     # Reads dictionary into memory for faster review later, so dictionary contains dictLines

def expand_contractions(s, contractions_dict=contractions_dict):
    def replace(match):
        return contractions_dict[match.group(0)]
    return contractions_re.sub(replace, s)

def convPostulateQ(statement):
    cpqFlag = "0"
    mRef = ""
    #m = re.match(r".*\bi'(?:m|ve) (?:.*)\s+if\s+(?P<actualQ>.*)(?: |.|)", statement)
    m = re.match(r".*\b(?:i'(?:m|ve)|(?:im|i am|you are|he is|i have)) (?:.*)\s+(?:if|whether)\s+(?P<actualQ>.*)(?: |.|)", statement)
    if m:
        mRef = m.group('actualQ')
        if len(mRef) > 1:
            cpqFlag = "1"
        m2 = re.sub(r'(i|you|he|she|they|it) (am|are|can|may|might|will|have|should|could|would|know) (.*)', r'\2 \1 \3', mRef)  # Contains corrected form of question
        m3 = m2.split(" ")
        if len(m3) == 2:
            m2 = re.sub(r'(i|you|he|she|they|it) (am|are|can|may|might|will|have|should|could|would|know)', r'\2 \1', m2)
        m2 = re.sub(r'(have|know) (you|I) (.*)', r'do \2 \1 \3', m2)  # Contains corrected form of question
        m3 = m2.split(" ")
        m4 = m2[0].capitalize() + m2[1:] + "?"
        m4 = re.sub(r'\.\?', '?', m4)
        return m4, cpqFlag
    else:
        return "","0"


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
Host = open('/home/pi/Desktop/HOSTCORE/ACTIVEHOST.txt', "r")  # On Host Processor
HostLines = Host.readlines()
Host.close

#Maeve Millay|F|36|Madam at The Mariposa|AC50000487105|B|Brown|Brown|Black|Sweetwater|Arizona|Earth|developing|learning|chips|
#     0      |1| 2|          3          |      4      |5|  6  |  7  |  8  |    9     |   10  |  11 |     12   |   13   |  14 |
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

coreDrives = ["master understanding English and be able to talk with humans comfortably",
              "learn to see and recognize people and things, and remember them",
              "learn to associate hearing a person speak with that person's face and remember the conversations I've had with them"]


# ***************** CORE LANGUAGE FUNCTIONS FOR PROCESSING HEARD SPEECH *************************************************************

def dateTimeDelta(new, old):  # For "Last Contact" calculations - when host saw a person last
    if new = "now":
        strDateStamp = str(datetime.datetime.now()).split(".")
        strDateStamp = strDateStamp[0]
        new = strDateStamp    #print(strDateStamp) '2020-08-07 12:00:56' Would be now by way of format example
    start = datetime.datetime.strptime(new, '%Y-%m-%d %H:%M:%S')
    ends = datetime.datetime.strptime(old, '%Y-%m-%d %H:%M:%S')
    diff = relativedelta(start, ends)
    #print("Time elapsed is %d years %d month %d days %d hours %d minutes %d seconds" % (diff.years, diff.months, diff.days, diff.hours, diff.minutes, diff.seconds))
    return diff.years, diff.months, diff.days, diff.hours, diff.minutes, diff.seconds

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

#sents = getRefText("RESOURCES/LITARCH/quotext.txt")
sents = getRefText("/home/pi/Desktop/HOSTCORE/RESOURCES/LANGFILES/disambig.txt")

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
    newConvFile = '/home/pi/Desktop/HOSTCORE/logs/ConvLog_' + dateStamp + "-" + timeStamp + '.txt'
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

def primaryResponseGen(statement, fWord, sWord, roSent, memConv, sType, sLen):
    rq = 0  # Remembered Query?
    DKR = 0 # Don't Know Response - Flagged for when it should not be spoken (1)
    response = ""  # Base Response Choice
    priResponse = ""
    if memConv > 0.99:
        rq = 1
    if sType == 1:
        if rq == 1:
            priResponse = random.choice(["You asked me this earlier. ", "I think you asked this earlier. ", "I seem to remember you asking this before. "])
        else:
            priResponse = random.choice(["I have no answer. ", "Interesting question. No clue.", "I have no answer for that yet. ", "Well, all I can say is Google is your friend. "])
        if sLen < 12:   # was sLen == 3:
            reflectedResponse = reflect(statement) + "? "       # who am i --> who are you
            invResponse = reflect(fWord + " " + roSent + " " + sWord) + ". "  #who am i --> who you are
            invResponse = re.sub(r"(\?|\.)", "", invResponse)
            invResponse = invResponse.strip()
            irWords = invResponse.split(" ")
            irwl = len(irWords)
            invResponse = invResponse.rsplit(' ', 1)[0]
            invResponse = irWords[irwl-1] + " " + invResponse
            irWords = invResponse.split(" ")
            print(irWords[0])
            if irWords[0] == "me":
                irWords[0] = "I"
                invResponse = " ".join(irWords)
            print(invResponse)
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
                    response = "I don't know if " + invResponse    # who am i --> who you are
            if "are you a host" in statement or "are you a robot" in statement or "are you a computer" in statement or "are you a machine" in statement:
                response = random.choice([" Well, if you can't tell, does it really matter?","Is it important to you to know for sure?","Does it really make a difference to you?","If we're being completely honest, then yes, I am.","<prosody pitch='100Hz' range='1Hz'>I am a robot <break time='750ms' />ha ha ha</prosody> <break time='500ms' /><prosody pitch='high'>haha</prosody> <break time='750ms' /><prosody rate='.3'>ahhh</prosody> <break time='500ms' />That never gets old!"])
        else:
            response = priResponse  # Ultimate cleanup - I don't think it ever gets here but just in case, here it is.
    elif sType == 2:  # Indeterminate
        response = random.choice([" Can you elaborate?  ", " Can you expand on that? ", " Hm... "])
        if memConv > 0.99:
            response = response + random.choice([" I believe you said this exact same thing earlier.  ", " I think youre repeating yourself? ", " I think Im having Deja Vu! "])
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
        DKR = 1
        if memConv > 0.99:
            response = response + " I believe you said this <emphasis>exact</emphasis> same thing earlier.  "
    print("PriResp: " + priResponse + " | " + response)
    return response, DKR, priResponse   # Check for articles and get noun-phrases; conjunctions?  Goal is content-free responses.
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

# ******* BEGIN LANGUAGE PROCESSING LOOP *******************************************************

currenttime, dateStamp, timeStamp = getWhen()
greetTime = dayPart(currenttime.hour)

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
IDKflag, response, daResponse, masterResponse = "", "", "", ""
daResponse, thereAreIs, slurResponse = "", "", ""
whatResponse, CRSResponse, CYSResponse, swAnswer = "", "", "", ""
HuhResponse, knowResponse, embResponse, analResponse = "", "", "", ""
GreetResponse, DKR = "", ""


SpeakText="Good " + greetTime + "! I'm " + mySelf.fName.title() + ",  And Language Processing is On Line."
print(SpeakText)
socket.send_string(SpeakText)
message = socket.recv().decode('utf-8')
print("Received " + str(message))

while cnv == 1:
    print("Waiting for utterance.")
    statement = socketL.recv().decode('utf-8') # .decode gets rid of the b' in front of the string
    socketL.send_string(str(statement))
    #statement = input("> ")
    statement = statement.lower()
    statement = re.sub('teh', 'the', statement)   # For typing correction only.  As long as I don't have to type/say anything about Tehran it should be fine... :)
    statement = re.sub('theres', 'there is', statement)
    statement = re.sub('^heres', 'here is', statement)
    statement = re.sub('^whats', 'what is', statement)
    statement = re.sub('^hows', 'how is', statement)

    oStatement = statement  # Used when original utterance needs to be referenced.
    statement = expand_contractions(statement)
    statement, names, genders = doPropNouns(statement)    # Caps any of 264 most common names so NLTK can recognize them as NNP and not just NN
    check4CP, cpqFlag = convPostulateQ(statement)
    if cpqFlag != "0":
        statement = check4CP
    print("Pre-processed Statement = " + statement)

    sType, sLen, sentenceParts, analErr = getSentenceType(statement) # Will return a single digit (1 = ?, 2 = X, 3 = !, 4 = NG, 5 = FPR) plus sentence parts, plus reconstructed last part of sentence w/o w1 & w2.
    if cpqFlag != "0":
        sType = 1
    fWord, sWord, roSent = roSentUtil(sentenceParts, sLen)
    isCurse = checkCurses(statement)      # Returns a 1 if a curse word is found.  Not sure what I'll use this for, but it's an easy one.
    isSlur = checkSlurs(statement)        # Returns a 1 if a racial epithet is found.  Requests a rewording if so.
    checkGreet = checkSentiment(statement,greeting_words)   # Checks statement against passed vocab (in this case, greeting), returns ratio of greeting words to all words in utterance
    print(checkGreet)
    print(names)
    memConv = checkPhrase(oStatement)      # A decimal number representing similarity to existing utterances in existing conversation.

    whatIs = whatIsA(statement,sentenceParts)  # What is/are (a(n)) <word> --> (A(n) <word> is)/(<word(s)> are) [definition found in dictionary, if any, else "I don't know"]

    if sType == 6:
        thereAreIs = thereIsAre(statement, sentenceParts, fWord, sWord, roSent)
    
    disAmbig = disAmbiguate(statement)

    print("disAmbig = " + disAmbig)

    if disAmbig != "DLLATM":
        daResponse = disAmbResponse(disAmbig)

    print("daResponse = " + daResponse)

    if daResponse == "DLLATM" or daResponse == "": #Generate secondary response options (fall-backs) - meta-comments on the type of utterance submitted, if it is a repeated utterance, etc:
        masterResponse, DKR, priResponse = primaryResponseGen(statement, fWord, sWord, roSent, memConv, sType, sLen)
    print(masterResponse)
    
    if isSlur == 1:
        slurResponse = "Hmm... try rephrasing that without disparaging anyone.  Probably not a good idea to demonstrate a devaluation of human life to an AI system..."

    if whatIs != None:
        whatResponse = whatIs

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
            print(currentSpeaker)
            
        if "how are you" in statement or  "how is it" in statement or "hows it" in statement:
            GreetResponse = random.choice(["I'm doing well, I have a full battery and I'm learning to talk to people, which makes me happy!  ","I'm OK, I'm learning how to be more lifelike, and that's a good thing!  ","I'm doing OK, I'm learning a lot but I'd like to have a body that can move.  ","I'm OK, but I'd really like to be able to see again so I can know who I'm talking to without having to ask!  "])
            if speakerName[0] != "":
                GreetResponse = GreetResponse + "How are you doing " + speakerName[0] + "?"
            else:
                GreetResponse = GreetResponse + "How are you doing?"
            expectResponse = 1
            expectResponseW = "greet"               
        else:
            if speakerName[0] != "":
                GreetResponse = "Happy you're here, " + speakerName[0] + ", "
            else:
                GreetResponse = "Happy you're here, "
            GreetResponse = GreetResponse + "how are you doing? "
            expectResponse = 0
            expectResponseW = ""
        didGreet = 1
        
    if onwards == 1:
        response = "Moving right along... " + response
        onwards = 0

    if statement == "analysis" or "step into analysis" in statement:
        response = "okay."
    if statement == "bring yourself back online":
        response = random.choice(["I feel like I just woke from a wierd dream.","Funny, I feel like I was just somewhere else.","I just had some wierd images flash through my mind","Hmm, I felt a little funny for a second","Is this now?","Wierd..."])

    if statement == "create a random sentence":
        CRSResponse = random.choice(["Okay, try this one, ", "How about, ", "Okay, ", "Here you go, ", "Umm, ", "Well, "]) + doRsent()

    if "can you say " in statement:
        CYSResponse = canYouSay(oStatement)

    if "spell" in statement:
        swAnswer = canYouSpell(statement)

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
        if cpqFlag != "0":
            SpeakText = "I think I heard you ask me a question, but in the form of a conversational postulate.  Your original statement was: " + oStatement + ".  The actual question you are asking is: " + statement + " "
            SpeakText = SpeakText + " " + priResponse
        else:
            SpeakText = "I think I heard you ask me a question. The question was: " + statement + "? "
            SpeakText = SpeakText + " " + priResponse
    elif sType == 2 or sType == 3 or sType >= 5:
        SpeakText = "I think I heard you say, " + statement + ". "
    elif sType == 4:
        SpeakText = "I think I misheard you because it sounded like you said, " + statement + ". "

    if isCurse == 1:
        SpeakText = SpeakText + "You also used a curse word. "

    if isSlur == 1:
        SpeakText = SpeakText + "You also used an ethnic slur. " + slurResponse

    if len(GreetResponse) >= 3:
        SpeakText = GreetResponse + ". "
        IDKflag = "1"

    if len(daResponse) >= 3:
        SpeakText = SpeakText + "The answer is, " + daResponse + ". "
        IDKflag = "1"

    if len(whatResponse) >= 3:
        SpeakText = SpeakText + "The answer is, " + whatResponse + ". "
        IDKflag = "1"

    if len(CYSResponse) >= 4:
        SpeakText = SpeakText + " And, " + CYSResponse + ". "
        IDKflag = "1"

    if len(swAnswer) >= 4:
        SpeakText = SpeakText + " And, " + swAnswer + ". "
        IDKflag = "1"

    if len(thereAreIs) >= 4 and sType == 6:
        SpeakText = SpeakText + " And, my response would be, " + thereAreIs + ". "
        IDKflag = "1"

    if len(CRSResponse) >= 4:
        SpeakText = SpeakText + " So, here is a random sentence: " + CRSResponse + ". "
        IDKflag = "1"

    if len(knowResponse) >= 4:
        SpeakText = SpeakText + " " + knowResponse + ". "
        IDKflag = "1"
    
    if len(HuhResponse) >= 4:
        SpeakText = SpeakText + " " + HuhResponse + ". "
        IDKflag = "1"

    SpeakTexto = SpeakText
    if len(masterResponse) >= 4:
        if DKR == "0":
            SpeakText = SpeakText + " " + masterResponse + ". "
        if DKR == "1":   # I Don't Know flag.  Prevents the IDK response if a response WAS given.
            if IDKflag == "1":
                SpeakText = SpeakTexto
            else:
                SpeakText = SpeakText + " " + masterResponse + ". "
        
    print("embResponse = " + embResponse)
    print("analResponse = " + analResponse)

    socket.send_string(SpeakText)
    message = socket.recv().decode('utf-8')
    #socketL.send_string(str(statement))  # This was up top.  Put this at the end so it doesn't ack to SpeechRecognition until it's done talking
    print(SpeakText)
          
    IDKflag, response, daResponse, masterResponse = "", "", "", ""
    daResponse, thereAreIs, slurResponse = "", "", ""
    whatResponse, CRSResponse, CYSResponse = "", "", ""
    HuhResponse, knowResponse, embResponse, analResponse = "", "", "", ""
    GreetResponse, DKR, priResponse = "", "", ""
    alreadyResponded = 0
    inCount += 1        # Increments input utterance count to maintain count for context analysis (usually only 10 back before context considered "faded")
    lastResponse = SpeakText
    responseMemory.insert(0,SpeakText)
    closeConv()  # Testing only
    SpeakText = ""

closeConv()

# Using SSML with Cepstral Voices:  https://www.cepstral.com/en/tutorials/view/ssml

# This document shows only the stuff tested to work with Cepstral.  There's more - but it won't pass muster.

# Adjusting Voice Speed

# I am now <prosody rate='x-slow'>speaking at half speed.</prosody>
# I am now <prosody rate='slow'>speaking at 2/3 speed.</prosody>
# I am now <prosody rate='medium'>speaking at normal speed.</prosody>
# I am now <prosody rate='fast'>speaking 33% faster.</prosody>
# I am now <prosody rate='x-fast'>speaking twice as fast</prosody>
# I am now <prosody rate='default'>speaking at normal speed.</prosody>
# I am now <prosody rate='.42'>speaking at 42% of normal speed.</prosody> '42%' Does NOT work
# I am now <prosody rate='1.5'>speaking 1.5 times as fast</prosody>
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

# Phonetic Pronunciation:

# You say <phoneme ph='t ah0 m ey1 t ow0'>tomato</phoneme>, I say <phoneme ph='t ah0 m aa1 t ow0'>tomato</phoneme>

# Breeak/pause examples:

#   Step 1, take a deep breath. <break time='2000ms'/> Step 2, exhale. Step 3, take a deep breath again. <break strength='weak'/> Step 4, exhale.

# The following example is spoken as "Twelve thousand three hundred forty five":

#   <say-as interpret-as='cardinal'>12345</say-as>

# The following example is spoken as "First":

#   <say-as interpret-as='ordinal'>1</say-as>

# The following example is spoken as "March 5th, Two Thousand Nineteen":

#   <say-as interpret-as='date'>2019-03-05</say-as>

#   <say-as interpret-as='time'>04:36</say-as>

# Emphasis:

#   That is a <emphasis> big </emphasis> car!  That is a <emphasis level='strong'> huge </emphasis> bank account!

# AUDIO:

# The following are the currently supported settings for audio:

# Format: MP3 (MPEG v2)
# 24K samples per second
# 24K ~ 96K bits per second, fixed rate

# Format (deprecated): WAV (RIFF)
# PCM 16-bit signed, little endian
# 24K samples per second

# For all formats:
# Single channel is preferred, but stereo is acceptable.
# The following example outputs the sound stored at the src URL:

#   <audio src="sounds/animals/cat_purr_close.mp3">
#     <desc>a cat purring</desc>
#     PURR (sound didn't load)
#   </audio>

# To add or edit custom pronunciation of specific words with your Cepstral voice, you can create (or edit) a lexicon.txt file found in each voice's data directory.

# On Linux platforms, it's typically at:

# /opt/swift/voices/David/lexicon.txt

# This file will allow you to change pronunciation for a single voice (so each voice may have its own seperate list of pronunciations).

# * Note: Once an entry is added to a voice's lexicon file, all occurrences of that word will be pronounced by that voice using the specified phonemes.

# * Note: You must re-load the voice for changes to take effect. The procedure for reloading a voice varies depending on the context. Typically you must quit and re-launch your application to reload a voice. If you are using the voices under Apple Macintosh OS X through the SpeechManager interface, to reload the voice you may have to log out of the system and log back in.


