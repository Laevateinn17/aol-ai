from flask import Flask, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

bluejack_url = 'https://bluejack.binus.ac.id/lapi/api/Assistant/All'
messier_url = 'https://socs1.binus.ac.id/messier/GeneralWeb.svc/GetThumbnail/'

@app.route('/', methods=['GET'])
def hello():
    return 'Hello world'

@app.route('/assistants', methods=['GET'])
def assistant():
    response = requests.get(bluejack_url)
    if response.status_code == 200:
        data = response.json()
        list = data.get('active', []) + data.get('inactive', [])
        
        for value in list:
            picture_id = value.get('PictureId', '')
            picture_link = f'{messier_url}{picture_id}/300'
            value['PictureLink'] = picture_link
        
        return jsonify(list)
    return ''

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)