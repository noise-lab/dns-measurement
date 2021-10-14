import sys
import os
import uuid
import logging.config
import collections
import subprocess
import json
from ping3 import ping
import time

all_dns_info = []
k = 0
localtime = time.strftime("%Y%m%d-%H%M%S")
print(localtime)
loop = 50
a = "data_"+str(loop)+"_"+localtime+".json"
print(a)

for k in range(loop):
        cmd = ["./dns-timing", "doh", "recursors", "domains"]
        try:
                output = subprocess.check_output(cmd, stderr = subprocess.STDOUT)
                output = output.decode('unicode_escape')
                lines = output.splitlines()
                for line in lines:
                        status, resolver,  domain, r_time, size_or_error, datetime = line.split(',')
                        if status == "ok":
                                response_size = int(size_or_error)
                                error = None
                                temp = resolver.replace("https://", "")
                                ping_name = temp.replace("/dns-query", "")
                                try:
                                        d = ping(ping_name, unit='ms')
                #                       print(d)
                                        all_dns_info.append({'status': status, 'resolver': resolver, 'domain': domain, 'rtime': r_time,'size_or_error': response_size,'ping_time': d, 'datetime': datetime})
                                except Exception as e:
                                        print('ping error:', e)
                                        d = None
                #                       print(d)
                                        all_dns_info.append({'status': status, 'resolver': resolver, 'domain': domain, 'rtime': r_time,'size_or_error': response_size,'ping_time': d, 'datetime': datetime})            
                        else:
                                response_size = None
                                error = None
                                r_time = None
                                d = None
                                all_dns_info.append({'status': status, 'resolver': resolver, 'domain': domain, 'rtime': r_time,'size_or_error': error,'ping_time': d, 'datetime': datetime})
        except subprocess.CalledProcessError as e:
                print(e.stdout)
                print(e.stderr)
        except Exception as e:
                err = 'Error parsing DNS output for website {0}: {1}'
                print(e)
        k = k+1
print(all_dns_info)
with open(a, "w") as outfile:
        json.dump(all_dns_info, outfile)
