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

d =  path.dirname(__file__) if "__file__" in locals() else os.getcwd()

    # Read the whole text.
text = open(path.join(d, 'wordcloud.txt')).read()

    # Generate a word cloud image
wordcloud = WordCloud().generate(text)
print('wordcloud generated')
image = wordcloud.to_image()

image.save('static/cloud.png', 'PNG')
