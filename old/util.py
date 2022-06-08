""" 公用 Utils """
# 要更改公网ip获取源，在PublicIP类中写入新的函数，
# 并将函数加入PublicIP.public_ip_list中即可，函数返回文本类型IP值


import logging
import json
import requests
from os import path

import config


BASEPATH = path.dirname(__file__)


# LOG
def setLog():
    """ log """
    # datefmt='%Y-%m-%d %H:%M:%S'
    LOGGER = logging.Logger(__name__)
    LOGGER.setLevel(config.logLevel)

    logFile = logging.FileHandler(config.logPath)
    logFile
    format = logging.Formatter(
        '\n%(asctime)s - %(filename)s: %(lineno)d - %(levelname)s: %(message)s')
    logFile.setFormatter(format)
    LOGGER.addHandler(logFile)
    return LOGGER


LOGGER = setLog()


# ---公网IP获取网址---

class PublicIP():
    """ get public IP -> 'xxx.xxx.xx.xx' """

    def __init__(self) -> None:
        # ---公网IP列表---
        self.public_ip_list = [self.ip_jsonip,
                               self.ip_ipip
                               ]

    @staticmethod
    def ip_jsonip() -> list:
        """ https://jsonip.com """
        try:
            r = requests.get('https://jsonip.com')
            res = [r.status_code, ]
            if res[0] == 200:

                r = json.loads(r.text)
                res.append(r['ip'])
                LOGGER.debug('1 - jonip.com:' + str(res))

            else:
                res.append('failed')
                LOGGER.warning(
                    'jsonip.com requests failed: ' + str(r.status_code))
        except Exception as e:
            res = ['requests 404', ]
            LOGGER.warning('jsonip.com requests failed')
            LOGGER.debug(e)

        return res

    @staticmethod
    def ip_ipip() -> list:
        """ http://myip.ipip.net """
        from re import search

        try:
            r = requests.get('http://myip.ipip.net')
            res = [r.status_code, ]
            if res[0] == 200:

                r = r.text
                r = search(r'(\d{1,3}\.){3}\d{1,3}', r)
                res.append(r.group())
                LOGGER.debug('2 - ipip.com:' + str(res))

            else:
                res.append('failed')
                LOGGER.warning(
                    'jsonip.com requests failed: ' + str(r.status_code))
        except Exception as e:
            res = ['requests 404', ]
            LOGGER.warning('jsonip.com requests failed')
            LOGGER.debug(e)

        return res


# login
with open(path.join(BASEPATH, 'PRIVATE'), mode='r', encoding='utf-8') as f:
    TASKS = json.load(f)
