# -*- coding: utf-8 -*-
import datetime
import json
import logging
import re
import time

import redis
import scrapy
import pymongo
from scrapy_redis.spiders import RedisSpider

from recruit_spider.config import mongo_host, redis_host, redis_port
from recruit_spider.items import LaGouSpiderItem
from recruit_spider.proxy import Proxy


class Lagou(RedisSpider):
    name = 'lagou'

    redis_key = 'lagou:start_urls'

    redis_pool = redis.ConnectionPool(host=redis_host, port=redis_port, decode_responses=True)
    redis_conn = redis.Redis(connection_pool=redis_pool)

    def make_requests_from_url(self, url):
        info = re.search('(?<=&suginput=).*', url).group(0)
        url = url.replace(info, "")
        info = json.loads(info)
        info['init_url'] = url
        return scrapy.Request(url=url, meta=info, callback=self.init_parse, dont_filter=True)

    def init_parse(self, response):
        logging.info(response.url)
        if 'https://www.lagou.com/utrack/' in response.url:
            time.sleep(2)
            self.redis_conn.srem('zhima_proxy', response.meta['proxy'])
            logging.info(response.meta['init_url'])
            return scrapy.Request(url=response.meta['init_url'], meta=response.meta, callback=self.init_parse, dont_filter=True)
        else:
            print('-----------------not verify')
            set_cookie = str(response.headers.getlist('Set-Cookie'))
            logging.info(set_cookie)
            try:
                JSESSIONID = re.search('JSESSIONID=.*?;', set_cookie).group(0)
                SEARCH_ID = re.search('SEARCH_ID=.*?;', set_cookie).group(0)
                try:
                    user_trace_token = re.search('user_trace_token=.*?;', set_cookie).group(0)
                except AttributeError:
                    user_trace_token = ''
                X_HTTP_TOKEN = re.search('X_HTTP_TOKEN=.*?(?=;)', set_cookie).group(0)

            except AttributeError:
                return scrapy.Request(url=response.meta['init_url'], meta=response.meta, callback=self.init_parse, dont_filter=True)
            cookie = JSESSIONID + SEARCH_ID + user_trace_token + X_HTTP_TOKEN
            if response.meta["page"] != '1':
                return scrapy.FormRequest(
                    url='https://a.lagou.com/collect?v=1&_v=j31&a=1260963230&t=pageview&_s=1&dl=https%3A%2F%2Fwww.lagou.com%2Fjobs%2F' + \
                        'list_' + response.meta['keyword'] + '%3Fpx%3Dnew%26city%3D%25' + response.meta['city'] + '&dr=https%3A%2F%2Fwww.lagou.com' + \
                        '%2Fzhaopin%2F&ul=zh-cn&de=UTF-8&dt=%E6%89%BE%E5%B7%A5%E4%BD%9C-%E4%BA%92%E8%81%94%E7%BD%91%E6%8B%9B%E8%81%98%E6%B1%82%E8%81%8C%E7%BD%91-'
                        '%E6%8B%89%E5%8B%BE%E7%BD%91&sd=24-bit&sr=1716x927&vp=718x813&je=0&_u=MEAAAAQBK~&jid=959634670&cid=190625864.1553575548&tid=UA-41268416-1&_r=1&z=795162837',
                    meta=dict({'proxy': response.meta['proxy']}, **response.meta,
                              **{'JSESSIONID': JSESSIONID, 'SEARCH_ID': SEARCH_ID, 'user_trace_token': user_trace_token, 'X_HTTP_TOKEN': X_HTTP_TOKEN},
                              **{'url': response.url}),
                    headers={'Cookie': cookie, 'Referer': response.url},
                    callback=self.not_first_page,
                    dont_filter=True
                )
            else:
                return scrapy.FormRequest(
                    url='https://www.lagou.com/jobs/positionAjax.json?px=default&city=' + response.meta['city'] + '&needAddtionalResult=false',
                    meta=dict({'proxy': response.meta['proxy']}, **response.meta),
                    formdata={'first': 'true', 'pn': '1', 'kd': response.meta['keyword']},
                    headers={'Cookie': cookie},
                    callback=self.parse,
                    dont_filter=True
                )

    def not_first_page(self, response):
        set_cookie = str(response.headers.getlist('Set-Cookie'))
        logging.info(set_cookie)
        try:
            LGRID = re.search('LGRID=.*?;', set_cookie).group(0)
            LGSID = re.search('LGSID=.*?;', set_cookie).group(0)
            LGUID = re.search('LGUID=.*?;', set_cookie).group(0)
            # LGUID = ''
            cookie = LGSID + LGRID + LGUID + response.meta['JSESSIONID'] + \
                     response.meta['SEARCH_ID'] + response.meta['user_trace_token'] + response.meta['X_HTTP_TOKEN']
        except AttributeError:
            # self.redis_conn.srem('zhima_proxy', response.meta['proxy'])
            return scrapy.Request(url=response.meta['url'], meta=response.meta, callback=self.init_parse, dont_filter=True)
        print(cookie)
        yield scrapy.FormRequest(
            url='https://www.lagou.com/jobs/positionAjax.json?px=default&city=' + response.meta[
                'city'] + '&needAddtionalResult=false',
            meta=dict({'proxy': response.meta['proxy']}, **response.meta),
            formdata={'first': 'false', 'pn': response.meta['page'], 'kd': response.meta['keyword']},
            headers={'Cookie': cookie, 'Referer': response.meta['url']},
            callback=self.parse,
            dont_filter=True
        )

    def parse(self, response):
        data = json.loads(response.body.decode('utf8'))
        logging.info(data)

        for element in data['content']['positionResult']['result']:
            item = LaGouSpiderItem()

            item['city'] = response.meta['city']
            item['keyword'] = response.meta['keyword']
            item['position_name'] = element['positionName']
            item['position_url'] = "https://www.lagou.com/jobs/" + str(element['positionId']) + ".html"
            item['company_name'] = element['companyFullName']
            item['company_url'] = "https://www.lagou.com/gongsi/" + str(element['companyId']) + ".html"
            item['working_place'] = element['city'] + " " + element['district']
            item['experience_requirement'] = "不限" if element['workYear'] == '1年以下' or element['workYear'] == '应届毕业生' else element['workYear']
            item['educational_requirement'] = "大专以下" if element['education'] == '不要求' else element['education']
            item['salary'] = element['salary']
            item['publish_time'] = element['createTime']

            yield scrapy.Request(url=item['position_url'],
                                 meta={"item": item, "url": response.url},
                                 callback=self.detail_parse, dont_filter=True)

    def detail_parse(self, response):
        logging.info('-----------------' + response.url)
        if 'https://www.lagou.com/utrack' in response.url or 'login' in response.url:
            # time.sleep(3)
            logging.info('---------------original url' + response.meta['item']['position_url'])
            logging.info('---------------referer' + response.meta['url'])
            # self.redis_conn.srem('zhima_proxy', response.meta['proxy'])
            return scrapy.Request(url=response.meta['item']['position_url'],
                                  meta=response.meta,
                                  headers={'Referer': response.meta['url']},
                                  callback=self.detail_parse, dont_filter=True)
        item = response.meta['item']
        item['position_detail_info'] = self.get_position_detail_info(response)
        item['insert_time'] = datetime.datetime.now()
        return item

    @staticmethod
    def get_position_detail_info(position):
        content = position.xpath('//div[@class="content_l fl"]//dd[@class="job_bt"]/descendant::*/text()').re('[^\xa0]+')
        return content



