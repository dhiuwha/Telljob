# -*- coding: utf-8 -*-
import json
import re

import scrapy
import pymongo
from recruit_spider.config import mongo_host
from recruit_spider.items import LaGouSpiderItem


class Lagou(scrapy.Spider):
    name = 'lagou'

    start_urls = ['https://www.lagou.com/jobs/list_python?px=default&city=%E4%B8%8A%E6%B5%B7']

    def start_requests(self):
        yield scrapy.Request(
            url='https://www.lagou.com/jobs/list_python?px=default&city=%E4%B8%8A%E6%B5%B7',
            callback=self.init_parse
        )

    def init_parse(self, response):

        set_cookie = str(response.headers.getlist('Set-Cookie'))

        JSESSIONID = re.search('JSESSIONID=.*?;', set_cookie).group(0)
        SEARCH_ID = re.search('SEARCH_ID=.*?;', set_cookie).group(0)
        LGRID = re.search('LGRID=.*?(?=;)', set_cookie).group(0)
        cookie = JSESSIONID + SEARCH_ID + LGRID

        return scrapy.FormRequest(
            url='https://www.lagou.com/jobs/positionAjax.json?px=default&city=%E4%B8%8A%E6%B5%B7&needAddtionalResult=false',
            formdata={'first': 'true', 'pn': '1', 'kd': 'python'},
            headers={'Cookie': cookie},
            callback=self.parse
        )

    def parse(self, response):
        data = json.loads(response.body.decode('utf8'))
        print(data['content']['positionResult']['result'])
        for element in data['content']['positionResult']['result']:
            item = LaGouSpiderItem()

            item['position_name'] = element['positionName']
            item['position_url'] = "https://www.lagou.com/jobs/" + str(element['positionId']) + ".html"
            item['company_name'] = element['companyFullName']
            item['company_url'] = "https://www.lagou.com/gongsi/" + str(element['companyId']) + ".html"
            item['working_place'] = element['city'] + " " + element['district']
            item['experience_requirement'] = element['workYear']
            item['educational_requirement'] = element['education']
            item['salary'] = element['salary']
            item['publish_time'] = element['createTime']
            print(item['position_url'])
            yield scrapy.Request(url=item['position_url'], meta={"item": item}, callback=self.detail_parse, dont_filter=True)

    def detail_parse(self, response):
        print(1)
        item = response.meta['item']
        item['position_detail_info'] = self.get_position_detail_info(response)
        yield item

    @staticmethod
    def get_position_detail_info(position):
        content = position.xpath('//div[@class="job-detail"]/p/text()').re('[^\xa0]+')
        # content.extend(position.xpath(
        #         '//div[@class="responsibility pos-common"]/div[@class="pos-ul"]/descendant::*/text()').re('[^\xa0\s]+'))
        return content



