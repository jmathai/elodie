FROM python:3.9-slim

ARG EXIF_TOOL_VER="13.27"

RUN apt-get update -y
RUN apt-get install -y --no-install-recommends ca-certificates libimage-exiftool-perl wget make
RUN rm -rf /var/lib/apt/lists/*

RUN apt-get update -qq && \
    apt-get install -y locales -qq && \
    locale-gen en_US.UTF-8 en_us && \
    dpkg-reconfigure locales && \
    locale-gen C.UTF-8 && \
    /usr/sbin/update-locale LANG=C.UTF-8

ENV LANG C.UTF-8
ENV LANGUAGE C.UTF-8
ENV LC_ALL C.UTF-8

RUN cd /tmp && \
    wget https://exiftool.org/Image-ExifTool-${EXIF_TOOL_VER}.tar.gz && \
    gzip -dc /tmp/Image-ExifTool-${EXIF_TOOL_VER}.tar.gz  | tar -xf - && \
    cd Image-ExifTool-${EXIF_TOOL_VER} && perl Makefile.PL && \
    make install && \
    cd ../ && rm -r Image-ExifTool-${EXIF_TOOL_VER} && \
    rm -r Image-ExifTool-${EXIF_TOOL_VER}.tar.gz

COPY requirements.txt /opt/elodie/requirements.txt
COPY docs/requirements.txt /opt/elodie/docs/requirements.txt
COPY elodie/tests/requirements.txt /opt/elodie/elodie/tests/requirements.txt
WORKDIR /opt/elodie
RUN pip install -r docs/requirements.txt && \
    pip install -r elodie/tests/requirements.txt && \
    rm -rf /root/.cache/pip

COPY . /opt/elodie

ENTRYPOINT [ "/opt/elodie/elodie.py" ]
