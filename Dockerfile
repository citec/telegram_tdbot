FROM python:2.7
MAINTAINER Jaime Sánchez <jaime@grupocitec.com>

RUN apt-get update
RUN apt-get install -y git
RUN pip install py==1.4.29
RUN pip install pytest==2.7.2
RUN pip install requests==2.7.0
RUN pip install six==1.9.0
RUN pip install wheel==0.24.0
RUN pip install BeautifulSoup
RUN pip install python-decouple
WORKDIR /tmp
RUN git clone https://github.com/eternnoir/pyTelegramBotAPI.git
WORKDIR /tmp/pyTelegramBotAPI
RUN /usr/local/bin/python setup.py install
RUN pip install ipdb
# Timezone
RUN mkdir /tz && mv /etc/timezone /tz/ && mv /etc/localtime /tz/ && ln -s /tz/timezone /etc/ && ln -s /tz/localtime /etc/
RUN echo "America/Sao_Paulo" > /etc/timezone && dpkg-reconfigure -f noninteractive tzdata && cp /etc/localtime /tz/
VOLUME /tz
