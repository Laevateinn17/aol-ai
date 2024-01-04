from nltk.tokenize import word_tokenize
from nltk import FreqDist
from nltk.classify import NaiveBayesClassifier, accuracy
from nltk.corpus import stopwords
import pickle
from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

bluejack_url = 'https://bluejack.binus.ac.id/lapi/api/Assistant/All'
messier_url = 'https://socs1.binus.ac.id/messier/GeneralWeb.svc/GetThumbnail/'

def remove_punctuation(text):
    import string
    translator = str.maketrans("", "", string.punctuation)
    return text.translate(translator)

def remove_stopwords(words):
    stop_words = set(stopwords.words("indonesian"))
    return [word for word in words if word.lower() not in stop_words]

@app.route('/', methods=['GET'])
def hello():
    return 'Hello there'

# @app.route('/assistants', methods=['GET'])
# def assistant():
#     response = requests.get(bluejack_url)
#     if response.status_code == 200:
#         data = response.json()
#         list = data.get('active', []) + data.get('inactive', [])
        
#         for value in list:
#             picture_id = value.get('PictureId', '')
#             picture_link = f'{messier_url}{picture_id}/300'
#             value['PictureLink'] = picture_link
        
#         return jsonify(list)
#     return ''

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)