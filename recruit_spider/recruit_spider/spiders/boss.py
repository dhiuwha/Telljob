# -*- coding: utf-8 -*-
import scrapy

from recruit_spider.items import BossSpiderItem


class BossSpider(scrapy.Spider):
    name = 'boss'
    # allowed_domains = ['www.zhipin.com']
    start_urls = ['https://www.zhipin.com/job_detail/?query=python&scity=101010100&industry=&position=']

    def parse(self, response):
        position_url = self.get_position_url(response)
        publish_time = self.get_publish_time(response)
        basic_info = self.get_position_basic_info(response)
        for index in range(len(self.get_position_basic_info(response))):
            pass

        for url, publish_time, basic_info in map(lambda x, y, z: [x, y, z], position_url, publish_time, basic_info):
            url = "https://www.zhipin.com" + url
            yield scrapy.Request(url=url, meta={'url': url, 'publish_time': publish_time, 'basic_info': basic_info},
                                 callback=self.detail_parse, dont_filter=True)

    def detail_parse(self, response):
        item = BossSpiderItem()
        item['position_name'] = self.get_position_name(response)
        item['position_url'] = "https://www.zhipin.com" + response.meta['url']
        item['company_name'] = self.get_company_name(response)
        item['company_url'] = self.get_company_url(response)
        item['salary'] = self.get_position_salary(response)
        print(response.meta['basic_info'])
        item['working_place'], item['experience_requirement'], item['educational_requirement'] = \
            response.meta['basic_info']
        item['publish_time'] = response.meta['publish_time']
        return item

    @staticmethod
    def get_position_name(position):
        return position.xpath('//div[@class="name"]/h1/text()').extract()[0]

    @staticmethod
    def get_position_url(position):
        return position.xpath(
            '//ul/li/div[@class="job-primary"]/div[@class="info-primary"]/h3[@class="name"]/a/@href').extract()

    @staticmethod
    def get_company_name(position):
        return position.xpath('//div[@class="company-info"]/div/a/text()').re('[^\xa0\s]*')[1]

    @staticmethod
    def get_company_url(position):
        return position.xpath('//div[@class="company-info"]/div/a/@href').extract()[0]

    @staticmethod
    def get_position_basic_info(position):
        return position.xpath('//ul/li/div[@class="job-primary"]/div[@class="info-primary"]/p/text()').extract()

    @staticmethod
    def get_position_salary(position):
        return position.xpath('//div[@class="name"]/span[@class="salary"]/text()').re('[^\xa0\s]*')

    @staticmethod
    def get_publish_time(position):
        return position.xpath('//div[@class="info-publis"]/p/text()').re('[^\xa0\s]*')

    @staticmethod
    def get_position_detail_info(position):
        content = position.xpath('//div[@class="job-sec"]/descendant::*/text()').re('[^\xa0]*')
        # if len(content) == 0:
        #     content = position.xpath('//div[@class="bmsg job_msg inbox"]/p/span/text()').re('[^\xa0]*')
        for sentence in content:
            if sentence == '' or sentence == ' ':
                content.remove(sentence)
        return content

