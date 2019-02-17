# -*- coding: utf-8 -*-
import scrapy
import pymongo
from recruit_spider.config import mongo_host


class Lagou(scrapy.Spider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com/']

    def parse(self, response):
        print(response.text)
        client = pymongo.MongoClient(host=mongo_host, port=27017)
        db = client['test']
        collection = db['lagou']
        collection.insert({"page": response.text})
