FROM ubuntu:20.04

RUN apt update && apt install -y python3 python3-pip

RUN apt update && apt install -y libcurl4-openssl-dev libssl-dev curl

COPY . /cryptdomainmgr

WORKDIR /cryptdomainmgr

RUN cd /cryptdomainmgr && pip3 install -r requirements.txt

#VOLUME /etc/cryptdomainmgr

RUN chmod +x /cryptdomainmgr/entrypoint.sh

ENTRYPOINT ["/bin/bash", "/cryptdomainmgr/entrypoint.sh"]


