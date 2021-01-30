# python retest.py

import re

testtext = "Isn't this is a sentence with <break time='3s' /> three second's delay."

p = re.compile(r'<|>*')     # ['This is a sentence with a ', "break time='3s' /", ' three second delay.']
parts = p.split(testtext)

print(parts[0],parts[1],parts[2])             # break time='3s' /   FUTURE:  p = re.compile(r'(\<(/?[^\>]+)\>*)') matches full tag

parts[0] = parts[0].replace("'","")
parts[2] = parts[2].replace("'","")

fixed = parts[0] + "<" + parts[1] + ">" + parts[2]
print(fixed)





    

