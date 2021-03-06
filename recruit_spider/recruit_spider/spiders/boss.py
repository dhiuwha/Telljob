# -*- coding: utf-8 -*-
import datetime
import json
import logging
import re
import time

import scrapy
from scrapy_redis.spiders import RedisSpider

from recruit_spider.items import BossSpiderItem


class BossSpider(RedisSpider):
    name = 'boss'

    redis_key = 'boss:start_urls'

    education_filter = ['大专', '本科', '硕士', '博士']

    def make_requests_from_url(self, url):
        info = re.search('(?<=&ka=page-\d).*', url).group(0)
        return scrapy.Request(url=url.replace(info, ""), meta=json.loads(info), callback=self.parse, dont_filter=True)

    def parse(self, response):

        position_url = self.get_position_url(response)
        # publish_time = self.get_publish_time(response)
        basic_info = self.get_position_basic_info(response)

        basic_info = [basic_info[i: i+3] for i in range(0, len(basic_info), 3)]

        for url, basic_info in map(lambda x, y: [x, y], position_url, basic_info):
            url = "https://www.zhipin.com" + url
            yield scrapy.Request(url=url, callback=self.detail_parse, dont_filter=True,
                                 meta=dict({'url': url, 'basic_info': basic_info}, **response.meta))

    def detail_parse(self, response):
        item = BossSpiderItem()

        item['city'] = response.meta['city']
        item['keyword'] = response.meta['keyword']
        item['position_name'] = self.get_position_name(response)
        item['position_url'] = response.meta['url']
        item['company_name'] = self.get_company_name(response)
        item['company_url'] = "https://www.zhipin.com" + self.get_company_url(response)
        item['salary'] = self.get_position_salary(response)
        item['working_place'], item['experience_requirement'], item['educational_requirement'] = \
            response.meta['basic_info']
        item['position_detail_info'] = self.get_position_detail_info(response)
        item['insert_time'] = datetime.datetime.now()
        item['experience_requirement'] = "不限" if item['experience_requirement'] == '1年以内' or item['experience_requirement'] == '应届生' or item['experience_requirement'] == '经验不限' else item['experience_requirement']
        if item['educational_requirement'] not in self.education_filter:
            item['educational_requirement'] = "大专以下"
        return item

    @staticmethod
    def get_position_name(position):
        return position.xpath('//div[@class="name"]/h1/text()').extract_first()

    @staticmethod
    def get_position_url(position):
        return position.xpath(
            '//ul/li/div[@class="job-primary"]/div[@class="info-primary"]/h3[@class="name"]/a/@href').extract()

    @staticmethod
    def get_company_name(position):
        return position.xpath('//div[@class="sider-company"]/div[@class="company-info"]/a[last()]/text()').re('\w+')[0]

    @staticmethod
    def get_company_url(position):
        return position.xpath('//div[@class="company-info"]/div/a[last()]/@href').extract_first()

    @staticmethod
    def get_position_basic_info(position):
        return position.xpath('//ul/li/div[@class="job-primary"]/div[@class="info-primary"]/p/text()').extract()

    @staticmethod
    def get_position_salary(position):
        return position.xpath('//div[@class="name"]/span[@class="salary"]/text()').re('\d+?k-\d+?k')[0]

    @staticmethod
    def get_publish_time(position):
        return position.xpath('//div[@class="info-publis"]/p/text()').re('\d+?月\d+?日')

    @staticmethod
    def get_position_detail_info(position):
        content = position.xpath('//div[@class="job-sec"]/div[@class="text"]/text()').re('[^\xa0]+')
        return content

