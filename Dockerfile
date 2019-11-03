FROM python:3.6

RUN set -xe \
    && sed  -i "s/deb.debian.org/mirrors.aliyun.com/g" /etc/apt/sources.list  \
    && sed  -i "s/security.debian.org/mirrors.aliyun.com/g" /etc/apt/sources.list  \
    && apt-get update \
    && apt-get install -y libssl-dev

COPY demo.sol /demo.sol
COPY flag /flag

COPY src /app
COPY start.sh /start.sh
COPY solc-static-linux /usr/bin/solc
COPY requirements.txt /requirements.txt

RUN set -xe \ 
    && pip install -U pip \
    && pip install -r /requirements.txt -i https://mirrors.aliyun.com/pypi/simple \ 
    && chmod +x /usr/bin/solc \
    && chmod +x /start.sh

WORKDIR /app

EXPOSE 10000

CMD ["/start.sh"]