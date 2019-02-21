# -*- coding: utf-8 -*-
import json
import re

import scrapy
import pymongo
from recruit_spider.config import mongo_host
from recruit_spider.items import LaGouSpiderItem
from recruit_spider.proxy import Proxy


class Lagou(scrapy.Spider):
    name = 'lagou'

    start_urls = ['https://www.lagou.com/jobs/list_python?px=default&city=%E4%B8%8A%E6%B5%B7']

    def start_requests(self):
        proxy = Proxy()
        print(proxy.proxy)
        yield scrapy.Request(
            url='https://www.lagou.com/jobs/list_python?px=default&city=%E4%B8%8A%E6%B5%B7',
            meta={'proxy_list': proxy},
            callback=self.init_parse
        )

    def init_parse(self, response):

        set_cookie = str(response.headers.getlist('Set-Cookie'))

        print(set_cookie)

        if not set_cookie:
            print(1)
            self.start_requests()

        JSESSIONID = re.search('JSESSIONID=.*?;', set_cookie).group(0)
        SEARCH_ID = re.search('SEARCH_ID=.*?;', set_cookie).group(0)
        LGRID = re.search('LGRID=.*?(?=;)', set_cookie).group(0)
        cookie = JSESSIONID + SEARCH_ID + LGRID

        return scrapy.FormRequest(
            url='https://www.lagou.com/jobs/positionAjax.json?px=default&city=%E4%B8%8A%E6%B5%B7&needAddtionalResult=false',
            meta={'proxy': response.meta['proxy'], 'delivery': response.meta['proxy_list']},
            formdata={'first': 'true', 'pn': '1', 'kd': 'python'},
            headers={'Cookie': cookie},
            callback=self.parse
        )

    def parse(self, response):
        data = json.loads(response.body.decode('utf8'))

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

            yield scrapy.Request(url=item['position_url'],
                                 meta={"item": item, 'proxy_list': response.meta['delivery']},
                                 callback=self.detail_parse, dont_filter=True)

    def detail_parse(self, response):
        item = response.meta['item']
        item['position_detail_info'] = self.get_position_detail_info(response)
        yield item

    @staticmethod
    def get_position_detail_info(position):
        content = position.xpath('//div[@class="content_l fl"]/dl[@class="job_detail"]/dd[@class="job_bt"]/div[@class="job-detail"]/descendant::*/text()').re('[^\xa0]+')
        return content



