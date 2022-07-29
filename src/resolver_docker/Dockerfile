FROM debian:buster-slim

ENV DEBIAN_FRONTEND noninteractive
ENV DEBCONF_NONINTERACTIVE_SEEN true

RUN apt-get -y update && \
    apt-get -y install --no-install-recommends \
        sudo python3-pip procps git libcurl4-openssl-dev libssl-dev libev4 libev-dev libevent-2.1.6 \
        libevent-core-2.1.6 libevent-openssl-2.1.6 libevent-dev libuv1 dns-root-data build-essential uuid

RUN pip3 install ping3

RUN git clone https://github.com/ranyasharma/dns-measurement-suite
WORKDIR /dns-measurement-suite/src/measure/dns-timing
RUN git checkout resolver-research
RUN dpkg -i debs/libgetdns10_1.5.1-1.1_amd64.deb
RUN dpkg -i debs/libgetdns-dev_1.5.1-1.1_amd64.deb
RUN make
ENTRYPOINT ["sudo", "nohup", "python3", "resolver_data.py", ">", "data_100.txt", "&"]
