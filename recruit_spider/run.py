import json
import os

address = ['master', 'slave1', 'slave2']


def deploy():
    for a in address:
        os.system('scrapyd-deploy ' + a + " -p recruit_spider")


def schedule():
    spider_name = ['51job', 'lagou', 'zhilian', 'boss']
    for s in spider_name:
        for a in address:
            os.system('curl http://' + a + ':6800/schedule.json -d project=recruit_spider -d spider=' + s)


def stop():
    for a in address:
        result = os.popen('curl http://' + a + ':6800/listjobs.json?project=recruit_spider')
        job_ids = map(lambda x: x['id'], json.loads(result.readlines()[0])['running'])
        for job_id in job_ids:
            os.system('curl http://' + a + ':6800/cancel.json -d project=recruit_spider -d job=' + job_id)


if __name__ == '__main__':
    deploy()
    schedule()
    # stop()
