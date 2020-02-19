FROM debian:stable-slim

ENV DEBIAN_FRONTEND noninteractive
ENV DEBCONF_NONINTERACTIVE_SEEN true

RUN apt-get -y update && \
    apt-get -y install --no-install-recommends \
        sudo python3-pip vim wget bzip2 libgtk-3-0 libdbus-glib-1-2 \
        libxt6 procps dnsutils libssl-dev openssl libyaml-dev git libtool m4 autoconf build-essential automake libunbound-dev

RUN echo "deb http://deb.debian.org/debian stretch-backports main" >> /etc/apt/sources.list && \
    cat /etc/apt/sources.list
RUN apt-get -y update && \
    apt-get -y -t stretch-backports install libidn2-dev

RUN wget -q https://ftp.mozilla.org/pub/firefox/releases/67.0.4/linux-x86_64/en-US/firefox-67.0.4.tar.bz2 -O /tmp/firefox.tar.bz2  && \
    tar -xf /tmp/firefox.tar.bz2 -C /opt/ && \
    rm /tmp/firefox.tar.bz2

RUN wget -q https://github.com/mozilla/geckodriver/releases/download/v0.24.0/geckodriver-v0.24.0-linux64.tar.gz -O /tmp/geckodriver.tar.gz && \
    tar -xf /tmp/geckodriver.tar.gz -C /usr/local/bin/ && \
    rm /tmp/geckodriver.tar.gz

RUN git clone https://github.com/getdnsapi/getdns.git && \
    cd getdns && \
    git checkout master && \
    git submodule update --init && \
    libtoolize -ci && \
    autoreconf -fi && \
    mkdir build && \
    cd build && \
    ../configure --prefix=/usr/local/bin --without-libidn --without-libidn2 --with-stubby && \
    make && \
    sudo make install

ADD requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt

RUN mkdir -p /usr/lib/mozilla/native-messaging-hosts/
ADD har_catcher.json /usr/lib/mozilla/native-messaging-hosts/

RUN useradd -ms /bin/bash seluser
RUN adduser seluser sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

ADD harexporttrigger-0.6.2-fx.xpi \
    run.py \
    har_catcher.py \
    stubby-cf.yml \
    stubby-quad9.yml \
    stubby-google.yml \
    resolv.conf \
    /home/seluser/measure/

RUN chown seluser:seluser -R /home/seluser/measure

USER seluser
WORKDIR /home/seluser/measure

ENTRYPOINT ["sudo", "python3", "/home/seluser/measure/run.py"]
