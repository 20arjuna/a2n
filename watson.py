import json
import re
import operator
import re
from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1 import Features, KeywordsOptions

def findKeywords(filename):
    file = open(filename, "r")
    outputfile = open("jsonOutput.json", "w")
    keywords = []

    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2018-11-16',
        iam_apikey='m620e2y3lML5qG_oRJy9JERrlR0-159j3vJVrtPJkhJg',
        url='https://gateway-wdc.watsonplatform.net/natural-language-understanding/api'
        )

    response = natural_language_understanding.analyze(
        text = file.read(),
        features=Features(keywords=KeywordsOptions(sentiment=False,emotion=False))).get_result()

    #print(json.dumps(response, indent=2))
    file.close()
    outputfile.write(json.dumps(response, indent=2))
    outputfile.close()
    with open("jsonOutput.json", "r") as read_file:
        data = json.load(read_file)
    keywordslist = data['keywords']
    for x in keywordslist:
        keywords.append(x['text'])
    #for i in keywords:
        #print(i)
    return keywords
#print(findKeywords("text.txt"))
def converttexttoString(filename):
    with open(filename) as f:
        lines = f.readlines()
    textstr = ''
    for x in lines:
        textstr+= x
    #print(type(textstr))
    return textstr
#print(converttexttoString("text.txt"))
def createDictionary (text, keywords):
    my_dict = {}
    #print(len(text))
    for i in keywords:
        #print(i)
        #print(text.index(i))
        my_dict.update({i : text.index(i)})
    return my_dict

def sortByIndex(dict):
    sorted_dict = sorted(dict.items(), key=operator.itemgetter(1))
    return sorted_dict
def makestringfromDictionary(sorteddictionary):
    str = ''
    for key in sorteddictionary:
        str+=key[0] + ' '
    return str

def makeMainIdea(filename, outputfile):
    keywordwatsonlist = findKeywords(filename)
    textstring = converttexttoString(filename)
    dictionary = createDictionary(textstring,keywordwatsonlist)
    beautifulsorteddictionary = sortByIndex(dictionary)
    finalstring = makestringfromDictionary(beautifulsorteddictionary)
    text_file = open(outputfile, "w")
    text_file.write(finalstring)

def splitIntoParagraphs(text):
    return re.split('[\n]', text)

if __name__ == '__main__':
    makeMainIdea('text.txt', 'WSA.txt')
    print(splitIntoParagraphs(converttexttoString("text.txt")))




#keyworddata1 = keywordslist[0]
#print(keyworddata1['text'])
#newoutputfile = open("output.txt", "r")
#linelist = newoutputfile.read().splitlines()
#print("\"text\": ")
#for x in linelist:
#    print(x)
#    if x.startswith("\"text\": "):
#        keywords.append(x[8:])
#
#print(keywords)
