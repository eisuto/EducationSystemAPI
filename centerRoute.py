import time

from flask import Flask, request
#from flask_redis import FlaskRedis
import mainAPI

app = Flask(__name__)
#app.config['REDIS_URL'] = 'redis://:@localhost:6379/0'
#redis_client = FlaskRedis(app)


@app.route('/')
def hello_world():
    return "Hello?!"


# 登录校验
@app.route('/login', methods=['POST', 'GET'])
def login():
    no = request.form['no']
    mm = request.form['mm']

    student = mainAPI.Sdata(no, mm)
    # 存到缓存 10分钟过期
    # expires = int(time.time()) + 600
    # p = redis_client.pipeline()
    # p.set('no', no)
    # p.expireat('no', expires)
    # p.execute()

    return str(student.login())


# 获取 姓名 班级 照片
@app.route('/info', methods=['POST', 'GET'])
def info():
    no = request.form['no']
    mm = request.form['mm']

    return mainAPI.get_name_college(no, mm)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="80")
