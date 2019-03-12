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
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def upload_to_google(filename):
    print('uploading to google')
    storage_client = storage.Client.from_service_account_json(
          'A2N-Official-bd3ee1c6cc61.json')
    bucket = storage_client.get_bucket('a2n_audio')
    blob = bucket.blob('input')
     #print(fString[1])
    blob.upload_from_filename(filename)
    print('GOT HERE')


def speech_to_text():
    client = speech.SpeechClient()
    text_file = open("wordcloud.txt", "w")

    audio = types.RecognitionAudio(uri='gs://a2n_audio/input')
    config = types.RecognitionConfig(
    encoding=enums.RecognitionConfig.AudioEncoding.FLAC,
    sample_rate_hertz=44100,
    language_code='en-US',
    enable_automatic_punctuation=True)

    operation = client.long_running_recognize(config, audio)

    print('Waiting for operation to complete...')
    response = operation.result(timeout=9000)
    print('after operation')
    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    for result in response.results:
        print("in for loop")
        # The first alternative is the most likely one for this portion.
        text_file.write(u'{}'.format(result.alternatives[0].transcript))

        text_file.write("\n")
    text_file.close()

def convert_to_outline():
    finaloutputoutline('wordcloud.txt', 'notes.txt')
    path_notes = 'notes.txt'
    document = Document()
    myfile = open(path_notes).read()
    myfile = re.sub(r'[^\x00-\x7F]+|\x0c',' ', myfile) # remove all non-XML-compatible characters
    p = document.add_paragraph(myfile)
    document.save('static/outline'+ '.docx')

def create_wordcloud():
     d =  path.dirname(__file__) if "__file__" in locals() else os.getcwd()

         # Read the whole text.
     text = open(path.join(d, 'wordcloud.txt')).read()

         # Generate a word cloud image
     wordcloud = WordCloud().generate(text)
     print('wordcloud generated')
     image = wordcloud.to_image()

     image.save('static/cloud.png', 'PNG')

def send_email(to_address, file_name, file_path):
    fromaddr = 'a2npelican@gmail.com'
    toaddr = to_address

    # instance of MIMEMultipart
    msg = MIMEMultipart()

    # storing the senders email address
    msg['From'] = fromaddr

    # storing the receivers email address
    msg['To'] = toaddr

    # storing the subject
    msg['Subject'] = "Your Outline and Wordcloud, courtesy of A2N"

    # string to store the body of the mail
    body = "Enjoy."

    # attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))

    # open the file to be sent
    filename = file_name
    attachment = open(file_path, "rb")

    # instance of MIMEBase and named as p
    p = MIMEBase('application', 'octet-stream')

    # To change the payload into encoded form
    p.set_payload((attachment).read())

    # encode into base64
    encoders.encode_base64(p)

    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)

    # attach the instance 'p' to instance 'msg'
    msg.attach(p)

    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)

    # start TLS for security
    s.starttls()

    # Authentication
    s.login(fromaddr, "arjunsahil123")

    # Converts the Multipart msg into a string
    text = msg.as_string()

    # sending the mail
    s.sendmail(fromaddr, toaddr, text)

    # terminating the session
    s.quit()

##### Watson Helper Methods #######



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
