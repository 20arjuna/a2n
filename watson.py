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
def printMainIdea(filename):
    keywordwatsonlist = findKeywords(filename)
    textstring = converttexttoString(filename)
    dictionary = createDictionary(textstring,keywordwatsonlist)
    beautifulsorteddictionary = sortByIndex(dictionary)
    finalstring = makestringfromDictionary(beautifulsorteddictionary)
    print(finalstring)
def findKeywordsofString(string):
    outputfile = open("jsonOutput.json", "w")
    keywords = []

    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2018-11-16',
        iam_apikey='m620e2y3lML5qG_oRJy9JERrlR0-159j3vJVrtPJkhJg',
        url='https://gateway-wdc.watsonplatform.net/natural-language-understanding/api'
        )

    response = natural_language_understanding.analyze(
        text = string,
        features=Features(keywords=KeywordsOptions(sentiment=False,emotion=False))).get_result()

    #print(json.dumps(response, indent=2))
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
def wsa(inputstring):
    keywordwatsonlist = findKeywordsofString(inputstring)
    dictionary = createDictionary(inputstring,keywordwatsonlist)
    beautifulsorteddictionary = sortByIndex(dictionary)
    finalstring = makestringfromDictionary(beautifulsorteddictionary)
    return finalstring

def splitIntoParagraphs(text):
    return re.split('[\n]', text)
def splitParagraphIntoSentences(paragraph):
    sentencelist = re.split('[?!.]', paragraph)
    return sentencelist[:-1]
def createSummaryMatrix(paragraphList):
    #paragraphList = splitIntoParagraphs(text)
    mat = []
    for paragraph in paragraphList:
        sentencesList = splitParagraphIntoSentences(paragraph)
        wsaList = []
        sentencesList = preprocess(sentencesList)
        for sentence in sentencesList:
            wsaList.append(wsa(sentence))
        #print(wsaList)
        mat.append(wsaList)
    return mat
def runWSAOnParagraphs(paragraphList):
    wsaList = []
    for paragraph in paragraphList:
        wsaList.append(wsa(paragraph))
    return wsaList

def preprocess(list):
    for element in list:
        elementlist = element.split(' ')
        if(len(elementlist) < 3):
            list.remove(element)
    return list

def outputOutline(wsaParagraphList, wsaSentenceMatrix, outputfile):
    text_file = open(outputfile, "w")
    for paragraph in wsaParagraphList:
        text_file.write("-   "+paragraph)
        for sentList in wsaSentenceMatrix:
            for sentence in sentList:
                text_file.write("\t -" + sentence)

if __name__ == '__main__':
    #print(createSummaryMatrix(converttexttoString("text.txt")))
    paragraphlist = splitIntoParagraphs(converttexttoString('text.txt'))
    newparagraphlist = preprocess(paragraphlist)
    print('newparagraphlist')
    print(newparagraphlist)
    wsaSentenceMatrix = createSummaryMatrix(newparagraphlist)
    outputOutline(newparagraphlist,wsaSentenceMatrix, 'WSA.txt')

    #makeMainIdea('text.txt', 'WSA.txt')
    #paragraphlist = splitIntoParagraphs(converttexttoString("text.txt"))
    #print(paragraphlist[1])
    #print(splitParagraphIntoSentences(paragraphlist[1]))





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
