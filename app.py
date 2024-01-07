from nltk.tokenize import word_tokenize
from nltk import FreqDist
from nltk.classify import NaiveBayesClassifier, accuracy
from nltk.corpus import stopwords
import pickle
import random
from flask import Flask, request, session
import requests
from flask_cors import CORS
import nltk


nltk.download('punkt')
nltk.download('stopwords')




app = Flask(__name__)
CORS(app)

def help_command():
    command_list = """
Command List:
/inputTasks (task1,task2,task3) (person1,person2,person3)
  -> Format penggunaan: /inputTasks (daftar_tugas) (daftar_anggota)

/randomAssignment
  -> Jangan lupa jalankan command /inputTasks untuk memasukkan daftar tugasnya
  -> Mengacak dan membagikan tugas yang telah dimasukkan

/help
  -> Menampilkan command lists
    """
    return command_list

def random_diskusi():
    sentence = ["Wah ada yang lagi diskusi nih", "Ayo siapa yang punya ide bagus?", "Sepertinya itu ide yang bagus", "Hmm oke banget!"]
    return random.choice(sentence)

def random_kick():
    sentence = ["Kesian yang mau dikeluarin...", "Makanya kalau udah ada tugas langsung dikerjain", "Itu akibatnya kalau kamu tidak mengerjakan tugas", "Dasar beban kelompok!"]
    return random.choice(sentence)

def random_marah():
    sentence = ["Jangan marah-marah gais nanti cepat tua", "Calm down mapren", "Santai dong bos~", "Waduh, ada yang marah nih..."]
    return random.choice(sentence)

def random_ngajak():
    sentence = ["Ayo dikerjain tugasnya", "Dikerjain ya gais jangan ditunda terus", "Semangat kerjain nya <3", "Hayo sudah mau deadline"]
    return random.choice(sentence)

def random_kotor():
    sentence = ["Eitss kasar sekali mulut kau!", "Hush tidak boleh ngomong kasar ya", "Hadeh mulut kamu ya", "Jangan ngomong kasar dong!"]
    return random.choice(sentence)

def random_read():
    sentence = ["Ada yang jualan kacang nih", "Kalau udah read, dibalas dong gais", "Kacang~", "Read aja teros!"]
    return random.choice(sentence)


def remove_punctuation(text):
    import string
    translator = str.maketrans("", "", string.punctuation)
    return text.translate(translator)

def remove_stopwords(words):
    stop_words = set(stopwords.words("indonesian"))
    return [word for word in words if word.lower() not in stop_words]

@app.route('/', methods=['GET'])
def hello():
    return 'hello'

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


    import random
    random.shuffle(featuresets)

    train_count = int(len(featuresets)*0.9)
    train_data = featuresets[:train_count]
    test_data = featuresets[train_count:]

    classifier = NaiveBayesClassifier.train(train_data)

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
    
task_list = []
anggota_list = []


@app.route('/webhook', methods=['POST'])
def webhook():
    task_list = []
    anggota_list = []

    try:
        data = request.json
        events = data['events']

        for event in events:
            if 'message' in event and 'text' in event['message']:
                user_message = event['message']['text']
                if user_message == '/help':
                    response_text = help_command()
                    reply_token = event['replyToken']
                    send_line_message(reply_token, response_text)

                elif user_message.startswith('/inputTasks'):
                    if '(' not in user_message or ')' not in user_message:
                        response_text = 'Format penggunaan: /inputTasks (daftar_tugas) (daftar_anggota)'
                    else:
                        content = user_message[user_message.find('(')+1:user_message.rfind(')')]
                        tasks_and_members = content.split(' ')

                        if len(tasks_and_members) < 2:
                            response_text = 'Format penggunaan: /inputTasks (daftar_tugas) (daftar_anggota)'
                        else:
                            session['task_list'] = tasks_and_members[0].split(',')
                            session['anggota_list'] = tasks_and_members[1].split(',')
                            response_text = 'Daftar tugas dan anggota telah diterima.'
                    reply_token = event['replyToken']
                    send_line_message(reply_token, response_text)

                elif user_message == '/randomAssignment':
                    task_list = session.get('task_list', [])
                    anggota_list = session.get('anggota_list', [])
                    if len(task_list) == 0:
                        response_text = 'Anda perlu memasukkan daftar tugas terlebih dahulu.'
                    elif len(task_list) != len(anggota_list):
                         response_text = 'Jumlah daftar tugas harus sama dengan jumlah daftar anggota.'
                    else:
                        random.shuffle(task_list)
                        random.shuffle(anggota_list)
                        assignment_message = 'Pembagian tugas:\n'
                        for i, (task, anggota) in enumerate(zip(task_list,anggota_list), start=1):
                            assignment_message += f'{i}.{anggota.strip("()")} : {task.strip("()")}\n'
                        response_text = assignment_message
                    reply_token = event['replyToken']
                    send_line_message(reply_token, response_text)
                
                else:
                    preprocessed_chat = remove_stopwords(word_tokenize(remove_punctuation(user_message)))
                    prediction = classifier.classify(FreqDist(preprocessed_chat))

                    if prediction == 'marah':
                        response_text = random_marah()
                    elif prediction == 'diskusi':
                        response_text = random_diskusi()
                    elif prediction == 'kick':
                        response_text = random_kick()
                    elif prediction == 'ngajak':
                        response_text = random_ngajak()
                    elif prediction == 'ngomong_kotor':
                        response_text = random_kotor()
                    elif prediction == 'read_doang':
                        response_text = random_read()
                    random_number = random.randint(1, 2)
                    if random_number == 1:
                        reply_token = event['replyToken']
                        send_line_message(reply_token, response_text)
    except:
        print("an error occurred")
    finally:
        return 'yey'
    
def send_line_message(reply_token, text):
    line_url = 'https://api.line.me/v2/bot/message/reply'
    channel_access_token = "TQcMI7gfUAD/eEszmvuTOcpQCnJSJ3LogpM3YAIwSnLRFzIcwyBMQehRsAncc3EFbIoMLmsvABWqXsGiO0+XPsDaru0qpWKCnwmR/CPenafQu7cBDIvTipT4f46jEEaYMMi+ZjZJ0DA1pLrqfcl6lQdB04t89/1O/w1cDnyilFU="
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + channel_access_token,
    }
    data = {
        'replyToken': reply_token,
        'messages': [{'type': 'text', 'text': text}],
    }
    requests.post(line_url, json=data, headers=headers)

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