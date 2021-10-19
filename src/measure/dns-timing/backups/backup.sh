#!/bin/bash

scp -i "~/Documents/ec2_keys/doh-resolver-measurements/doh-resolver-measurements.pem" admin@ec2-52-14-69-198.us-east-2.compute.amazonaws.com:~/git/forks/dns-measurement-suite/src/measure/dns-timing/data_50_\*.json ohio/

scp -i "~/Documents/ec2_keys/doh-resolver-measurements/doh-resolver-measurements-frankfurt.pem" admin@ec2-3-66-155-20.eu-central-1.compute.amazonaws.com:~/git/forks/dns-measurement-suite/src/measure/dns-timing/data_50_\*.json frankfurt/

scp -i "~/Documents/ec2_keys/doh-resolver-measurements/doh-resolver-measurements-seoul.pem" admin@ec2-52-78-192-185.ap-northeast-2.compute.amazonaws.com:~/git/forks/dns-measurement-suite/src/measure/dns-timing/data_50_\*.json seoul/
