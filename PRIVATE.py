from os import path, environ

# 必须配置下面四项

# 域名
domainName = "domain.name"

# 需要匹配的记录值名
KeyName = "@"

# 阿里云的 AccessKey ID
accessKeyId = "AccessKey ID"

# 阿里云的AccessKey Secret
accessSecret = "AccessKey Secret"


# docker ENV 覆盖文本配置
try:
    KeyName = environ['K']
except KeyError:
    KeyName = "@"

try:
    envs=(environ['DN'], environ['AKEY'], environ['ASECRET'])
    (domainName, accessKeyId, accessSecret) = envs
except KeyError:
    pass

# --- other setting---

# log级别
LogLevel = 20
# 0 NOTSET
# 10 DEBUG
# 20 INFO
# 30 WARNING
# 40 ERROR
# 50 CRITICAL

# log文件位置
LOGPATH = path.join(path.dirname(__file__), 'DDNS.log')

BASEPATH = path.dirname(__file__)
