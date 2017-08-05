# -*- coding: utf-8 -*-

__mktime__ = '17-8-3'
__author__ = 'ymfsder'

import requests
import re
import time

from PIL import Image

try:
    import cookielib
except:
    import http.cookiejar as cookielib

session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename="cookies.txt")
try:
    session.cookies.load(ignore_discard=True)
except:
    print("cookie未能加载")

agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
header = {
    "Host": "www.zhihu.com",
    'Referer': 'https://www.zhihu.com/',
    'User-Agent': agent
}


def is_login():
    # 通过个人中心页面返回状态码来判断是否为登录状态
    inbox_url = "https://www.zhihu.com/inbox"
    response = session.get(inbox_url, headers=header, allow_redirects=False)
    if response.status_code != 200:
        return False
    else:
        return True


def get_xsrf():
    # 获取xsrf code
    response = session.get("https://www.zhihu.com", headers=header)
    match_obj = re.search('.*name="_xsrf" value="(.*?)"', response.text)
    if match_obj:
        return (match_obj.group(1))
    else:
        return ""


def get_index():
    response = session.get("https://www.zhihu.com", headers=header)
    with open("index_page.html", "wb") as f:
        f.write(response.text.encode("utf-8"))
    print("ok")


def get_captcha():
    t = str(int(time.time() * 1000))
    captcha_url = 'https://www.zhihu.com/captcha.gif?r={0}&type=login'.format(t)
    requestCon = session.get(captcha_url, headers=header)
    with open('captcha.jpg', 'wb') as f:
        f.write(requestCon.content)
        f.close()

    try:
        im = Image.open('captcha.jpg')
        im.show()
        im.close()
    except:
        pass
    captcha = input('请输入验证码\n>')
    return captcha


def zhihu_login(account, password):
    # 知乎登录
    if re.match("^1\d{10}", account):
        print("手机号码登录")
        post_url = "https://www.zhihu.com/login/phone_num"
        post_data = {
            "_xsrf": get_xsrf(),
            "phone_num": account,
            "password": password,
            'captcha':get_captcha()
        }
    else:
        if "@" in account:
            # 判断用户名是否为邮箱
            print("邮箱方式登录")
            post_url = "https://www.zhihu.com/login/email"
            post_data = {
                '_xsrf': get_xsrf(),
                'password': password,
                'captcha_type': 'cn',
                'phone_num': account

            }

    response_text = session.post(post_url, data=post_data, headers=header)
    session.cookies.save()


zhihu_login("18651812507", "admin0417")
# get_index()
is_login()
# get_captcha()
