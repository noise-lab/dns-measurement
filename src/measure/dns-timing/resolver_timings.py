import sys
import os
import uuid
import logging.config
import collections
import subprocess
import logging
log = logging.getLogger('postgres')
# Create csv 
textfile=open("resolver_data.csv","a")
textfile.write("status,resolver,domain,time,size\n")
# Repeat measurements by the number defined in the loop and input data into csv, appending each time 
k=0
for k in range(30):
	cmd = ["./dns-timing", "doh", "recursors", "domains"]
	output = subprocess.check_output(cmd, stderr = subprocess.STDOUT)
	output = output.decode('unicode_escape')
	print(output)
	lines = output.splitlines()
#	print(lines)
	for element in lines:
		textfile.write(element + "\n")
	k = k+1
textfile.close()
# Initialize the dict with all the data for each resolver
# I was experimenting with a different way of creting the output file, following Austin's code. The above method is more efficient - disregard this.   
##all_dns_info = {}
##try:
##	lines = output.splitlines()
##	i=-1
##	for line in lines:
##		i=i+1
##		str = line.split(',')
##		if (len(str) == 5):
##			status, resolver,  domain, response_time, size_or_error = line.split(',')
##			if status == "ok":
##				response_size = int(size_or_error)
##				error = None
##			else:
##				response_size = None
##				error = int(size_or_error)
##			all_dns_info[i] = {'status': "", 'resolver': "", 'domain': "", 'response_time': 0., 'response_size': 0, 'error': 0}
##			all_dns_info[i] = {'status': status, 'resolver': resolver, 'domain': domain, 'response_time': float(response_time),'response_size': response_size,'error': error}
##
##		else:
##			all_dns_info[i] = {'status': "Error", 'resolver': "", 'domain': "", 'response_time': 0., 'response_size': 0, 'error': 0}

##except Exception as e:
##	err = 'Error parsing DNS output for website {0}: {1}'

