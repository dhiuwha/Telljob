import json

import redis
import requests

from recruit_spider.config import zhima_proxy_api, mogu_proxy_api


class Proxy:

    def __init__(self, redis_conn):
        self.redis_conn = redis_conn

    @staticmethod
    def get_proxy_json():
        result = requests.get(zhima_proxy_api).content.decode('utf8')
        return json.loads(result)['data']

    # @staticmethod
    # def get_proxy_json():
    #     result = requests.get(mogu_proxy_api).content.decode('utf8')
    #     return json.loads(result)['msg']

    @staticmethod
    def splice_ip(proxy):
        return 'https://' + proxy['ip'] + ":" + str(proxy['port'])

    def put_into_redis(self):
        proxies = self.get_proxy_json()
        for element in proxies:
            self.redis_conn.sadd('zhima_proxy', self.splice_ip(element))
        # print(self.redis_conn.smembers('zhima_proxy'))


if __name__ == '__main__':
    # r = requests.get(proxy_api)
    # print(r.status_code)
    # print(r.content.decode('utf8'))
    # print(r.text)
    Proxy().put_into_redis()
