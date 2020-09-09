import pickle
import re
import time
import RSAJS
import base64
import LinkRedis
from requests_html import HTMLSession


def hex2b64(string):
    m = bytes().fromhex(string)
    result = bytes(base64.b64encode(m)).decode('utf-8')
    return result


def b642hex(string):
    m = base64.b64decode(string.encode('utf-8'))
    result = ''.join([hex(i).replace('0x', '').zfill(2) for i in bytes(m)])
    return result


class Sdata:
    __session = 0
    # 加密后密码
    __ras_password = ""
    # 加密前密码
    __password = ""
    # 学号
    __yhm = ""
    # 验证码
    __csrftoken = ""
    # 时间戳获取
    __exponent = ""
    __modulus = ""
    __timed = ""
    # 请求头
    headers = {
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/85.0.4183.83 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                  '*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7',
    }

    def __init__(self, yhm, password):
        self.__yhm = yhm
        self.__password = password
        self.__session = HTMLSession()
        self.__session.headers = self.headers
        self.__csrftoken = self.get_csrftoken()
        self.__timed = self.creat_timed()
        self.__modulus, self.__exponent = self.get_me()
        self.__ras_password = self.get_rsa_password()

    # 获取会话
    def get_session(self):
        return self.__session

    # 生成时间戳 13 位
    @staticmethod
    def creat_timed():
        return str(round(time.time() * 1000))

    # 获取csrftoken
    def get_csrftoken(self, index_url="http://jw.dfxy.net/jwglxt/xtgl/login_slogin.html"):
        csr = self.__session.get(index_url)
        csrftoken = csr.html.find("#csrftoken", first=True).attrs['value']
        return csrftoken

    # 获取加密需要的两个值
    def get_me(self):
        url = "http://jw.dfxy.net/jwglxt/xtgl/login_getPublicKey.html?time={timed}&_={timed}" \
            .format(timed=self.__timed)
        me = str(self.__session.get(url).text)
        m = re.search(":\".*\",", me).group()[2:-2]
        e = re.search("exponent\":.*\"", me).group()[-5:-1]
        return m, e

    # 计算加密后的密码
    def get_rsa_password(self):
        key = RSAJS.RSAKey()
        key.setPublic(b642hex(self.__modulus), b642hex(self.__exponent))
        return hex2b64(key.encrypt(self.__password))

    # 校验登陆
    def login(self):
        url = "http://jw.dfxy.net/jwglxt/xtgl/login_slogin.html?time={timed}".format(timed=self.__timed)
        data = {
            'csrftoken': self.__csrftoken,
            'yhm': self.__yhm,
            'mm': self.__ras_password,
            'mm': self.__ras_password
        }
        # Session序列化并存到redis 10分钟过期
        return_page = self.__session.post(url, data=data)
        cookies = pickle.dumps(self.get_session())

        LinkRedis.Cache.set(self.__yhm, cookies)
        if str(return_page.url).find("initMenu") == -1:
            return False
        return True


# 检查是否登陆过且缓存未失效
def check_session(no, mm):
    se = LinkRedis.Cache.get(no)
    if se is None:
        return Sdata(no, mm).login()
    return pickle.loads(se)


# 获取姓名 学部 照片
def get_name_college(no, mm):
    test = check_session(no, mm)
    url = "http://jw.dfxy.net/jwglxt/xtgl/index_cxYhxxIndex.html?xt=jw&localeKey=zh_CN&_={timed}" \
          "&gnmkdm=index&su={yhm}".format(timed=Sdata.creat_timed(), yhm=no)
    page = test.get(url).html
    name = page.find(".media-heading", first=True)
    coll = page.find("p", first=True)
    # 保存照片到本地
    html = test.get(url='http://jw.dfxy.net' + (page.find(".media-object", first=True).attrs['src']))
    with open('./static/' + no + '.jpg', 'wb') as file:
        file.write(html.content)
    return {
        "name": name.text,
        "college": coll.text,
        "img": 'http://101.200.121.157/static/' + no + '.jpg'
    }


# 获取课程表
def get_class_schedule(no, mm):
    test = check_session(no, mm)
    data = {
        "xnm": "2020",
        "xqm": "3"
    }
    re_json = test.post("http://jw.dfxy.net/jwglxt/kbcx/xskbcx_cxXsKb.html?gnmkdm=N2151",
                                      data=data).text
    return re_json


# 获取成绩
def get_grades(no, mm, ):
    test = check_session(no, mm)
    test.post("http://jw.dfxy.net/jwglxt/cjcx/cjcx_cxDgXscj.html?gnmkdm=N305005&"
                            "layout=default&su={no}".format(no=no), data={"gndm": "N305005"})
    data = {
        "xnm": "2019",
        "xqm": "",
        "_search": "false",
        "nd": str(Sdata.creat_timed()),
        "queryModel.showCount": "15",
        "queryModel.currentPage": "1",
        "queryModel.sortName": "",
        "queryModel.sortOrder": "asc",
        "time": "1"
    }
    re_json = test.post("http://jw.dfxy.net/jwglxt/cjcx/cjcx_cxDgXscj.html?"
                                      "doType=query&gnmkdm=N305005", data=data).text
    return re_json


if __name__ == "__main__":
    yhm = input("请输入学号")
    mm = input("请输入密码")
    test = Sdata(yhm, mm)
    if test.login():
        print("欢迎您：{name} , {coll}".format(name=test.get_name_college(yhm, mm)[0],
                                           coll=test.get_name_college(yhm, mm)[1]))
    else:
        print("登录失败，请重试")
