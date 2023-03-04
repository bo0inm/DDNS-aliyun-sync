# DNS SYNC

## *自用的更新阿里云ddns脚本*

**从第三方网站获取本地公网ip地址，然后更新阿里云dns解析记录**

#### 为什么我写了这个脚本？
* 自家服务器nas用，**有公网IP**但是是动态的公网IP，
* 可以接受IP变更后，**非第一时间变更DNS解析指向**（阿里云dns解析数据更改后，阿里云会根据TTL时间周期将更新记录上传DNS服务器，这就产生了一个空档期）
* 免费ddns服务商不太稳定，有些情况还需要硬件支持
* 自建ddns服务器还是需要一个固定ip的服务器，而且没必要
* 我也不想用别人的ddns服务器

## 依赖

* python >= 3.5
* `alibabacloud_alidns20150109` == 3.0.1

## USE

### Local
1. 填入`PRIVATE.py`配置信息
2. `pip install alibabacloud_alidns20150109==3.0.1`
3. `python3 ./DDNS.py`

### docker
<https://hub.docker.com/r/bo0inm/ddns-aliyun-sync>

key|details
-----|-----
`-e DN=` | 域名 domainName
`-e K=@` | 可选，需要匹配的`记录值`名
`-e AKEY=` | 阿里云的 `AccessKey ID`
`-e ASECRET=` | 阿里云的 `accessSecret`

### 自定义外网ip获取源
默认从 [jsonip.com](https://jsonip.com)、[myip.ipip.net](http://myip.ipip.net) 中获取外网ip，会依次从上述网站获取外网IP，获取成功停止。
要更改获取源需要：
1. 在`DDNS.py`中[`PublicIP`](https://github.com/bo0inm/DNS-sync/blob/e0f4e75ac0d3c35fb9d74849e2509afe0048a6ac/DDNS.py#L51)类中添加获取外网ip的类函数，保证返回字符串类型的ip值（如"123.123.123.123"）。
2. 在`PublicIP`类的[`public_ip_list`](https://github.com/bo0inm/DNS-sync/blob/e0f4e75ac0d3c35fb9d74849e2509afe0048a6ac/DDNS.py#L57)添加刚写的函数。

## 定时任务

脚本(包括docker版本)只运行一次，liunx可以使用crontab制作定时任务，如：
`0 */2 * * * python3 path/DDNS.py` 每两个小时更新一次