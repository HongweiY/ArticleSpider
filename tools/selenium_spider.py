# -*- coding: utf-8 -*-

__mktime__ = '17-9-1'
__author__ = 'ymfsder'

from selenium import webdriver
from scrapy.selector import Selector
import time

# brower = webdriver.Firefox(executable_path='/home/yumengfsd/PycharmProjects/ArticleSpider/geckodriver')


# #模拟知乎登陆
# brower.get('https://www.zhihu.com/#signin')
#
# brower.find_element_by_css_selector(".qrcode-signin-step1 span.signin-switch-password").click()
# brower.find_element_by_css_selector(".view-signin input[name='account']").send_keys('18651812507')
# brower.find_element_by_css_selector(".view-signin input[name='password']").send_keys('admin0417')
# brower.find_element_by_css_selector(".view-signin button.sign-button").click()

# # 微薄登陆和下拉刷新\
# brower.get('http://weibo.com/')
# time.sleep(5)
# brower.find_element_by_css_selector('#loginname').send_keys('18651812507')
# brower.find_element_by_css_selector(".info_list.password input[node-type='password']").send_keys('yw104717')
# brower.find_element_by_css_selector(".info_list.password a[node-type='submitBtn']").click()
# 鼠标下拉
# brower.get('https://www.oschina.net/blog')
# time.sleep(2)
# for i in range(3):
#
#     brower.execute_script(
#         'window.scrollTo(0,document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage)')
#     time.sleep(1)

# selector = Selector(text=brower.page_source)
# name = selector.css('.sku-name::text').extract()
# print(name)
# brower.quit()

# 设置不加载图片

chrome_opt = webdriver.ChromeOptions()
prefs ={'profile.managed_default_content_settings.images':2}
chrome_opt.add_experimental_option('prefs',prefs)
brower = webdriver.Chrome(executable_path='/home/yumengfsd/PycharmProjects/ArticleSpider/chromedriver',chrome_options=chrome_opt)
brower.get('https://www.jd.com')


