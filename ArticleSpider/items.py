# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import datetime

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join

from settings import SQL_DATETIME_FORMAT
from utils.common import extract_num
from w3lib.html import remove_tags


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
    title = scrapy.Field()
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
        input_processor=MapCompose(extract_num)
    )
    fav_num = scrapy.Field(
        input_processor=MapCompose(extract_num)
    )
    com_num = scrapy.Field(
        input_processor=MapCompose(extract_num)
    )
    content = scrapy.Field()
    tags = scrapy.Field(
        intput_processor=MapCompose(remove_comment_tag),
        output_processor=Join(',')
    )

    def get_insert_sql(self):
        insert_sql = """
                        insert into jobbole_article(title, create_date, url, fav_nums,url_object_id,front_image_path,comment_nums,praise_nums,tags,content,front_image_url)
                        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        ON DUPLICATE KEY UPDATE fav_nums=VALUES(fav_nums),comment_nums=VALUES(comment_nums),praise_nums=VALUES(praise_nums)
                    """
        params = (self["title"], self["create_date"], self["url"], self["fav_num"], self["url_object_id"],
                  self["front_image_path"], self['com_num'], self['praise_num'], self['tags'], self['content'],
                  self['front_image_url'][0])
        return insert_sql, params


class ZhihuQuestionItem(scrapy.Item):
    zhihu_id = scrapy.Field()
    topics = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answer_num = scrapy.Field()
    comments_num = scrapy.Field()
    watch_user_num = scrapy.Field()
    click_num = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
                           insert into zhihu_question(zhihu_id, topics, url, title, content, answer_num,comments_num,
                              watch_user_num,crawl_time)
                           VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)
                           ON DUPLICATE KEY UPDATE content=VALUES (content),answer_num=VALUES (answer_num),comments_num=VALUES (comments_num),
                              watch_user_num=VALUES (watch_user_num)
                          
                       """
        zhihu_id = self["zhihu_id"][0]
        topics = ','.join(self["topics"])
        url = self["url"][0]
        title = ''.join(self["title"])
        content = ''.join(self["content"])
        answer_num = extract_num(''.join(self["answer_num"]))
        comments_num = extract_num(''.join(self['comments_num']))
        watch_user_num = extract_num(''.join(self['watch_user_num']))
        # click_num = extract_num(''.join(self['click_num']))
        crawl_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)

        params = (zhihu_id, topics, url, title, content, answer_num, comments_num, watch_user_num, crawl_time)
        return insert_sql, params


class ZhihuAnswerItem(scrapy.Item):
    zhihu_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    parise_num = scrapy.Field()
    comments_num = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
                           insert into zhihu_answer (zhihu_id, url, question_id, author_id, content,
                               priase_num, comments_num, create_time, update_time, crawl_time)
                           VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                           ON DUPLICATE KEY UPDATE content=VALUES (content),comments_num=VALUES (comments_num),
                                priase_num=VALUES (priase_num),update_time=VALUES (update_time)

                       """

        create_time = datetime.datetime.fromtimestamp(self['create_time']).strftime(SQL_DATETIME_FORMAT)
        update_time = datetime.datetime.fromtimestamp(self['update_time']).strftime(SQL_DATETIME_FORMAT)

        params = (
            self['zhihu_id'], self['url'], self['question_id'], self['author_id'], self['content'],
            self['parise_num'], self['comments_num'], create_time, update_time,
            self['crawl_time'].strftime(SQL_DATETIME_FORMAT),
        )
        return insert_sql, params


def remove_splash(value):
    # 去掉工作中的斜线
    return value.replace('/', '')


def handel_addrr(value):
    addr_list = value.split('\n')
    addr_list = [item.strip() for item in addr_list if item.strip() != '查看地图']
    return ''.join(addr_list)


class LagouJobItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class LagouJonItem(scrapy.Item):
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    title = scrapy.Field()
    salary = scrapy.Field()
    job_city = scrapy.Field(
        input_processor=MapCompose(remove_splash)
    )
    work_years = scrapy.Field(
        input_processor=MapCompose(remove_splash)
    )
    degree_need = scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    job_type = scrapy.Field()
    publish_time = scrapy.Field()
    tags = scrapy.Field(
        input_processor=Join(',')
    )
    job_advantage = scrapy.Field()
    job_desc = scrapy.Field()
    job_addr = scrapy.Field(
        input_processor=MapCompose(remove_tags, handel_addrr),
    )
    company_url = scrapy.Field()
    company_name = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
                           insert into lagou_job(url, url_object_id, title, salary,
                                                job_city, work_years, degree_need,job_type, 
                                                publish_time, tags, job_advantage, job_desc,
                                                 job_addr, company_url, company_name,crawl_time) 
                           VALUES (%s,%s,%s,%s,
                                   %s,%s,%s,%s,
                                   %s,%s,%s,%s,
                                   %s,%s,%s,%s)
                           ON DUPLICATE KEY UPDATE salary=VALUES (salary),work_years=VALUES (work_years),
                                publish_time=VALUES (publish_time)

                       """
        params = (
            self['url'], self['url_object_id'], self['title'], self['salary'],
            self['job_city'], self['work_years'], self['degree_need'], self['job_type'],
            self['publish_time'], self['tags'], self['job_advantage'], self['job_desc'],
            self['job_addr'], self['company_url'], self['company_name'],
            self['crawl_time'].strftime(SQL_DATETIME_FORMAT),
        )
        return insert_sql, params

