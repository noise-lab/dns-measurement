FROM debian:stable-slim

ENV DEBIAN_FRONTEND noninteractive
ENV DEBCONF_NONINTERACTIVE_SEEN true

RUN apt-get update && \
	apt-get upgrade -y && \
	apt-get install -y git && \
	apt-get install sudo -y
RUN git clone https://github.com/ranyasharma/dns-measurement-suite
WORKDIR /dns-measurement-suite
RUN git checkout resolver-research 

ENTRYPOINT ["sudo", "nohup", "python3", "src/measure/dns-timing/resolver_ping.py", ">", "data_30.txt"]
