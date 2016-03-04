FROM debian:jessie

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends ca-certificates libimage-exiftool-perl python2.7 python-pip python-pyexiv2 && \
    pip install --upgrade pip setuptools && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# RUN apk add --update boost-python ca-certificates exiftool exiv2 make python py-pip && \
#     pip install --upgrade pip setuptools && \
#     apk add --virtual build-dependencies build-base boost-dev exiv2-dev python-dev scons wget && \
#     wget -O /tmp/pyexiv2-0.3.2.tar.bz2 https://launchpad.net/pyexiv2/0.3.x/0.3.2/+download/pyexiv2-0.3.2.tar.bz2 && \
#     echo "9c0377ca4cf7d5ceeee994af0b5536ae  /tmp/pyexiv2-0.3.2.tar.bz2" | md5sum -c - && \
#     tar -C /tmp -xjf /tmp/pyexiv2-0.3.2.tar.bz2 && \
#     rm -f /tmp/pyexiv2-0.3.2.tar.bz2 && \
#     cd /tmp/pyexiv2-0.3.2 && \
#     scons && \
#     scons install && \
#     cd / && \
#     rm -rf /tmp/*

COPY requirements.txt /opt/elodie/requirements.txt
COPY docs/requirements.txt /opt/elodie/docs/requirements.txt
COPY elodie/tests/requirements.txt /opt/elodie/elodie/tests/requirements.txt
WORKDIR /opt/elodie
RUN pip install -r docs/requirements.txt && \
    pip install -r elodie/tests/requirements.txt && \
    rm -rf /root/.cache/pip

COPY . /opt/elodie

CMD ["/bin/sh"]
