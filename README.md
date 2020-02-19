## Dependencies
docker (sudo curl -sSL https://get.docker.com/ | sh)

python3, python3-pip

postgresql, postgresql-client

dnsutils

net-tools (for ifconfig)

for the dns-timing tool: libcurl4-openssl-dev, libssl-dev, libev4, libev-dev, libevent-2.1.6, libevent-core-2.1.6, libevent-openssl-2.1.6, libevent-dev libuv1
- You will also need to install the packages in the debs/ directory. Use sudo dpkg -i.


for jq: autoconf automake build-essential libtool python3-dev


## Installation
clone this repo

add your postgres credentials file to data/

run "make" in the dns-timing/ directory

install pip packages (pip3 install -r src/measure/requirements.txt)


## Running a measurement
configure src/measure/measure.sh to your liking

run src/measure/measure.sh
