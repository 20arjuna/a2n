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
