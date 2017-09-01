# -*- coding: utf-8 -*-

__mktime__ = '17-8-30'
__author__ = 'ymfsder'

import requests
import MySQLdb
from scrapy.selector import Selector

conn = MySQLdb.connect('127.0.0.1', 'ymfsder', 'abc123', 'article_spider', charset="utf8", use_unicode=True)
cursor = conn.cursor()


def crawl_ips():
    headers = {

        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
    }
    for i in range(1000):
        re = requests.get('http://www.xicidaili.com/nn/{0}'.format(i), headers=headers)
        selector = Selector(text=re.text)
        all_trs = selector.css('#ip_list tr')
        ip_list = []
        for tr in all_trs[1:]:
            speed_str = tr.css('.bar::attr(title)').extract()[0]
            if speed_str:
                speed = float(speed_str.split('秒')[0])
            all_text = tr.css('td::text').extract()
            ip = all_text[0]
            port = all_text[1]
            proxy_type = all_text[5]
            ip_list.append((ip, port, proxy_type, speed))

        for ip_info in ip_list:
            if ip_info[2] == 'HTTP' and ip_info[3] < 2:
                cursor.execute(
                    "insert into proxy_ip(ip, port,speed,proxy_type) VALUES('{0}','{1}','{2}','{3}')".
                        format(ip_info[0], ip_info[1], ip_info[3], ip_info[2])
                )
                conn.commit()




class GetIP(object):
    def jude_ip(self, ip, port):
        http_url = 'https://www.baidu.com'
        proxy_url = 'http://{0}:{1}'.format(ip, port)
        try:
            proxy_dict = {
                'http': proxy_url,
            }
            response = requests.get(http_url, proxies=proxy_dict)
            return True
        except Exception as e:
            print('invalid ip and port')
            self.del_ip(ip)
            return False
        else:
            code = response.status_code
            if code >= 200 and code <= 300:
                print('effective ip')
                return True
            else:
                print('invalid ip and port')
                self.del_ip(ip)
                return False

    def del_ip(self, ip):
        del_sql = """
           delete from proxy_ip WHERE ip='{}'
        """.format(ip)
        cursor.execute(del_sql)
        conn.commit()
        return True

    def get_random_ip(self):
        sql = """
        select ip,port from proxy_ip ORDER BY rand() limit 1
        """
        cursor.execute(sql)
        for ip_info in cursor.fetchall():
            ip = ip_info[0]
            port = ip_info[1]
            jude_ip=self.jude_ip(ip, port)
            if jude_ip:
                return 'http:{0}:{1}'.format(ip,port)
            else:
                return self.get_random_ip()


if __name__=='__main__':
    get_ip=GetIP()
    get_ip.get_random_ip()
