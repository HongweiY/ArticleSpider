# -*- coding: utf-8 -*-

__mktime__ = '17-7-21'
__author__ = 'ymfsder'


import hashlib
import re


def get_md5(url):
    if isinstance(url,str):
        url = url.encode('utf-8')
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()

# 定义数字获取函数
def extract_num(text):
    match_com = re.match('.*?(\d+).*', text)
    if match_com:
        num = int(match_com.group(1))
    else:
        num = 0
    return num