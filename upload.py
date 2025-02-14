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
import io
import operator
import re #add comme
from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1 import Features, KeywordsOptions
import matplotlib
from docx import Document
matplotlib.use('Agg')
import smtplib
import subprocess
from rq import Queue
from worker import conn
import utils
import time
from rq.job import Job
from redis import Redis
#import sox
#from ffmpy import FFmpeg
#import ffmpy
import ffmpeg
from pydub import AudioSegment
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.utils import COMMASPACE, formatdate
from email import encoders
app = Flask(__name__)
methodlist = ['uploadtogoogle.py', 'speechtotext.py', 'converttooutline.py', 'createwordcloud.py']
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
@app.route('/')
def hello():
    return render_template('demo.html')

@app.route('/uploaderlocal', methods=['POST'])
def upload_file():
    q = Queue(connection=conn)
    print('flacifying LOL')
    rawFile = request.files['gcloudfile']
    email = request.form['email']

    fString = str(rawFile.filename)

    fString = fString.split("'")
    filepath = fString[0]
    formatType = filepath[filepath.index('.')+1:]
    storage_client = storage.Client.from_service_account_json(
          'A2N-Official-bd3ee1c6cc61.json')
    bucket = storage_client.get_bucket('a2n_audio')
    blob = bucket.blob('rawInput')
     #print(fString[1])
    blob.upload_from_file(rawFile, content_type = 'audio/'+ formatType)
    storage_client = storage.Client.from_service_account_json(
          'A2N-Official-bd3ee1c6cc61.json')
    bucket = storage_client.get_bucket('a2n_audio')
    blob = bucket.blob('rawInput')
    blob.download_to_filename('rawInput.'+formatType)

    #f.save(f.filename)
    #print('saving')
    #formatType = filepath[filepath.index('.')+1:]
    output = AudioSegment.from_file('rawInput.'+formatType, formatType)
    output.export('flacified.flac', format="flac", parameters=["-ac", "1"])
    print('able to take from file ' + filepath)
    print('sox is a go!')





    print('uploading to google')
    storage_client = storage.Client.from_service_account_json(
          'A2N-Official-bd3ee1c6cc61.json')
    bucket = storage_client.get_bucket('a2n_audio')
    blob = bucket.blob('input')
     #print(fString[1])
    blob.upload_from_filename('flacified.flac')
    print('GOT HERE')




    # f.save(f.filename)
    # fString = str(f.filename)
    # fString = fString.split("'")
    # filepath = fString[0]
    # formatType = filepath[filepath.index('.')+1:]
    # output = AudioSegment.from_file(fString[0], formatType)
    # output.export('flacified.flac', format="flac", parameters=["-ac", "1"])
    # print('able to take from file ' + fString[0])
    # print('sox is a go!')
    # os.remove(fString[0])
    #for i in range(4):
        #subprocess.call("python3 "+ methodlist[i], shell=True)
    # utils.upload_to_google()
    # print('uploaded to google')
    # utils.speech_to_text()
    # print('speech to text successful')
    # utils.convert_to_outline()
    # print('made the outline')
    # utils.create_wordcloud()
    # print('finished! made the wordcloud')
   # # extra argument: result_ttl=5000
    ####job1 = q.enqueue_call(func=utils.upload_to_google, args=('flacified.flac', 'string'), timeout='1h', result_ttl=30)
    #q.enqueue(utils.upload_to_google)
   #  #print(job1.get_id())
   #  #get_results(job1.get_id())
   # #  #print(result.get_id())
   #  ###job2 = q.enqueue_call(func=utils.speech_to_text, args=(), timeout='1h')
    q.enqueue(utils.speech_to_text, timeout = '1h')
   #  #print(job2.get_id()   #  #print(result.get_id())
   #  ###job3 = q.enqueue_call(func=utils.convert_to_outline, args=(), timeout='1h')
    q.enqueue(utils.convert_to_outline, timeout = '1h')
   #  #print(job3.get_id())
   #  #get_results(job3.get_id())
   # #  #print(result.get_id())
   #  ###job4 = q.enqueue_call(func=utils.create_wordcloud, args=(), timeout='1h')
    q.enqueue(utils.create_wordcloud, timeout = '1h')
   #  #job5 = q.enqueue_call(func=utils.send_email, args=(email, 'outline.docx', 'static/outline.docx'), timeout='1h')
    q.enqueue(utils.send_email, email, ['static/outline.docx', 'static/cloud.png'], timeout = '1h')


    # print('Job 2 status before ' + job2.status)
    # while(job2.status=='queued'):
    #     time.sleep(1)
    # print('Job 2 status after ' + job2.status)
    # while(job3.status=='queued'):
    #     time.sleep(1)
    # while(job4.status=='queued'):
    #     time.sleep(1)
    #print(result.get_id())
    #print(job4.get_id())
    #get_results(job4.get_id())
    #while (result.is_finished != True):
        #time.sleep(1)
    #return render_template('fileDownload.html')
    # while(len(q1)>0):
    #     time.sleep(1)
    return render_template('fileDownload.html')
def get_results(job_key):

    job = Job.fetch(job_key, connection=conn)

    if(job.is_finished == False):
        job = Job.fetch(job_key, connection=conn)
    print(" finished")
    return

if __name__ == '__main__':
    app.run()
