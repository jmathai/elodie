FROM gliderlabs/alpine

COPY requirements.txt /opt/elodie/requirements.txt
COPY docs/requirements.txt /opt/elodie/docs/requirements.txt
COPY elodie/tests/requirements.txt /opt/elodie/elodie/tests/requirements.txt
WORKDIR /opt/elodie

RUN apk add --update boost-python ca-certificates exiftool exiv2 make python py-pip && \
    apk add --virtual build-dependencies build-base boost-dev exiv2-dev openssl python-dev scons wget && \
    pip install -r docs/requirements.txt && \
    pip install -r elodie/tests/requirements.txt && \
    wget -O /tmp/pyexiv2-0.3.2.tar.bz2 https://launchpad.net/pyexiv2/0.3.x/0.3.2/+download/pyexiv2-0.3.2.tar.bz2 && \
    echo "9c0377ca4cf7d5ceeee994af0b5536ae  /tmp/pyexiv2-0.3.2.tar.bz2" | md5sum -c - && \
    tar -C /tmp -xjf /tmp/pyexiv2-0.3.2.tar.bz2 && \
    rm -f /tmp/pyexiv2-0.3.2.tar.bz2 && \
    cd /tmp/pyexiv2-0.3.2 && \
    scons && \
    scons install && \
    cd / && \
    apk del build-dependencies && \
    rm -rf /root/.cache/pip /tmp/* /var/cache/apk/*

COPY . /opt/elodie

CMD ["/bin/sh"]
