# -*- coding: utf-8 -*-
import scrapy


class ZhilianSpider(scrapy.Spider):
    name = 'zhilian'
    allowed_domains = ['www.zhaopin.com']
    start_urls = ['https://www.zhaopin.com/']

    def parse(self, response):
        pass
