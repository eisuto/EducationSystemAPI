import re
import time
import RSAJS
import base64
from requests_html import HTMLSession


def hex2b64(string):
    m = bytes().fromhex(string)
    result = bytes(base64.b64encode(m)).decode('utf-8')
    return result


def b642hex(string):
    m = base64.b64decode(string.encode('utf-8'))
    result = ''.join([hex(i).replace('0x','').zfill(2) for i in bytes(m)])
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

    def __init__(self,  yhm, password):
        self.__yhm = yhm
        self.__password = password
        self.__session = HTMLSession()
        self.__session.headers = self.headers
        self.__csrftoken = self.get_csrftoken()
        self.__timed = self.creat_timed()
        self.__modulus, self.__exponent = self.get_me()
        self.__ras_password = self.get_rsa_password()

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
        return_page = self.__session.post(url, data=data)
        if str(return_page.url).find("initMenu") == -1:
            return False
        return True

    # 获取姓名 学部
    def get_name_college(self):
        url = "http://jw.dfxy.net/jwglxt/xtgl/index_cxYhxxIndex.html?xt=jw&localeKey=zh_CN&_={timed}" \
              "&gnmkdm=index&su={yhm}".format(timed=self.creat_timed(), yhm=self.__yhm)
        page = self.__session.get(url).html
        name = page.find(".media-heading", first=True)
        coll = page.find("p", first=True)
        return name.text, coll.text


'''
    if __name__ == "__main__":
    # yhm = input("请输入学号")
    # mm  = input("请输入密码")
    # test = Sdata(yhm, mm)
    if str(test.login().url).find("initMenu") == -1:
        print("登录失败，请重试")
    print("欢迎您：{name} , {coll}".format(name=test.get_name_college()[0], coll=test.get_name_college()[1]))
'''











