from flask import Flask, request
import pickle
import mainAPI
import LinkRedis

app = Flask(__name__)


@app.route('/')
def hello_world():
    return "Hello?!"


# 登录校验
@app.route('/login', methods=['POST', 'GET'])
def login():
    no = request.form['no']
    mm = request.form['mm']
    student = mainAPI.Sdata(no, mm)

    return str(student.login())


# 获取 姓名 班级 照片
@app.route('/info', methods=['POST', 'GET'])
def info():
    no = request.form['no']
    mm = request.form['mm']
    # return mainAPI.get_name_college(no, mm)
    return mainAPI.get_name_college(no, mm)


# 获取 课程表
@app.route('/class_schedule', methods=['POST', 'GET'])
def class_schedule():
    no = request.form['no']
    mm = request.form['mm']
    return mainAPI.get_class_schedule(no, mm)


# 获取 成绩
@app.route('/grades', methods=['POST', 'GET'])
def grades():
    no = request.form['no']
    mm = request.form['mm']
    # year = request.form['year']
    return mainAPI.get_grades(no, mm)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="80")



















