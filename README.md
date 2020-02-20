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
  the har_table field, choose the name of the table that you want to store HARs
  for page load times. For the dns_table field, choose the name of the table that
  you want to store DNS response times.

* Run the following script to initialize the tables in your database that will
  store HARs and DNS response times:

  `python3 database.py ../../data/postgres.ini`

* Run `make` in src/dns-timing to create the DNS response time measurement tool.

* Install the pip packages listed in src/measure/requirements.txt with the
  following command:

  `pip3 install -r requirements.txt`

## Running a measurement

Assuming your credentials are in data/postgres.ini and you wish to measure the
websites listed in data/tranco_combined.txt, you can simply run `sudo ./measure.sh`
from the src/measure directory to start your measurements. We need `sudo` to 
measure the ping to recursive resolvers.

This script will perform page loads for each website in
data/tranco_combined.txt. These page loads will be performed with Cloudflare's 
resolver (1.1.1.1), Google's resolver (8.8.8.8), Quad9's resolver (9.9.9.9),
and your local resolver listed in /etc/resolv.conf.

For each "quad" resolver listed above, the page loads will be performed with 
traditional DNS ("Do53"), DoT, and DoH. For your local resolver, the page loads 
will only be performed with Do53.

## Images

A pre-compiled Docker image that can be used to collect HARs is available
[here](https://www.dropbox.com/s/ibnl20duge85fy3/har-firefox-67.0-stable-image.tar.gz?dl=0).
Simply run `docker load < har-firefox-67.0-stable.image.tar.gz` to load the
image into Docker. Run `sudo docker images` to confirm that the image loaded is
named "har:firefox-67.0-stable".

## Modifying our code

If you wish to perform measurements with different resolvers, then you need to
modify src/measure/wrapper.py. The "Resolvers" class at the top of the file
contains an enum for resolver names, IP addresses, and DoH URIs. We note that
"default" refers to your local resolver listed in /etc/resolv.conf; you do not
need to modify this entry. If you wish to add new resolvers, simply add new
entries to this class.

We note that if you do wish to add resolvers that support DoT, then you will
also need to add a new configuration file for Stubby that lists this resolver.
We use [Stubby](https://github.com/getdnsapi/stubby) to load web pages with DoT. 
See the example configuration files for Cloudflare, Google, and Quad9's
resolvers listed in src/docker.

Once you've created new Stubby configuration files, you will need to add them to
the Dockerfile and compile a new Docker image. See src/docker/Dockerfile for
examples of how we add the Stubby configuration files to a new Docker image.

If you modify our code and compile a new Docker image with a different name, 
make sure you change the image name referenced in src/measure/wrapper.py. The 
function `measure_and_collect_har()` in particular needs the correct image name.

