# -*- coding: utf-8 -*-
import json
import re
import time
import datetime

from urllib import parse

from zheye import zheye
from items import ZhihuQuestionItem, ZhihuAnswerItem
from scrapy.loader import ItemLoader

z = zheye()
import scrapy


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']
    # question的第一页answer的请求url
    start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?sort_by=default&include=data%5B%2A%5D.is_normal%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccollapsed_counts%2Creviewing_comments_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Cmark_infos%2Ccreated_time%2Cupdated_time%2Crelationship.is_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cupvoted_followees%3Bdata%5B%2A%5D.author.is_blocking%2Cis_blocked%2Cis_followed%2Cvoteup_count%2Cmessage_thread_token%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics&limit={1}&offset={2}"
    header = {
        "Host": "www.zhihu.com",
        'Referer': 'https://www.zhihu.com/',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
    }

    custom_settings = {
        'COOKIES_ENABLED': False,
    }

    def parse(self, response):
        """
        提取页面中的所有url,然后去匹配
        :param response:
        :return:
        """
        all_urls = response.css('a::attr(href)').extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        all_urls = filter(lambda x: True if x.startswith('https') else False, all_urls)
        for url in all_urls:
            match_obj = re.match('(.*www.zhihu.com/question/(\d+))(/|$).*', url)
            if match_obj:
                request_url = match_obj.group(1)
                yield scrapy.Request(request_url, headers=self.header, callback=self.parse_question)
            else:
                yield scrapy.Request(url, headers=self.header, callback=self.parse)

    def parse_question(self, response):

        if 'QuestionHeader-title' in response.text:
            match_obj = re.match('(.*www.zhihu.com/question/(\d+))(/|$).*', response.url)
            if match_obj:
                question_id = int(match_obj.group(2))
            item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
            item_loader.add_css("title", "h1.QuestionHeader-title::text")
            item_loader.add_css("content", ".QuestionHeader-detail")
            item_loader.add_value("url", response.url)
            item_loader.add_value("zhihu_id", question_id)
            item_loader.add_css("answer_num", ".List-headerText span::text")
            item_loader.add_css("comments_num", ".QuestionHeader-Comment button::text")
            item_loader.add_css("watch_user_num", ".NumberBoard-value::text")
            item_loader.add_css("topics", ".QuestionHeader-topics .Popover div::text")
            question_item = item_loader.load_item()
        else:
            # 处理老版本页面的item提取
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", response.url)
            if match_obj:
                question_id = int(match_obj.group(2))

            item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
            # item_loader.add_css("title", ".zh-question-title h2 a::text")
            item_loader.add_xpath("title",
                                  "//*[@id='zh-question-title']/h2/a/text()|//*[@id='zh-question-title']/h2/span/text()")
            item_loader.add_css("content", "#zh-question-detail")
            item_loader.add_value("url", response.url)
            item_loader.add_value("zhihu_id", question_id)
            item_loader.add_css("answer_num", "#zh-question-answer-num::text")
            item_loader.add_css("comments_num", "#zh-question-meta-wrap a[name='addcomment']::text")
            # item_loader.add_css("watch_user_num", "#zh-question-side-header-wrap::text")
            item_loader.add_xpath("watch_user_num",
                                  "//*[@id='zh-question-side-header-wrap']/text()|//*[@class='zh-question-followers-sidebar']/div/a/strong/text()")
            item_loader.add_css("topics", ".zm-tag-editor-labels a::text")

            question_item = item_loader.load_item()
        yield scrapy.Request(self.start_answer_url.format(question_id, 20, 2), headers=self.header,
                             callback=self.parse_answer)
        yield question_item

    def parse_answer(self, response):
        answer_json = json.loads(response.text)
        is_end = answer_json['paging']['is_end']
        totals = answer_json['paging']['totals']
        next_url = answer_json['paging']['next']

        # 提取answer的具体内容
        for answer in answer_json['data']:
            answer_item = ZhihuAnswerItem()
            answer_item['zhihu_id'] = answer['id']
            answer_item['url'] = answer['url']
            answer_item['question_id'] = answer['question']['id']
            answer_item['author_id'] = answer['author']['id'] if 'id' in answer['author'] else None
            answer_item['content'] = answer['content'] if 'content' in answer else None
            answer_item['parise_num'] = answer['voteup_count']
            answer_item['create_time'] = answer['created_time']
            answer_item['update_time'] = answer['updated_time']
            answer_item["comments_num"] = answer["comment_count"]
            answer_item['crawl_time'] = datetime.datetime.now()
            yield answer_item

        if not is_end:
            yield scrapy.Request(next_url, headers=self.header, callback=self.parse_answer)

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
