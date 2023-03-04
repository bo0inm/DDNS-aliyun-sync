# syntax=docker/dockerfile:1

FROM python:3.10-alpine
COPY . /app
WORKDIR /app
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple alibabacloud_alidns20150109==3.0.1 
CMD python3 DDNS.py