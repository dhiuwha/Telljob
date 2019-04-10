# -*- coding: utf-8 -*-
import datetime
import json
import logging
import re
import time

import redis
import scrapy
from scrapy_redis.spiders import RedisSpider

from recruit_spider.config import redis_host, redis_port
from recruit_spider.items import A51jobSpiderItem


class A51jobSpider(RedisSpider):
    name = '51job'

    redis_key = '51job:start_urls'

    education_filter = ['大专', '本科', '硕士', '博士']

    def make_requests_from_url(self, url):
        info = re.search('(?<=\.html).*', url).group(0)
        return scrapy.Request(url=url.replace(info, ""), meta=json.loads(info), callback=self.parse, dont_filter=True)

    def parse(self, response):
        position_url = self.get_position_url(response)
        for url in position_url:
            yield scrapy.Request(url=url, meta=dict({'url': url}, **response.meta),
                                 callback=self.detail_parse, dont_filter=True)

    def detail_parse(self, response):
        item = A51jobSpiderItem()

        item['city'] = response.meta['city']
        item['keyword'] = response.meta['keyword']
        item['position_name'] = self.get_position_name(response)
        item['position_url'] = response.meta['url']
        item['company_name'] = self.get_company_name(response)
        item['company_url'] = self.get_company_url(response)
        item['salary'] = self.get_position_salary(response)
        item['working_place'], item['experience_requirement'], item['educational_requirement'], \
            item['header_count'], item['publish_time'] = \
            self.get_position_basic_info(response).split('\xa0\xa0|\xa0\xa0')[:5]
        item['publish_time'] = re.search('\d{2}-\d{2}(?=发布)', item['publish_time']).group(0)
        item['position_detail_info'] = self.get_position_detail_info(response)
        item['insert_time'] = datetime.datetime.now()
        if item['educational_requirement'] not in self.education_filter:
            item['educational_requirement'] = "大专以下"
        if item['experience_requirement'] == "无工作经验":
            item['experience_requirement'] = "不限"
        elif '1' in item['experience_requirement'] or '2' in item['experience_requirement']:
            item['experience_requirement'] = "1-3年"
        elif '3' in item['experience_requirement'] or '4' in item['experience_requirement'] or '5' in item['experience_requirement']:
            item['experience_requirement'] = "3-5年"
        elif '10' in item['experience_requirement']:
            item['experience_requirement'] = "10年以上"
        else:
            item['experience_requirement'] = "5-10年"
        if '千' in item['salary']:
            begin = re.search('.+?(?=-)', item['salary']).group(0)
            end = re.search('(?<=-).+?(?=千)', item['salary']).group(0)
            item['salary'] = begin + 'k-' + end + 'k'
        elif '万' in item['salary']:
            begin = re.search('.+?(?=-)', item['salary']).group(0)
            end = re.search('(?<=-).+?(?=万)', item['salary']).group(0)
            item['salary'] = str(int(float(begin) * 10)) + 'k-' + str(int(float(end) * 10)) + 'k'
        yield item

    @staticmethod
    def get_position_name(position):
        return position.xpath('//div[@class="cn"]/h1/@title').extract_first()

    @staticmethod
    def get_position_url(position):
        return position.xpath('//div[@class="dw_table"]/div[@class="el"]/p/span/a/@href').extract()

    @staticmethod
    def get_company_name(position):
        return position.xpath('//div[@class="cn"]/p[@class="cname"]/a[@class="catn"]/@title').extract_first()

    @staticmethod
    def get_company_url(position):
        return position.xpath('//div[@class="cn"]/p[@class="cname"]/a[@class="catn"]/@href').extract_first()

    @staticmethod
    def get_position_basic_info(position):
        return position.xpath('//div[@class="cn"]/p[@class="msg ltype"]/@title').extract_first()

    @staticmethod
    def get_position_salary(position):
        return position.xpath('//div[@class="cn"]/strong/text()').extract_first()

    @staticmethod
    def get_position_detail_info(position):
        content = position.xpath('//div[@class="bmsg job_msg inbox"]/p/text()').re('[^\xa0]+')
        if len(content) == 0:
            content = position.xpath('//div[@class="bmsg job_msg inbox"]/p/descendant::*/text()').re('[^\xa0]+')
        return content
