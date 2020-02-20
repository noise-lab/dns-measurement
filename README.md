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

To build the DNS response time measurement tool, you will first need to install
the packages in the dns-timing/debs directory with `dpkg -i`.
You will also need to install the following dependencies:

* libcurl4-openssl-dev
* libssl-dev
* libev4, libev-dev
* libevent-2.1.6, libevent-core-2.1.6, libevent-openssl-2.1.6, libevent-dev
* libuv1

To instrument the Docker image to measure page loads, parse the resulting HARs,
and insert the HARs into a PostgreSQL database, you will need to install the
following dependencies:

* python3, python3-pip, python3-dev
* postgresql, postgresql-client
* dnsutils
* net-tools 
* autoconf
* automake
* build-essential
* libtool

## Installation

Once you've installed the dependencies listed above, you need to do a few more
things before you can start some measurements:

* Create a PostgreSQL database and user that has write access to the database

* Modify the data/postgres.ini file to contain your PostgreSQL credentials. For
  the har-info field, choose the name of the table that you want to store HARs
  for page load times. For the dns-info field, choose the name of the table that
  you want to store DNS response times.

* Run the following script to initialize the tables in your database that will
  store HARs and DNS response times:

  `python3 database.py ../../data/postgres.ini`

* Run `make` in src/dns-timing to create the DNS response time measurement tool.

* Install the pip packages listed in src/measure/requirements.txt with the
  following command:

  `pip3 install -r requirements.txt`

## Running a measurement

configure src/measure/measure.sh to your liking

run src/measure/measure.sh

## Images

A pre-compiled Docker image that can be used to collect HARs is available
[here](https://www.dropbox.com/s/ibnl20duge85fy3/har-firefox-67.0-stable-image.tar.gz?dl=0).
Simply run `docker load < har-firefox-67.0-stable.image.tar.gz` to load the
image into Docker.

If you wish to modify our code and compile your own Docker image, make sure you change the image name referenced in src/measure/wrapper.py. The function `measure_and_collect_har()` in particular needs the correct image name.
