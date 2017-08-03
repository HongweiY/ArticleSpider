# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json
import MySQLdb
import MySQLdb.cursors

from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi


class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item


class JsonWithEncodingPipeline(object):
    def __init__(self):
        self.file = codecs.open('article.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + '\n'
        self.file.write(lines)
        return item

    def spider_closed(self, spider):
        self.file.close()


class JsonExporterPipleline(object):
    def __init__(self):
        self.file = open('articleexport.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


class MysqlPipleline(object):
    def __init__(self):
        self.conn = MySQLdb.connect('127.0.0.1', 'ymfsder', 'abc123', 'article_spider', charset="utf8",
                                    use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """
           insert into jobbole_article(title, create_date, url, fav_nums,url_object_id)
           VALUES(%s,%s,%s,%s,%s)

       """
        self.cursor.execute(insert_sql,
                            (item["title"], item["create_date"], item["url"], item["fav_num"], item["url_object_id"]))
        self.conn.commit()


# 异步保存
class MysqlTwistedPipleline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    #读取设置中的数据库配置
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
        query.addErrback(self.handle_error())

    def handle_error(self, failure):
        print(failure)

    def do_insert(self, cursor, item):
        insert_sql = """
                   insert into jobbole_article(title, create_date, url, fav_nums,url_object_id,front_image_path,comment_nums,praise_nums,tags,content,front_image_url)
                   VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
               """
        cursor.execute(insert_sql,
                       (item["title"], item["create_date"], item["url"], item["fav_num"], item["url_object_id"],
                        item["front_image_path"], item['com_num'], item['praise_num'], item['tags'], item['content'],item['front_image_url'][0]))


#获取链接地址
class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if 'front_image_url' in item:
            for ok, values in results:
                image_file_path = values['path']
            item['front_image_path'] = image_file_path

        return item
