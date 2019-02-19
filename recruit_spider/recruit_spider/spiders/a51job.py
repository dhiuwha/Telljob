# -*- coding: utf-8 -*-
import re

import scrapy

from recruit_spider.items import A51jobSpiderItem


class A51jobSpider(scrapy.Spider):
    name = '51job'

    start_urls = ['https://search.51job.com/list/120700,000000,0000,00,9,99,python,2,1.html']

    def parse(self, response):
        position_url = self.get_position_url(response)
        for url in position_url:
            yield scrapy.Request(url=url, meta={'url': url}, callback=self.detail_parse, dont_filter=True)

    def detail_parse(self, response):
        item = A51jobSpiderItem()

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

