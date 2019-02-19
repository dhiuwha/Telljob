# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class RecruitSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class A51jobSpiderItem(scrapy.Item):
    position_name = scrapy.Field()
    position_url = scrapy.Field()
    company_name = scrapy.Field()
    company_url = scrapy.Field()
    salary = scrapy.Field()
    working_place = scrapy.Field()
    experience_requirement = scrapy.Field()
    educational_requirement = scrapy.Field()
    header_count = scrapy.Field()
    publish_time = scrapy.Field()

    position_detail_info = scrapy.Field()


class BossSpiderItem(scrapy.Item):
    position_name = scrapy.Field()
    position_url = scrapy.Field()
    company_name = scrapy.Field()
    company_url = scrapy.Field()
    salary = scrapy.Field()
    working_place = scrapy.Field()
    experience_requirement = scrapy.Field()
    educational_requirement = scrapy.Field()
    header_count = scrapy.Field()
    publish_time = scrapy.Field()

    position_detail_info = scrapy.Field()


class ZhilianSpiderItem(scrapy.Item):
    position_name = scrapy.Field()
    position_url = scrapy.Field()
    company_name = scrapy.Field()
    company_url = scrapy.Field()
    salary = scrapy.Field()
    working_place = scrapy.Field()
    experience_requirement = scrapy.Field()
    educational_requirement = scrapy.Field()
    header_count = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    end_time = scrapy.Field()

    position_detail_info = scrapy.Field()


class LaGouSpiderItem(scrapy.Item):
    position_name = scrapy.Field()
    position_url = scrapy.Field()
    company_name = scrapy.Field()
    company_url = scrapy.Field()
    salary = scrapy.Field()
    working_place = scrapy.Field()
    experience_requirement = scrapy.Field()
    educational_requirement = scrapy.Field()
    header_count = scrapy.Field()
    publish_time = scrapy.Field()

    position_detail_info = scrapy.Field()
