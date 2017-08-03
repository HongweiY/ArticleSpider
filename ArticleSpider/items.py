# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import datetime
import re

from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


# 处理时间
def date_convert(value):
    try:
        create_time = datetime.datetime.strftime(value, '%Y/%m/%d').date()
    except Exception as e:
        create_time = datetime.datetime.now().date()
    return create_time


# 定义数字获取函数
def get_num(value):
    match_com = re.match('.*?(\d+).*', value)
    if match_com:
        num = int(match_com.group(1))
    else:
        num = 0
    return num


# 移除tag中的评论
def remove_comment_tag(value):
    if '评论' in value:
        return ''
    else:
        return value


# 返回value
def return_value(value):
    return value


# 自定义ItemLoader
class ArticleItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class JobBoleArticleItem(scrapy.Item):
    title = scrapy.Field( )
    create_date = scrapy.Field(
        input_processor=MapCompose(date_convert)
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field(
        output_processor=MapCompose(return_value)
    )
    front_image_path = scrapy.Field()
    praise_num = scrapy.Field(
        input_processor=MapCompose(get_num)
    )
    fav_num = scrapy.Field(
        input_processor=MapCompose(get_num)
    )
    com_num = scrapy.Field(
        input_processor=MapCompose(get_num)
    )
    content = scrapy.Field()
    tags = scrapy.Field(
        intput_processor=MapCompose(remove_comment_tag),
        output_processor=Join(',')
    )
