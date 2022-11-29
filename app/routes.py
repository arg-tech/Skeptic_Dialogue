from flask import redirect, request, render_template
from . import application
from app.skeptic_dialogue import SkepticDialogue
import json
import requests



def call_skeptic(filename):
    upload_url = 'http://skeptic-ws.arg.tech/'
    file_ = {'file': (filename, open(filename, 'rb'))}
    r = requests.post(upload_url, files=file_)
    data = json.loads(r.text)

    return data




@application.route('/skeptic_dialogue', methods=['GET', 'POST'])
def sk_dialogue():
    if request.method == 'POST':
        f = request.files['file']
        f.save(f.filename)
        #ff = open(f.filename, 'r')
        #data = json.load(ff)
        skeptic_out = call_skeptic(f.filename)
        sd = SkepticDialogue()
        dialogue = sd.generate_dialogue(skeptic_out)
        return dialogue
    
    elif request.method == 'GET':
        return render_template('index.html')
        
 
 
