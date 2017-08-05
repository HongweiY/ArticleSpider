# -*- coding: utf-8 -*-
import json
import re
import time

from zheye import zheye

z = zheye()
import scrapy


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
        if match_obj:
            xsrf = match_obj.group(1)
        if xsrf:
            post_data = {
                '_xsrf': xsrf,
                'password': 'admin0417',
                'captcha': '',
                'captcha_type': 'cn',
                'phone_num': '18651812507'
            }

            headers = {
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
            }
            randomNum = str(int(time.time() * 1000))
            captcha_url = 'https://www.zhihu.com/captcha.gif?r={}&type=login&lang=cn'.format(randomNum)
            yield scrapy.Request(captcha_url, headers=headers, meta={'post_data': post_data},
                                 callback=self.login_after_captcha)

    def login_after_captcha(self, response):

        with open('pic_captcha.gif', 'wb') as f:
            f.write(response.body)
            f.close()
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
        if len(pos) == 1:
            captcha = '{"img_size": [200, 44], "input_points": [[%.2f,%2f]]}' % (
                pos[0][1] / 2, pos[0][0] / 2)
        else:
            captcha = '{"img_size": [200, 44], "input_points": [[%.2f,%2f],[%.2f,%2f]]}' % (
                pos[0][1] / 2, pos[0][0] / 2, pos[1][1] / 2, pos[1][0] / 2)

        post_url = 'https://www.zhihu.com/login/phone_num'
        post_data = response.meta.get('post_data', {})
        post_data['captcha'] = captcha
        return [scrapy.FormRequest(
            url=post_url,
            formdata=post_data,
            headers=self.header,
            callback=self.check_login
        )]

    def check_login(self, response):
        text_json = json.loads(response.text)
        if 'msg' in text_json and text_json['msg'] == '登录成功':
            for url in self.start_urls:
                yield scrapy.Request(url, dont_filter=True, headers=self.header)
