# -*- coding: utf-8 -*-
import scrapy


class BossSpider(scrapy.Spider):
    name = 'boss'
    allowed_domains = ['www.zhipin.com']
    start_urls = ['https://www.zhipin.com/']

    def parse(self, response):
        pass
