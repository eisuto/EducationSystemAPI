from flask import Flask, request
import mainAPI
app = Flask(__name__)


@app.route('/')
def hello_world():
    return "Hello?!"


@app.route('/login', methods=['POST', 'GET'])
def login():
    return str(mainAPI.Sdata(request.form['no'],request.form['mm']).login())
