import nltk
import re
from nltk.collocations import *
from nltk.corpus import stopwords
from nltk import pos_tag, ne_chunk

stopset = set(stopwords.words('english'))

bigram_measures = nltk.collocations.BigramAssocMeasures()
trigram_measures = nltk.collocations.TrigramAssocMeasures()

with open('../LITARCH/Carroll-Alice_In_Wonderland.txt', 'r', encoding="utf-8") as textFile:
    text1 = textFile.read()
    text1 = text1.lower()
    tokens = nltk.word_tokenize(str(text1))
    tokens = [w for w in tokens if not w in stopset]
    tokens = [w for w in tokens if not w in [' ',',','.','!','-','--',';',':','?','(',')','‘','’','[',']','”','“','and']]
    
#text1 = re.sub("'", "", text1)
#text1 = text1.split(" ")
#text1 = nltk.Text(text1)

finder = BigramCollocationFinder.from_words(tokens)
finder.apply_freq_filter(4)

CLs = finder.nbest(bigram_measures.pmi, 200)  # doctest: +NORMALIZE_WHITESPACE

#tagged_tokens = pos_tag(tokens)
#print(tagged_tokens)            # [(str, tag)]
# [('John', 'NNP'), ('works', 'VBZ'), ('at', 'IN'), ('Intel', 'NNP'), ('.', '.')]

# Semantics Level
#ner_tree = ne_chunk(tagged_tokens)
#print(ner_tree)                # nltk.Tree
# (S (PERSON John/NNP) works/VBZ at/IN (ORGANIZATION Intel/NNP) ./.)

print(CLs)
