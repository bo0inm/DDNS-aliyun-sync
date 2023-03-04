# https://next.api.aliyun.com/api/Alidns/2015-01-09/DescribeDomainRecords?params={}&lang=PYTHON&sdkStyle=dara
# https://next.api.aliyun.com/api/Alidns/2015-01-09/UpdateDomainRecord?params={}&lang=PYTHON&sdkStyle=dara

import json
import logging

import requests
from alibabacloud_alidns20150109 import models as alidns_20150109_models
from alibabacloud_alidns20150109.client import Client as Alidns20150109Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient

import PRIVATE

# --- Log Setting ---


def createLog() -> logging.Logger:
    """log文件设置"""
    # datefmt='%Y-%m-%d %H:%M:%S'
    logger = logging.Logger(__name__)
    logger.setLevel(PRIVATE.LogLevel)

    logFile = logging.FileHandler(PRIVATE.LOGPATH)
    format = logging.Formatter(
        "%(asctime)s - %(filename)s: %(lineno)d - %(levelname)s: %(message)s"
    )
    logFile.setFormatter(format)
    logger.addHandler(logFile)
    return logger


# --- Get Public IP ---


class PublicIP:
    """---从第三方网址获取公网IP---"""

    def __init__(self) -> None:
        # ---公网IP获取函数列表---
        # IP从此列表依次获取，直至成功获取停止
        self.public_ip_list = [
            self.ip_jsonip,
            self.ip_ipip,
        ]

    @staticmethod
    def ip_jsonip() -> str:
        """https://jsonip.com"""
        try:
            r = requests.get("https://jsonip.com")
            if r.status_code == 200:
                r = json.loads(r.text)
                res = r["ip"]
                LOGGER.debug("1 - jonip.com:" + str(res))

            else:
                res = "failed"
                LOGGER.warning("jsonip.com requests failed: " + str(r.status_code))
        except Exception as e:
            res = "failed"
            LOGGER.warning("jsonip.com requests failed")
            LOGGER.debug(e)

        return res

    @staticmethod
    def ip_ipip() -> str:
        """http://myip.ipip.net"""
        from re import search

        try:
            r = requests.get("http://myip.ipip.net")
            if r.status_code == 200:
                r = r.text
                r = search(r"(\d{1,3}\.){3}\d{1,3}", r)
                res = r.group()
                LOGGER.debug("2 - ipip.com:" + str(res))

            else:
                res = "failed"
                LOGGER.warning("jsonip.com requests failed: " + str(r.status_code))
        except Exception as e:
            res = "failed"
            LOGGER.warning("jsonip.com requests failed")
            LOGGER.debug(e)

        return res


# --- Main Function ---


def setClient() -> Alidns20150109Client:
    """初始化Client"""
    config = open_api_models.Config(
        access_key_id=PRIVATE.accessKeyId,
        access_key_secret=PRIVATE.accessSecret,
        # endpoint='alidns.cn-hangzhou.aliyuncs.com',  // 选择阿里云服务器
    )
    return Alidns20150109Client(config=config)


def getRecord(
    client: Alidns20150109Client, runtime: util_models.RuntimeOptions
) -> alidns_20150109_models.DescribeDomainRecordsResponse:
    """
    获取解析记录
    """
    describe_domain_records_request = alidns_20150109_models.DescribeDomainRecordsRequest(
        # 这里设置查询过滤参数
        domain_name=PRIVATE.domainName,
        rrkey_word=PRIVATE.KeyName,
    )

    try:
        response = client.describe_domain_records_with_options(
            describe_domain_records_request, runtime
        )
        LOGGER.debug(f"{PRIVATE.domainName} : {PRIVATE.KeyName} - {response}")
        return response

    except Exception as error:
        log = f"{PRIVATE.domainName} : '{PRIVATE.KeyName}' - {error.message}"
        LOGGER.error(log)
        raise


def dataFilter(res: alidns_20150109_models.DescribeDomainRecordsResponse) -> tuple:
    # 从返回解析记录中提取IP、ID、TYPE
    data = res.body.domain_records.record

    if len(data) == 1:
        return (data[0].value, data[0].record_id, data[0].type)
    elif len(data) < 1:
        log = f"{PRIVATE.domainName} : '{PRIVATE.KeyName}' - No record"
        LOGGER.error(log)
        raise IndexError(log)
    else:
        log = f"{PRIVATE.domainName} : '{PRIVATE.KeyName}' - Record > 1 ???"
        LOGGER.error(log)
        raise IndexError(log)


def getLocal() -> str:
    """从第三方网站获取本地的公网IP"""
    for func in PublicIP().public_ip_list:
        func = func()
        if func != "failed":
            LOGGER.debug("get public IP: " + func[1])
            return func
    LOGGER.error("Fail to get public IP")
    raise ValueError("Fail to get public IP")


def changeRecord(
    client: Alidns20150109Client,
    recordID: str,
    recordType: str,
    localIP: str,
    runtime: util_models.RuntimeOptions,
) -> None:
    """修改阿里云解析为当下公网IP"""
    update_domain_record_request = alidns_20150109_models.UpdateDomainRecordRequest(
        # 这里设置更新值参数，以下四项为必填项
        record_id=recordID,
        rr=PRIVATE.KeyName,
        type=recordType,
        value=localIP,
    )
    try:
        client.update_domain_record_with_options(update_domain_record_request, runtime)
    except Exception as error:
        UtilClient.assert_as_string(error.message)
        log = f"{PRIVATE.domainName} : '{PRIVATE.KeyName}' - {error.message}"
        LOGGER.error(log)
        raise


def Start():
    # set client and runtime
    client = setClient()
    runtime = util_models.RuntimeOptions()

    # get domain record data
    recordRes = getRecord(client, runtime)
    recordIP, recordID, recordType = dataFilter(recordRes)

    # get local IP
    localIP = getLocal()

    # change IP
    if recordIP == localIP:
        log = f"{PRIVATE.domainName} : '{PRIVATE.KeyName}' - IP no change."
        LOGGER.info(log)
        print(log)
    else:
        changeRecord(client, recordID, recordType, localIP, runtime)
        log = f"{PRIVATE.domainName} : '{PRIVATE.KeyName}' - {recordIP} -> {localIP}"
        LOGGER.info(log)
        print(log)


if __name__ == "__main__":
    # load log
    LOGGER = createLog()

    Start()
