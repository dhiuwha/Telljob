# -*- coding: utf-8 -*-
import json
import logging
import time

import scrapy
from scrapy_redis.spiders import RedisSpider

from recruit_spider.items import ZhilianSpiderItem


class ZhilianSpider(RedisSpider):
    name = 'zhilian'

    redis_key = 'zhilian:start_urls'

    def make_requests_from_url(self, url):
        return scrapy.Request(url=url, callback=self.parse, dont_filter=True)

    def parse(self, response):

        data = json.loads(response.body.decode('utf8'))
        for element in data['data']['results']:
            item = ZhilianSpiderItem()

            item['position_name'] = element['jobName']
            item['position_url'] = element['positionURL']
            item['company_name'] = element['company']['name']
            item['company_url'] = element['company']['url']
            item['working_place'] = element['city']['display']
            item['experience_requirement'] = element['workingExp']['name']
            item['educational_requirement'] = element['eduLevel']['name']
            item['salary'] = element['salary']
            item['create_time'] = element['createDate']
            item['update_time'] = element['updateDate']
            item['end_time'] = element['endDate']
            item['header_count'] = element['recruitCount']
            # if item['position_url'] == 'https://jobs.zhaopin.com/CC263265337J00086662006.htm':
            yield scrapy.Request(url=item['position_url'], meta={"item": item},
                                 callback=self.detail_parse, dont_filter=True)

    def detail_parse(self, response):
        item = response.meta['item']
        item['position_detail_info'] = self.get_position_detail_info(response)
        item['insert_time'] = time.time()
        yield item

    @staticmethod
    def get_position_detail_info(position):
        content = position.xpath(
            '//div[@class="responsibility pos-common"]/div[@class="pos-ul"]/text()').re('[^\xa0]+')
        content.extend(position.xpath(
                '//div[@class="responsibility pos-common"]/div[@class="pos-ul"]/descendant::*/text()').re('[^\xa0]+'))
        return content
