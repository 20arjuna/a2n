#from google.cloud.storage import storage
from flask import Flask,render_template, Response, request, redirect, url_for, send_file
from werkzeug import secure_filename
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
import google.cloud.storage as storage
import os
from os import path
from wordcloud import WordCloud
import json
import re
import operator
import re
from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1 import Features, KeywordsOptions
import matplotlib
from docx import Document
matplotlib.use('Agg')
import subprocess
from rq import Queue
from worker import conn
import utils
import time
import sox
from ffmpy import FFmpeg
app = Flask(__name__)

#from google.cloud import resumable_media

def findKeywords(filename):
    file = open(filename, "r")
    outputfile = open("jsonOutput.json", "w")
    keywords = []

    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2018-11-16',
        iam_apikey='m620e2y3lML5qG_oRJy9JERrlR0-159j3vJVrtPJkhJg',
        url='https://gateway-wdc.watsonplatform.net/natural-language-understanding/api'
        )

    try:
        response = natural_language_understanding.analyze(
        text = string,
        features=Features(keywords=KeywordsOptions(sentiment=False,emotion=False))).get_result()
    except:
        return []
    #print(json.dumps(response, indent=2))
    file.close()
    outputfile.write(json.dumps(response, indent=2))
    outputfile.close()
    with open("jsonOutput.json", "r") as read_file:
        data = json.load(read_file)
    keywordslist = data['keywords']
    my_dict = {}
    for i in range((len(keywordslist))):
        x = keywordslist[i]
        keywords.append(x['text'])
        my_dict.update({x['text']:x['relevance']})
    #for i in keywords:
        #print(i)
    return createRelavantKeywordsList(my_dict, keywords)

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

def createRelavantKeywordsList(dict, keywordslist):
    keywords =[]
    threshold = 0.60
    for i in range(len(keywordslist)):
        #print(keywordslist[i])
        #print(dict.get(keywordslist[i]))
        if(dict.get(keywordslist[i]) > threshold):
            keywords.append(keywordslist[i])
    #print(keywordslist)
    #print(keywords)
    if(len(keywords)==0) and (len(keywordslist)>0):
        keywords.append(keywordslist[0])
    return keywords

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
    try:
        response = natural_language_understanding.analyze(
        text = string,
        features=Features(keywords=KeywordsOptions(sentiment=False,emotion=False))).get_result()
    except:
        return []


    #print(json.dumps(response, indent=2))
    outputfile.write(json.dumps(response, indent=2))
    outputfile.close()
    with open("jsonOutput.json", "r") as read_file:
        data = json.load(read_file)
    keywordslist = data['keywords']
    my_dict = {}
    for i in range((len(keywordslist))):
        x = keywordslist[i]
        keywords.append(x['text'])
        my_dict.update({x['text']:x['relevance']})
    #for i in keywords:
        #print(i)
    return createRelavantKeywordsList(my_dict, keywords)

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
        #print()
        #print("sentencesbefore")
        #print()
        #print(sentencesList)
        wsaList = []
        sentencesList = preprocess(sentencesList)
        #print()
        #print("sentencesafter")
        #print()
        #print(sentencesList)
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
    for i in range (len(list)-1, -1, -1):
        iList = list[i].split(' ')
        if '' in iList:
            iList.remove('')
        if(len(iList) <3):
            list.remove(list[i])
    return list

def outputOutline(wsaParagraphList, wsaSentenceMatrix, outputfile):
    ascii_outer = 65
    text_file = open(outputfile, "w")
    text_file.write("Here is your autogenerated outline!")
    text_file.write('')
    text_file.write('')
    for i in range(len(wsaParagraphList)):
        paragraph = wsaParagraphList[i]
        plist = paragraph.split(' ')
        if(len(plist) > 10):
            paragraphstring = ''
            for i in range(0,10):
                paragraphstring+=(' ' + plist[i])
            text_file.write("\n" + chr(ascii_outer) + ". " + paragraphstring)
        else:
            text_file.write("\n" + chr(ascii_outer) + ". " + paragraph)
        sentList = wsaSentenceMatrix[i]
        ascii_inner = 97
        for sentence in sentList:
            if(sentence != ''):
                wordlist = sentence.split(' ')
                if(len(wordlist) > 10):
                    sentencestring = ''
                    for i in range(0,10):
                        sentencestring+=(' ' + wordlist[i])
                    text_file.write("\n \t " + chr(ascii_inner)+ ". " + sentencestring)
                else:
                    text_file.write("\n \t " + chr(ascii_inner)+ ". " + sentence)
            else:
                ascii_inner-=1
            ascii_inner+=1
        ascii_outer+=1

def finaloutputoutline(inputfile, outputfile):
    paragraphlist = splitIntoParagraphs(converttexttoString(inputfile))
    newparagraphlist = preprocess(paragraphlist)
    wsaSentenceMatrix = createSummaryMatrix(newparagraphlist)
    #print(wsaSentenceMatrix)
    newparagraphlist = runWSAOnParagraphs(newparagraphlist)
    outputOutline(newparagraphlist,wsaSentenceMatrix, outputfile)

@app.route("/")

def hello():
    return render_template('wordcloud.html')

@app.route('/uploaderlocal', methods=['POST'])

def upload_file():
    #oauth2.init_app(app)
    # Explicitly use service account credentials by specifying the private key
    # file.

   q1 = Queue(connection=conn, default_connection=3600)
   f = request.files['gcloudfile']

   print('uploading to google cloud servers')


  # f.save(f.filename)
   fString = str(f.filename)
   fString = fString.split("'")
   stat = os.stat('flacified.flac')
   print(stat.st_mtime)
   #output = subprocess.call(['sox', fString[0], '-r', '44100', 'flacified.flac', 'remix', '1,2'], shell=True)
   ff = FFmpeg(
        inputs = {fString[0]: None},
        outputs = {'flacified.flac': ['-ac 1']}
   )
   ff.run()
   #subprocess.Popen('ffmpeg -i '+fString[0] + ' -ac 1 flacified.flac')
   print(stat.st_mtime)
   print('able to take from file' + fString[0])
   print('sox is a go!')

   # extra argument: result_ttl=5000
   result = q1.enqueue_call(func=utils.upload_to_google, args=(), timeout='1h')
   print(' arjun is suhtupid and uploadtogoogle works')
   result = q1.enqueue_call(func=utils.speech_to_text, args=(), timeout='1h')
   print(' arjun is sutupider and speechtotext works')
   result =q1.enqueue_call(func=utils.convert_to_outline, args=(), timeout='1h')
   print(' arjun is insanely sutupid and convertooutline works')
   result=q1.enqueue_call(func=utils.create_wordcloud, args=(), timeout='1h')
   print(' arjun is the suhtupidest person in the world and createwordcloud works')

   while (result.is_finished != True):
       time.sleep(1)
   return render_template('fileDownload.html')
   return render_template('fileDownload.html')

if __name__ == "__main__":
    app.run()
