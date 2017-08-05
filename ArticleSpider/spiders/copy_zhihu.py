# -*- coding: utf-8 -*-
import scrapy
import re
import time
from zheye import zheye
import requests
import shutil

z = zheye()


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    header = {
        "Host": "www.zhihu.com",
        'Referer': 'https://www.zhihu.com/',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
    }

    def parse(self, response):
        pass

    def start_requests(self):
        return [scrapy.Request('https://www.zhihu.com/#signin', headers=self.header, callback=self.login)]

    def login(self, response):
        response_text = response.text
        match_obj = re.search('.*name="_xsrf" value="(.*?)"', response_text)
        xsrf = ''
        pos = self.get_postdata()
        if pos.count() == 1:
            captcha = '{"img_size": [200, 44], "input_points": [[%.2f,%2f]]}' % (
                pos[0][1] / 2, pos[0][0] / 2, pos[1][1] / 2, pos[1][0] / 2)
        else:
            captcha = '{"img_size": [200, 44], "input_points": [[%.2f,%2f],[%.2f,%2f]]}' % (
                pos[0][1] / 2, pos[0][0] / 2, pos[1][1] / 2, pos[1][0] / 2)

        if match_obj:
            xsrf = match_obj.group(1)
        if xsrf:
            post_url = 'https://www.zhihu.com/login/phone_num'

            post_data = {
                '_xsrf': xsrf,
                'password': 'admin0417',
                'captcha': captcha,
                'captcha_type': 'cn',
                'phone_num': '18651812507'
            }

            return [scrapy.FormRequest(
                url=post_url,
                formdata=post_data,
                headers=self.header,
                callback=self.check_login
            )]

    def check_login(self, response):
        for url in self.start_urls:
            yield self.make_requests_from_url(url)
        pass

    # 倒立汉字验证码
    def get_postdata(self):
        randomNum = str(int(time.time() * 1000))
        response = requests.session().get('https://www.zhihu.com/captcha.gif?r={}&type=login&lang=cn'.format(randomNum),
                                          headers=self.header,
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

        return pos
