import json
from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1 import Features, KeywordsOptions

file = open("input.txt", "r")
outputfile = open("output.json", "w")

natural_language_understanding = NaturalLanguageUnderstandingV1(
    version='2018-11-16',
    iam_apikey='m620e2y3lML5qG_oRJy9JERrlR0-159j3vJVrtPJkhJg',
    url='https://gateway-wdc.watsonplatform.net/natural-language-understanding/api'
)

response = natural_language_understanding.analyze(
    text = file.read(),
    features=Features(keywords=KeywordsOptions(sentiment=False,emotion=False))).get_result()

print(json.dumps(response, indent=2))
file.close()
outputfile.write(json.dumps(response, indent=2))
outputfile.close()
