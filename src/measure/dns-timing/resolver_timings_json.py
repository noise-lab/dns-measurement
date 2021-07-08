import sys
import os
import uuid
import logging.config
import collections
import subprocess
import logging
import json
log = logging.getLogger('postgres')
all_dns_info = []
k=0
for k in range(100):
	cmd = ["./dns-timing", "doh", "recursors", "domains"]
#	output = subprocess.check_output(cmd, stderr = subprocess.STDOUT)
#	output = output.decode('unicode_escape')
#	print(output)
	try:	
		output = subprocess.check_output(cmd, stderr = subprocess.STDOUT)
		output = output.decode('unicode_escape')
#		raise subprocess.CalledProcessError('test')
		print(output)
		lines = output.splitlines()
		print(lines)
		print(len(lines))
		for line in lines:
			print(line)
			status, resolver,  domain, response_time, size_or_error, datetime = line.split(',')
			print(status, resolver, domain, response_time, size_or_error, datetime)
			if status == "ok":
				response_size = int(size_or_error)
				error = None
				all_dns_info.append({'status': status, 'resolver': resolver, 'domain': domain, 'response_time': response_time,'size_or_error': response_size, 'datetime': datetime})
				print(status, resolver,  domain, response_time, response_size, datetime)
			else:
				response_size = None
				error = None
				response_time = None
				print(status, resolver,  domain, response_time, error, datetime)
				all_dns_info.append({'status': status, 'resolver': resolver, 'domain': domain, 'response_time': response_time,'size_or_error': error, 'datetime': datetime})
	except subprocess.CalledProcessError as e:
		print(e.stdout)
		print(e.stderr)
	except Exception as e:
	#	if type(e) == subprocess.CalledProcessError
	#		print(e.stdout)
	#		print(e.stderr)
		err = 'Error parsing DNS output for website {0}: {1}'
	k = k+1
print(all_dns_info)
with open("data_100.json", "a") as outfile:
        json.dump(all_dns_info, outfile)
