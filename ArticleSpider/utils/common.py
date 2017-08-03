# -*- coding: utf-8 -*-

__mktime__ = '17-7-21'
__author__ = 'ymfsder'


import hashlib


def get_md5(url):
    if isinstance(url,str):
        url = url.encode('utf-8')
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()
