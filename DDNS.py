"""
更新阿里云的DNS解析列表

crontab 定时任务；
crontab -e



"""
# 不知道阿里云的dns解析记录超过一页运行起来有什么bug

from os import path
from aliyunsdkcore.client import AcsClient
from aliyunsdkalidns.request.v20150109.DescribeDomainRecordsRequest import DescribeDomainRecordsRequest
from aliyunsdkalidns.request.v20150109.UpdateDomainRecordRequest import UpdateDomainRecordRequest
import logging
import requests
import json

import config


# LOG setting
def setLog():
    """ log """
    # datefmt='%Y-%m-%d %H:%M:%S'
    LOGGER = logging.Logger(__name__)
    LOGGER.setLevel(config.logLevel)

    logFile = logging.FileHandler(config.logPath)
    logFile
    format = logging.Formatter(
        '%(asctime)s - %(filename)s: %(lineno)d - %(levelname)s: %(message)s'
    )
    logFile.setFormatter(format)
    LOGGER.addHandler(logFile)
    return LOGGER


def loadParams():
    """ login params """
    with open(path.join(BASEPATH, 'PRIVATE'), mode='r', encoding='utf-8') as f:
        return json.load(f)


BASEPATH = path.dirname(__file__)

LOGGER = setLog()


class PublicIP():
    """ ---公网IP获取网址--- \n
     get public IP -> 'xxx.xxx.xx.xx' """

    def __init__(self) -> None:
        # ---公网IP列表---
        self.public_ip_list = [
            self.ip_jsonip,
            self.ip_ipip,
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


class DDNS():
    """ 更新DNS """

    def __init__(self, task) -> None:
        LOGGER.debug('DDNS start: ' + str(task))
        self.res = "init"
        self.url = task
        self.DNSData = {}
        self.getDNS()

    def run(self):
        """ DO IT! """

        def update():
            """ 更新函数 """
            response = requestUpdateDNS(RecordId, RR, Type)
            if response:
                response = json.loads(response)
                if response['RecordId'] == str(RecordId):
                    self.res = 'IP change: {0}.{1} {2}->{3}'.format(
                        RR, self.url["urlName"], oldValue, self.value)
                else:
                    LOGGER.error('Update DNS failed - ' +
                                 self.url["urlName"] + str(response))

        def requestUpdateDNS(RecordId, RR, Type):
            """ 更新阿里云DNS记录 """
            request.set_RecordId(RecordId)
            request.set_RR(RR)
            request.set_Type(Type)
            request.set_Value(self.value)
            try:
                response = self.client.do_action_with_exception(request)
            except Exception as e:
                LOGGER.error(e)
                return False
            return response

        # --- here ---
        change = self.checkChange()
        if change:
            self.setClient()
            request = UpdateDomainRecordRequest()
            request.set_accept_format('json')

            for data in self.DNSData:
                RecordId = data["RecordId"]
                RR = data['RR']
                Type = data['Type']
                oldValue = data['Value']
                if self.value != oldValue:
                    update()
        else:
            self.res = "not changed."
            return
        self.getDNS()
        LOGGER.debug(self.url["urlName"] + ' Update DNS done!')

    def setClient(self):
        """ 设置登录信息 """
        self.client = AcsClient(self.url["accessKeyId"],
                                self.url["accessSecret"],
                                config.region_id_list)

    def getIP(self) -> str:
        """ 获取公网IP """
        for func in PublicIP().public_ip_list:
            func = func()
            if func[0] == 200:
                LOGGER.debug('get public IP: ' + func[1])
                return func[1]
        LOGGER.error('Fail to get public IP')
        return False

    def checkChange(self):
        """ 查看DNS是否更改 """
        change = False
        self.value = self.getIP()
        if self.value:
            for data in self.DNSData:
                if data['Value'] == self.value:
                    LOGGER.debug(
                        'ip not changed: ' + data['RR'] + '.' + self.url["urlName"] + ' ' + data['Value'])
                else:
                    change = True
        return change

    def getDNS(self):
        """ 获取NDS信息 """
        self.setClient()

        response = self.requestGetDNS()
        if response is False:
            return

        response = json.loads(response)
        self.PageSize = response['PageSize']
        self.DNSData = response['DomainRecords']['Record']

        for data in self.DNSData:

            if data['Type'] in self.url["bypassType"] and \
                    data['RR'] not in self.url["IncludeRR"]:
                self.DNSData.remove(data)
                continue

            if data['RR'] in self.url["bypassRR"]:
                self.DNSData.remove(data)
                continue

            LOGGER.debug(
                'Get aliyun DNS: ' + data['RR'] + '.' + self.url["urlName"] + ' ' + data['Value'])

    def requestGetDNS(self):
        """ 获取阿里云DNS记录 """
        request = DescribeDomainRecordsRequest()
        request.set_accept_format('json')
        request.set_DomainName(self.url["urlName"])
        try:
            response = self.client.do_action_with_exception(request)
        except Exception as e:
            LOGGER.error(e)
            return False
        return response


def Start():
    """ START! """
    tasks = loadParams()
    ddns = DDNS(tasks)
    ddns.run()

    if config.echoMode:
        print(ddns.res)
    else:
        LOGGER.info(ddns.res)


if __name__ == '__main__':
    Start()
