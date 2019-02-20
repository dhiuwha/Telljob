import json
import random

import requests

from recruit_spider.config import proxy_api


class Proxy:

    def __init__(self):
        self.proxy = self.get_proxy_json()

    @staticmethod
    def get_proxy_json():
        result = requests.get(proxy_api).content.decode('utf8')
        return json.loads(result)['msg']

    def random_choose(self):
        return random.choice(self.proxy)

    @staticmethod
    def splice_ip(proxy):
        return 'https://' + proxy['ip'] + ":" + str(proxy['port'])


if __name__ == '__main__':
    # r = requests.get(proxy_api)
    # print(r.status_code)
    # print(r.content.decode('utf8'))
    # print(r.text)
    print(Proxy().proxy)
