FROM python:3.8

RUN apt-get -y update \  
    && apt-get install -y chromium \
    && apt-get -y clean

RUN mkdir /dependencias

COPY requeriments.txt /dependencias

RUN pip3 install -r /dependencias/requeriments.txt

ENV SERVICIOS_SECRET_KEY=""
ENV DB_SERVICIOS_NAME=""
ENV DB_SERVICIOS_USER=""
ENV DB_SERVICIOS_PASSWORD="" 
ENV DB_SERVICIOS_HOST=""
ENV DB_SERVICIOS_PORT=3306
ENV CLIENTE_SERVICIOS_USR=""
ENV CLIENTE_SERVICIOS_PWD=""

RUN mkdir -p /code/backend-crawler
RUN mkdir -p /code/servicios_back_end
RUN mkdir /start

COPY ./run.sh /start
RUN chmod 751 /start/run.sh

WORKDIR /code

RUN useradd -s /bin/bash limitado

RUN chown -R limitado /code

RUN wget https://chromedriver.storage.googleapis.com/80.0.3987.106/chromedriver_linux64.zip
RUN unzip chromedriver_linux64.zip
RUN rm chromedriver_linux64.zip


CMD /start/run.sh