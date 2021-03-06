# -*- coding: utf-8 -*-

from urllib import parse

import scrapy
from scrapy.http import Request

from items import JobBoleArticleItem, ArticleItemLoader
from utils.common import get_md5
from selenium import webdriver
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from pyvirtualdisplay import Display


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def __init__(self):
        self.display = Display(visible=0, size=(800, 600))
        self.display.start()

        self.browser = webdriver.Chrome(executable_path='/home/yumengfsd/PycharmProjects/ArticleSpider/chromedriver')
        super(JobboleSpider, self).__init__()
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        # 当爬虫关闭时，关闭浏览器
        self.browser.quit()

    def parse(self, response):
        """
        1.获取文章列表页中的文章的url，并嫁给scrapy下载后进行解析
        2.获取下一页的url并交给scrapy进行下载


        :param response:
        :return:
        """

        # 1.获取文章列表页中的文章的url，并嫁给scrapy下载后进行解析
        post_nodes = response.css("#archive .floated-thumb .post-thumb a")
        for post_node in post_nodes:
            image_url = post_node.css("img::attr(src)").extract_first("")
            post_url = post_node.css("::attr(href)").extract_first("")
            yield Request(url=parse.urljoin(response.url, post_url), meta={"front_image_url": image_url},
                          callback=self.parse_detail)
        next_url = response.css(".next.page-numbers::attr(href)").extract_first("")
        if next_url:
            yield Request(url=parse.urljoin(response.url, post_url), callback=self.parse)

    def parse_detail(self, response):

        # 通过itemloder
        front_image_url = response.meta.get('front_image_url', '')
        item_loader = ArticleItemLoader(item=JobBoleArticleItem(), response=response)
        item_loader.add_css('title', '.entry-header h1::text')
        item_loader.add_value('url_object_id', get_md5(response.url))
        item_loader.add_css('create_date', '.entry-meta-hide-on-mobile::text')
        item_loader.add_value('url', response.url)
        item_loader.add_value('front_image_url', [front_image_url])
        item_loader.add_css('praise_num', '.vote-post-up h10::text')
        item_loader.add_css('fav_num', '.bookmark-btn::text')
        item_loader.add_css('com_num', "a[href='#article-comment'] span::text")
        item_loader.add_css('content', 'div.entry')
        item_loader.add_css('tags', 'p.entry-meta-hide-on-mobile a::text')

        article_item = item_loader.load_item()

        yield article_item
