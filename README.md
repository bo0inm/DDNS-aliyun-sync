# DNS SYNC

## *自用的更新阿里云dns解析脚本*

从外部获取公网ip地址，然后更新阿里云dns解析记录

自家服务器nas用，有公网IP但是**是动态的公网IP**，可以接受IP变更后，**非第一时间变更DNS解析指向**，则可以试试这个脚本。
* 自建ddns服务器还是需要一个固定ip的服务器，而且没必要
* 也不想用别人的ddns服务器

## 依赖

* python >= 3.5
* `pip install aliyun-python-sdk-core aliyun-python-sdk-alidns==2.6.32`

## USE

1. 填入`template.json`内容（记得删掉注释
2. 把`template.json`更名为`PRIVATE`（不带后缀名
3. `python3 ./DDNS.py`

`config.py` 有一些的设置项

### 自定义外网ip获取源
默认从 [jsonip.com](https://jsonip.com)、[myip.ipip.net](http://myip.ipip.net) 中获取外网ip，会依次从上述网站获取外网IP，获取成功停止。
要更改获取源需要：
1. 在`DDNS.py`中`PublicIP`类中添加获取外网ip的类函数，保证返回字符串类型的ip值（如"123.123.123.123"
2. `PublicIP`类的`public_ip_list`是获取源函数，在其中添加更改你的类方法。

## 定时任务

脚本只运行一次，liunx可以使用crontab制作定时任务，如：
`0 */2 * * * python3 ~/CODE/asare/DDNS/DDNS.py` 每两个小时更新一次