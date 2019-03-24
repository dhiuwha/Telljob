# -*- coding: utf-8 -*-
import datetime
import json
import logging
import re
import time

import redis
import scrapy
import pymongo
from scrapy_redis.spiders import RedisSpider

from recruit_spider.config import mongo_host, redis_host, redis_port
from recruit_spider.items import LaGouSpiderItem
from recruit_spider.proxy import Proxy


class Lagou(RedisSpider):
    name = 'lagou'

    redis_key = 'lagou:start_urls'

    redis_pool = redis.ConnectionPool(host=redis_host, port=redis_port, decode_responses=True)
    redis_conn = redis.Redis(connection_pool=redis_pool)

    def make_requests_from_url(self, url):
        info = re.search('(?<=&suginput=).*', url).group(0)
        return scrapy.Request(url=url.replace(info, ""), meta=json.loads(info), callback=self.init_parse, dont_filter=True)

    def init_parse(self, response):

        if 'https://www.lagou.com/utrack/verify.html' in response.url:
            self.redis_conn.srem('zhima_proxy', response.meta['proxy'])
            return scrapy.Request(url=response.url, meta=response.meta, callback=self.init_parse, dont_filter=True)
        logging.info('---------------init:' + response.url)
        set_cookie = str(response.headers.getlist('Set-Cookie'))
        try:
            JSESSIONID = re.search('JSESSIONID=.*?;', set_cookie).group(0)
            SEARCH_ID = re.search('SEARCH_ID=.*?;', set_cookie).group(0)
            LGRID = re.search('LGRID=.*?(?=;)', set_cookie).group(0)
            cookie = JSESSIONID + SEARCH_ID + LGRID
        except AttributeError:
            self.redis_conn.srem('zhima_proxy', response.meta['proxy'])
            return scrapy.Request(url=response.url, meta=response.meta, callback=self.init_parse, dont_filter=True)
        logging.info(cookie)
        logging.info({'first': 'true' if response.meta['page'] == '1' else 'false', 'pn': response.meta['page'], 'kd': response.meta['keyword']})
        yield scrapy.FormRequest(
            url='https://www.lagou.com/jobs/positionAjax.json?px=default&city=' + response.meta['city'] + '&needAddtionalResult=false',
            meta=dict({'proxy': response.meta['proxy']}, **response.meta),
            formdata={'first': 'true' if response.meta['page'] == '1' else 'false', 'pn': response.meta['page'], 'kd': response.meta['keyword']},
            headers={'Cookie': cookie},
            callback=self.parse
        )

    def parse(self, response):
        data = json.loads(response.body.decode('utf8'))
        logging.info(data)

        for element in data['content']['positionResult']['result']:
            item = LaGouSpiderItem()

            item['city'] = response.meta['city']
            item['keyword'] = response.meta['keyword']
            item['position_name'] = element['positionName']
            item['position_url'] = "https://www.lagou.com/jobs/" + str(element['positionId']) + ".html"
            item['company_name'] = element['companyFullName']
            item['company_url'] = "https://www.lagou.com/gongsi/" + str(element['companyId']) + ".html"
            item['working_place'] = element['city'] + " " + element['district']
            item['experience_requirement'] = element['workYear']
            item['educational_requirement'] = element['education']
            item['salary'] = element['salary']
            item['publish_time'] = element['createTime']

            yield scrapy.Request(url=item['position_url'],
                                 meta={"item": item},
                                 callback=self.detail_parse, dont_filter=True)

    def detail_parse(self, response):
        logging.info('-----------------' + response.url)
        if ' https://www.lagou.com/utrack/verify.html' in response.url:
            logging.info('---------------enter')
            self.redis_conn.srem('zhima_proxy', response.meta['proxy'])
            return scrapy.Request(url=response.meta['item'],
                                  meta={"item": response.meta['item']},
                                  callback=self.detail_parse, dont_filter=True)
        item = response.meta['item']
        item['position_detail_info'] = self.get_position_detail_info(response)
        item['insert_time'] = datetime.datetime.now()
        return item

    @staticmethod
    def get_position_detail_info(position):
        content = position.xpath('//div[@class="content_l fl"]//dd[@class="job_bt"]/descendant::*/text()').re('[^\xa0]+')
        return content



