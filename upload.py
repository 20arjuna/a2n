#from google.cloud.storage import storage
from flask import Flask,render_template, Response, request, redirect, url_for, send_file

#test

app = Flask(__name__)
#from google.cloud import resumable_media




@app.route("/", methods=['POST','GET'])
def hello():
    return render_template('wordcloud.html')

@app.route('/uploaderlocal', methods=['POST','GET'])
def upload_file():
   if request.method == 'POST':
       f = request.files['gcloudfile']


      # print(f.filename)
       #print(secure_filename(f.filename))
       f.save(f.filename)
       fString = str(f)
       fString = fString.split("'")
       storage_client = storage.Client.from_service_account_json(
            'A2N-Official-bd3ee1c6cc61.json')
       bucket = storage_client.get_bucket('a2n_audio')
       blob = bucket.blob('input')
       blob.upload_from_filename(fString[1])

       ##### Converting Speech to text ##########
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

       # Each result is for a consecutive portion of the audio. Iterate through
       # them to get the transcripts for the entire audio file.
       for result in response.results:
           # The first alternative is the most likely one for this portion.
           text_file.write(u'{}'.format(result.alternatives[0].transcript))

           text_file.write("\n")

           #text_file.write('Confidence: {}'.format(result.alternatives[0].confidence))


       text_file.close()

       print('starting wordcloud')

       d = path.dirname(__file__) if "__file__" in locals() else os.getcwd()

       # Read the whole text.
       text = open(path.join(d, 'wordcloud.txt')).read()

       # Generate a word cloud image
       wordcloud = WordCloud().generate(text)
       print('wordcloud generated')
       image = wordcloud.to_image()

       #image.show()
       image.save('/Users/20arjuna/Desktop/A2N/cloud.png', 'PNG')

       ##### Notes ########
       #wordcloud.txt is the inputfile for watson that has the output of speechtotext
       createNotes('wordcloud.txt', 'notes.txt')
       return send_file('cloud.png')
if __name__ == "__main__":
    app.run()
