## Structure

* data - Ancillary files for performing measurements, such as database 
credential files and lists of websites 

* src/docker - All source code for creating a Docker image that performs page
  loads 

* src/measure - All source code for instrumenting the Docker image to perform
  page loads for various websites, recursive resolvers, and DNS protocols. Also
  contains source code for measuring DNS response times, which is done outside
  of the Docker image.

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

## Images

A pre-compiled Docker image that can be used to collect HARs is available
[here](https://www.dropbox.com/s/ibnl20duge85fy3/har-firefox-67.0-stable-image.tar.gz?dl=0).
Simply run `docker load < har-firefox-67.0-stable.image.tar.gz` to load the
image into Docker.

If you wish to modify our code and compile your own Docker image, make sure you change the image name referenced in src/measure/wrapper.py. The function `measure_and_collect_har()` in particular needs the correct image name.
