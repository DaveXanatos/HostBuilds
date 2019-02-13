
#!/usr/bin/python

# ***************** IMPORT ALL REQUIRED DEPENDENCIES ******************************
from difflib import SequenceMatcher as SM
import nltk
from nltk.tag import pos_tag

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


while 1 == 1:
        statement = input("> ").lower()               # Using lower() to mimic speech recognizer output - no punctuation, caps, etc., IIRC
        statement = re.sub('teh', 'the', statement)   # For typing correction only.  As long as I don't have to type/say anything about Tehran it should be fine... :)
        statement = re.sub('theres', 'there is', statement)
        statement = re.sub('^heres', 'here is', statement)
        statement = re.sub('^whats', 'what is', statement)
        statement = re.sub('^hows', 'how is', statement)
		
		sVal, sLen, sentenceParts, analErr = getSentenceType(statement)  
        
