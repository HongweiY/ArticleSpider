# -*- coding: utf-8 -*-

__mktime__ = '17-8-4'
__author__ = 'ymfsder'

import requests
import shutil
import time
import re
import json

from zheye import zheye

z = zheye()

header = {
    'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
}

session = requests.session()
xsrf = ''

web_data = session.get('https://www.zhihu.com', headers=header).text

match_obj = re.search('.*name="_xsrf" value="(.*?)"', web_data)
if match_obj:
    xsrf = match_obj.group(1)

randomNum = str(int(time.time() * 1000))
response = session.get('https://www.zhihu.com/captcha.gif?r={}&type=login&lang=cn'.format(randomNum), headers=header,
                       stream=True)
if response.status_code == 200:
    with open('pic_captcha.gif', 'wb') as f:
        response.raw.decode_content = True
        shutil.copyfileobj(response.raw, f)

    position = z.Recognize('pic_captcha.gif')

captcha = {}
pos = position
tmp = []
captcha['input_points'] = []
for poss in pos:
    tmp.append(float(format(poss[0] / 2, '0.2f')))
    tmp.append(float(format(poss[1] / 2, '0.2f')))
    captcha['input_points'].append(tmp)
    tmp = []

params = {
    '_xsrf': xsrf,
    'password': 'admin0417',
    'captcha': '{"img_size": [200, 44], "input_points": [[%.2f,%2f],[%.2f,%2f]]}' % (
     pos[0][1] / 2, pos[0][0] / 2, pos[1][1] / 2, pos[1][0] / 2),
    'captcha_type': 'cn',
    'phone_num': '18651812507'
}


res = session.post('https://www.zhihu.com/login/phone_num',headers=header,params=params)
re_text = json.loads(res.text)

