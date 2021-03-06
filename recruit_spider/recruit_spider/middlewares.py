# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import base64
import logging
import random
import time

import redis
import requests
from scrapy import signals

from recruit_spider.config import user_agent, redis_host, redis_port, abu_host, \
    abu_port, abu_user, abu_pwd
from recruit_spider.proxy import Proxy


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

    redis_pool = redis.ConnectionPool(host=redis_host, port=redis_port, decode_responses=True)
    redis_conn = redis.Redis(connection_pool=redis_pool)

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

        redis_member_num = self.redis_conn.scard('zhima_proxy')
        #
        if redis_member_num < 5:
            if self.redis_conn.get('proxy_lock') != 'locked':
                self.redis_conn.set('proxy_lock', 'locked')
                Proxy(self.redis_conn).put_into_redis()
                self.redis_conn.set('proxy_lock', 'released')
            else:
                time.sleep(1)

        if 'lagou' in request.url or 'verify' in request.url or 'login' in request.url:
            request.meta['proxy'] = 'http://http-dyn.abuyun.com:9020'
            proxyAuth = "Basic " + base64.urlsafe_b64encode(bytes((abu_user + ":" + abu_pwd), "ascii")).decode(
                "utf8")
            request.headers["Proxy-Authorization"] = proxyAuth
        else:
            proxy = self.redis_conn.srandmember('zhima_proxy')
            logging.info(proxy)
            request.meta['proxy'] = proxy


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

        self.redis_conn.srem('zhima_proxy', request.meta['proxy'])

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
