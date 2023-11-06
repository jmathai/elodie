FROM debian:bullseye
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -y -qq 
# removed python-pyexiv2 from this
RUN apt-get install -y --no-install-recommends ca-certificates libimage-exiftool-perl python2.7 python3 python3-pip wget make
RUN ln -s /usr/bin/pip3 /usr/bin/python-pip
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1


#python-pyexiv2 won't be installed by apt-get. has to be mnaully compiled. with these steps.
# RUN apt-get install -y python-dev libexiv2-dev cmake git 
#RUN mkdir /repo && cd /repo && git clone https://github.com/Leo91231/pyexiv2.git
#RUN cd /repo/pyexiv2 && mkdir build && cd build && cmake .. && make && make install && pip install pyexiv2

#RUN mkdir /repos && cd /repos && git clone https://github.com/OlegIlyenko/py3exiv2.git && cd py3exiv2 && python setup.py install 
RUN pip install --upgrade pip setuptools && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

RUN apt-get update -qq && \
    apt-get install -y locales -qq && \
    locale-gen en_US.UTF-8 en_us && \
    dpkg-reconfigure locales && \
    locale-gen C.UTF-8 && \
    /usr/sbin/update-locale LANG=C.UTF-8

ENV LANG C.UTF-8
ENV LANGUAGE C.UTF-8
ENV LC_ALL C.UTF-8
#follwing https://exiftool.org/install.html#Unix
RUN wget https://exiftool.org/Image-ExifTool-12.69.tar.gz && \
    gzip -dc Image-ExifTool-12.69.tar.gz  | tar -xf - && \
    cd Image-ExifTool-12.69 && perl Makefile.PL && \
    make install 

COPY requirements.txt /opt/elodie/requirements.txt
COPY docs/requirements.txt /opt/elodie/docs/requirements.txt
COPY elodie/tests/requirements.txt /opt/elodie/elodie/tests/requirements.txt
WORKDIR /opt/elodie
RUN pip install -r docs/requirements.txt && \
    pip install -r elodie/tests/requirements.txt && \
    rm -rf /root/.cache/pip

COPY . /opt/elodie

CMD ["/bin/bash"]
