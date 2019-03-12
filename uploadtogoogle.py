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

storage_client = storage.Client.from_service_account_json(
      'A2N-Official-bd3ee1c6cc61.json')
bucket = storage_client.get_bucket('a2n_audio')
blob = bucket.blob('input')
 #print(fString[1])
blob.upload_from_filename('flacified.flac')
print('GOT HERE')
