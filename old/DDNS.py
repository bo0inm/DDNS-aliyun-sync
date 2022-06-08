"""
定时更新阿里云的DNS解析列表
python3 ./DDNS.py start  运行
python3 ./DDNS.py stop  停止
pip install aliyun-python-sdk-core
pip install aliyun-python-sdk-alidns==2.6.32
"""
# 不知道阿里云的dns解析记录超过一页运行起来有什么bug
# TODO 定时任务

import os
import sys
import atexit
import signal
from aliyunsdkcore.client import AcsClient
# from aliyunsdkcore.acs_exception.exceptions import ClientException
# from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkalidns.request.v20150109.DescribeDomainRecordsRequest import DescribeDomainRecordsRequest
from aliyunsdkalidns.request.v20150109.UpdateDomainRecordRequest import UpdateDomainRecordRequest
import json
import time
# import sched
from threading import Thread

import config
import util
from util import TASKS as ts


class DDNS():
    """ 阿里云DNS API """

    def __init__(self, task) -> None:
        util.LOGGER.debug('DDNS start: ' + task)
        self.url = task
        self.publicIP = util.PublicIP()
        self.DNSData = {}
        self.getDNS()

    def run(self):
        """ DO IT! """
        self.updateDNS()

    def setClient(self):
        """ 设置登录信息 """
        self.client = AcsClient(ts[self.url]["accessKeyId"],
                                ts[self.url]["accessSecret"],
                                config.region_id_list)

    def getIP(self) -> str:
        """ 获取公网IP """
        for func in self.publicIP.public_ip_list:
            func = func()
            if func[0] == 200:
                util.LOGGER.debug('get public IP: ' + func[1])
                return func[1]
        util.LOGGER.error('Fail to get public IP')
        return False

    def checkChange(self):
        """ 查看DNS是否更改 """
        change = False
        self.value = self.getIP()
        if self.value:
            for data in self.DNSData:
                if data['Value'] == self.value:
                    util.LOGGER.debug(
                        'ip not changed: ' + data['RR'] + '.' + self.url + ' ' + data['Value'])
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

            if data['Type'] in ts[self.url]["BypassType"] and \
                    data['RR'] not in ts[self.url]["IncludeRR"]:
                self.DNSData.remove(data)
                continue

            if data['RR'] in ts[self.url]["BypassRR"]:
                self.DNSData.remove(data)
                continue

            util.LOGGER.debug(
                'Get aliyun DNS: ' + data['RR'] + '.' + self.url + ' ' + data['Value'])

    def requestGetDNS(self):
        """ 获取阿里云DNS记录 """
        request = DescribeDomainRecordsRequest()
        request.set_accept_format('json')
        request.set_DomainName(self.url)
        try:
            response = self.client.do_action_with_exception(request)
        except Exception as e:
            util.LOGGER.error(e)
            return False
        return response

    def updateDNS(self):
        """ 更新DNS """
        def update():
            """ 更新函数 """
            response = requestUpdateDNS(RecordId, RR, Type)
            if response:
                response = json.loads(response)
                if response['RecordId'] == str(RecordId):
                    info = 'IP change: {0}.{1} {2}->{3}'.format(
                        RR, self.url, oldValue, self.value)
                    util.LOGGER.info(info)
                    if config.echoMode:
                        print(info)
                else:
                    util.LOGGER.error('Update DNS failed - ' +
                                      self.url + str(response))

        def requestUpdateDNS(RecordId, RR, Type):
            """ 更新阿里云DNS记录 """
            request.set_RecordId(RecordId)
            request.set_RR(RR)
            request.set_Type(Type)
            request.set_Value(self.value)
            try:
                response = self.client.do_action_with_exception(request)
            except Exception as e:
                util.LOGGER.error(e)
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
            return
        self.getDNS()
        util.LOGGER.debug(self.url + ' Update DNS done!')


class Clock():
    """ 计时触发器 """

    def run(self) -> None:
        """ run Clock! """
        for task in ts:
            if "accessKeyId" in ts[task] and \
                "accessSecret" in ts[task] and \
                    "UpdateTime" in ts[task]:
                self.runSchedDo(task)
            else:
                util.LOGGER.error(task + 'incomplete content')

    def runSchedDo(self, task):
        """ 为周期任务创建线程 """
        # updateTask = sched.scheduler(time.time, time.sleep)
        updateTask = False
        ddns = DDNS(task=task)
        thread = Thread(target=self.schedDo,
                        name=task,
                        args=(ddns, task, updateTask),
                        daemon=False)
        thread.start()
        util.LOGGER.debug('UpdateTask start: ' + task)

    def schedDo(self, ddns, task, updateTask=False):
        """ 周期任务 """
        sleepTime = int(60 * ts[task]["UpdateTime"])

        util.LOGGER.debug('schedDo run')

        while True:
            ddns.run()
            writeLog(loopTime=ts[task]["UpdateTime"])
            time.sleep(sleepTime)


past = time.strftime("%Y-%m-%d", time.localtime())


def writeLog(loopTime):
    """ 周期循环写入日志 """
    global past
    now = time.strftime("%Y-%m-%d", time.localtime())
    with open(config.logPath, mode='a') as f:
        if past == now:
            f.write(r'*')
        else:
            past = now
            f.write('\n{0}: *'.format(now))


# https://www.zhihu.com/question/394600542
def daemonize(pidfile, *, stdin='/dev/null',
              stdout='/dev/null',
              stderr='/dev/null'):
    """ 守护进程 """

    # if os.path.exists(pidfile):
    #     raise RuntimeError('Already running')

    # First fork (detaches from parent)
    try:
        if os.fork() > 0:
            raise SystemExit(0)   # Parent exit
    except OSError as e:
        raise RuntimeError('fork #1 failed.\n', e)

    os.chdir('/')
    os.umask(0)
    os.setsid()
    # Second fork (relinquish session leadership)
    try:
        if os.fork() > 0:
            raise SystemExit(0)
    except OSError as e:
        raise RuntimeError('fork #2 failed.\n', e)

    # Flush I/O buffers
    sys.stdout.flush()
    sys.stderr.flush()

    # Replace file descriptors for stdin, stdout, and stderr
    with open(stdin, 'rb', 0) as f:
        os.dup2(f.fileno(), sys.stdin.fileno())
    with open(stdout, 'ab', 0) as f:
        os.dup2(f.fileno(), sys.stdout.fileno())
    with open(stderr, 'ab', 0) as f:
        os.dup2(f.fileno(), sys.stderr.fileno())

    # Write the PID file
    with open(pidfile, 'w') as f:
        print(os.getpid(), file=f)

    # Arrange to have the PID file removed on exit/signal
    atexit.register(lambda: os.remove(pidfile))

    # Signal handler for termination (required)
    def sigterm_handler(signo, frame):
        raise SystemExit(1)

    signal.signal(signal.SIGTERM, sigterm_handler)


def Start():
    """ START! """

    PIDFILE = os.path.join(util.BASEPATH, 'DDNS.pid')

    # ----------
    if len(sys.argv) != 2:
        print('Usage: {} [start|stop]'.format(sys.argv[0]), file=sys.stderr)
        raise SystemExit(1)

    # start----------
    if sys.argv[1] == 'start':
        print('started with pid {}'.format(os.getpid()))

        if config.echoMode:
            def sigterm_handler(signo, frame):
                sys.exit()

            util.LOGGER.info('DDNS service running! ' + str(os.getpid()))

            with open(PIDFILE, mode='w') as f:
                print(os.getpid(), file=f)

            # Arrange to have the PID file removed on exit/signal
            atexit.register(lambda: os.remove(PIDFILE))

            signal.signal(signal.SIGINT, sigterm_handler)
            Clock().run()

        else:
            try:
                daemonize(PIDFILE,
                          stdout=config.logPath,
                          stderr=config.logPath)
            except RuntimeError as e:
                print(e, file=sys.stderr)
                raise SystemExit(1)

            sys.stdout.write(
                'Daemon started with pid {}\n'.format(os.getpid()))
            Clock().run()

    # start once----------
    if sys.argv[1] == 'once':
        util.LOGGER.info("once")

    # stop----------
    elif sys.argv[1] == 'stop':
        if os.path.exists(PIDFILE):
            with open(PIDFILE) as f:
                os.kill(int(f.read()), signal.SIGTERM)
                print("stop")
        else:
            print('Not running', file=sys.stderr)
            raise SystemExit(1)

    # ----------
    else:
        print('Unknown command {!r}'.format(sys.argv[1]), file=sys.stderr)
        raise SystemExit(1)


if __name__ == '__main__':
    Start()
