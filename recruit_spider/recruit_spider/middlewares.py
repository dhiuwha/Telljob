# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import random
import time

import redis
import requests
from scrapy import signals

from recruit_spider.config import user_agent, remove_proxy_api, get_proxy_api


class RecruitSpiderSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        print('-------------spider exception--------------')
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class RecruitSpiderDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called

        request.headers['User-Agent'] = random.choice(user_agent)

        if 'https://www.lagou.com/jobs/positionAjax.json?' not in request.url:
            request.meta['proxy'] = requests.post(get_proxy_api).text

        # redis_conn = request.meta.get('redis_conn')
        # if not redis_conn:
        #     redis_pool = redis.ConnectionPool(host=redis_host, port=redis_port, decode_responses=True)
        #     redis_conn = redis.Redis(connection_pool=redis_pool)
        # redis_member_num = redis_conn.scard('zhima_proxy')
        #
        # if redis_member_num < 3:
        #     if redis_conn.get('proxy_lock') != 'locked':
        #         redis_conn.set('proxy_lock', 'locked')
        #         Proxy(redis_conn).put_into_redis()
        #         redis_conn.set('proxy_lock', 'released')
        #     else:
        #         time.sleep(1)
        #
        # if 'https://www.lagou.com/jobs/positionAjax.json?' not in request.url:
        #     proxy = redis_conn.srandmember('zhima_proxy')
        #     request.meta['proxy'] = proxy

        print(request.meta['proxy'])
        # if 'proxy_list' in request.meta:
        #     proxy_obj = request.meta['proxy_list']
        #     # print(proxy_obj.proxy)
        #     request.meta['temp_proxy'] = proxy_obj.random_choose()
        #     request.meta['proxy'] = proxy_obj.splice_ip(request.meta['temp_proxy'])
            # raise TypeError
        pass

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        # print(spider.name, response.headers.getlist('Set-Cookie'))
        # if spider.name == 'lagou' and response.headers.getlist('Set-Cookie') is []:
        #     raise ConnectionError
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        print('---------------error--------------------')
        requests.post(remove_proxy_api, data={'failure_proxy': request.meta['proxy']})
        # redis_conn = request.meta['redis_conn']
        #
        # redis_conn.srem('zhima_proxy', request.meta['proxy'])


        # proxy_obj = request.meta['proxy_list']
        # if len(proxy_obj.proxy) == 0:
        #     request.meta['proxy_list'] = Proxy()
        #     proxy_obj = request.meta['proxy_list']
        # proxy_obj.proxy.remove(request.meta['temp_proxy'])
        # request.meta['temp_proxy'] = proxy_obj.random_choose()
        # request.meta['proxy'] = proxy_obj.splice_ip(request.meta['temp_proxy'])
        # return request

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
