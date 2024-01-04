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

def train():
    diskusi = open("Diskusi.txt","r").read()
    kick = open("Kick.txt","r").read()
    marah = open("Marah.txt","r").read()
    ngajak = open("NgajakTugas.txt","r").read()
    ngomong_kotor = open("NgomongKotor.txt","r").read()
    read_doang = open("ReadDoang.txt","r").read()

    diskusi_words = remove_stopwords(word_tokenize(remove_punctuation(diskusi)))
    kick_words = remove_stopwords(word_tokenize(remove_punctuation(kick)))
    marah_words = remove_stopwords(word_tokenize(remove_punctuation(marah)))
    ngajak_words = remove_stopwords(word_tokenize(remove_punctuation(ngajak)))
    kotor_words = remove_stopwords(word_tokenize(remove_punctuation(ngomong_kotor)))
    read_words = remove_stopwords(word_tokenize(remove_punctuation(read_doang)))

    all_words = []
    for word in diskusi_words:
        all_words.append(word)
    for word in kick_words:
        all_words.append(word)
    for word in marah_words:
        all_words.append(word)
    for word in ngajak_words:
        all_words.append(word)
    for word in kotor_words:
        all_words.append(word)
    for word in read_words:
        all_words.append(word)

    all_words = FreqDist(all_words)
    word_features = list(all_words.keys())[:5000]

    documents = []
    for sentence in diskusi.split('\n'):
        documents.append((sentence, "diskusi"))
    for sentence in kick.split('\n'):
        documents.append((sentence, "kick"))
    for sentence in marah.split('\n'):
        documents.append((sentence, "marah"))
    for sentence in ngajak.split('\n'):
        documents.append((sentence, "ngajak"))
    for sentence in ngomong_kotor.split('\n'):
        documents.append((sentence, "ngomong_kotor"))
    for sentence in read_doang.split('\n'):
        documents.append((sentence, "read_doang"))

    featuresets = []
    for sentence, label in documents:
        features = {}
        words = word_tokenize(sentence)
        for w in word_features:
            features[w] = (w in words)
        featuresets.append((features, label))

    # print(featuresets)
    import random
    random.shuffle(featuresets)

    train_count = int(len(featuresets)*0.9)
    train_data = featuresets[:train_count]
    test_data = featuresets[train_count:]

    classifier = NaiveBayesClassifier.train(train_data)
    # print(classifier.show_most_informative_features(n=700))
    # print(accuracy(classifier, test_data))

    file = open("mymodel.pickle","wb")
    pickle.dump(classifier, file)
    file.close()

    return classifier

try:
    file = open("mymodel.pickle","rb")
    classifier = pickle.load(file)
    file.close()
except:
    print("No data!")
    classifier = train()


@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    events = data['events']

    for event in events:
        if 'message' in event and 'text' in event['message']:
            user_message = event['message']['text']
            print(user_message)
            preprocessed_chat = remove_stopwords(word_tokenize(remove_punctuation(user_message)))
            prediction = classifier.classify(FreqDist(preprocessed_chat))
            if prediction == 'marah':
                response_text = "Jangan marah-marah ya gais!"
            elif prediction == 'diskusi':
                response_text = "Wah ada yang lagi diskusi nih"
            elif prediction == 'kick':
                response_text = "Calm dong gais"
            elif prediction == 'ngajak':
                response_text = "Ayo yang jangan lupa kerjain tugasnya"
            elif prediction == 'ngomong_kotor':
                response_text = "Gais, jangan ngomong kotor dong"
            elif prediction == 'read_doang':
                response_text = "Ini yang sudah read jawab dong!"


            reply_token = event['replyToken']
            send_line_message(reply_token, response_text)


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