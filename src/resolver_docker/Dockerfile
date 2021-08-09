FROM debian:stable-slim

ENV DEBIAN_FRONTEND noninteractive
ENV DEBCONF_NONINTERACTIVE_SEEN true

RUN apt-get -y update && \
    apt-get -y install --no-install-recommends \
        sudo python3-pip procps git

RUN git clone https://github.com/ranyasharma/dns-measurement-suite
WORKDIR /dns-measurement-suite
RUN git checkout resolver-research 

ENTRYPOINT ["sudo", "nohup", "python3", "src/measure/dns-timing/resolver_ping.py", ">", "data_30.txt"]
