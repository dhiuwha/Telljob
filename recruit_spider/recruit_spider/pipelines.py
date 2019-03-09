# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import logging

import pymongo

from recruit_spider.config import mongo_host, mongo_port, mongo_schema


class RecruitSpiderPipeline(object):

    client = pymongo.MongoClient(host=mongo_host, port=mongo_port)
    db = client[mongo_schema]
    collection = {
        '51job': db['51job'],
        'zhilian': db['zhilian'],
        'boss': db['boss'],
        'lagou': db['lagou']
    }

    def process_item(self, item, spider):

        self.collection[spider.name].insert(dict(item))

        return item

    def close_spider(self):
        self.client.close()


if __name__ == '__main__':
    rsp = RecruitSpiderPipeline()
    rsp.db['51job'].insert({
        'url': 'ppp'
    })
