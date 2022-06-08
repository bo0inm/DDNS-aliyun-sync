""" 设置 Setting """
from os import path


# log，非前台运行才使用log文件
logPath = path.join(path.dirname(__file__), 'DDNS.log')
logLevel = 20
# 0 NOTSET
# 10 DEBUG
# 20 INFO
# 30 WARNING
# 40 ERROR
# 50 CRITICAL

# 前台运行
echoMode = False

# 阿里云服务器地址
region_id_list = 'cn-qingdao'
# 'cn-qingdao'
# 'cn-beijing'
# 'cn-zhangjiakou'
# 'cn-shanghai'
# 'cn-shenzhen'
# 'cn-chengdu'
# 'cn-hangzhou'
# 'cn-huhehaote'
# 'cn-wulanchabu'

# 域名配置文件在 PRIVATE 文件中
