FROM ubuntu:20.04

RUN apt update && apt install -y python3 python3-pip

RUN apt update && apt install -y libcurl4-openssl-dev libssl-dev curl

COPY . /cryptdomainmgr

CMD cat /proc/1/cgroup && cd /cryptdomainmgr && pip3 install -r requirements.txt && python3 -m cryptdomainmgr

