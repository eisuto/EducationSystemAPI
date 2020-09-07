from flask import Flask, request
import mainAPI
app = Flask(__name__)


@app.route('/')
def hello_world():
    return "Hello?!"


@app.route('/login', methods=['POST', 'GET'])
def login():
    no = request.form['no']
    mm = request.form['mm']
    student = mainAPI.Sdata(no, mm)
    name, coll = student.get_name_college(no, mm)
    s1 = "欢迎您：{name} , {coll}".format(name=name, coll=coll)
    return s1
# @app.route('/getNameCollege', methods=['POST', 'GET'])
# def getNameCollege():


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="80")
