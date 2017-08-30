# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import MySQLdb
import MySQLdb.cursors

from scrapy.pipelines.images import ImagesPipeline
from twisted.enterprise import adbapi


class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item

# 异步保存
class MysqlTwistedPipleline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    # 读取设置中的数据库配置
    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            password=settings['MYSQL_PASSWORD'],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbparms)
        return cls(dbpool)

    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error)

    def handle_error(self, failure):
        print(failure)

    def do_insert(self, cursor, item):
        insert_sql, params = item.get_insert_sql()
        cursor.execute(insert_sql, params)


# 获取链接地址
class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if 'front_image_url' in item:
            for ok, values in results:
                image_file_path = values['path']
            item['front_image_path'] = image_file_path

        return item
