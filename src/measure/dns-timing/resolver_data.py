import subprocess
import json
from ping3 import ping
import time

all_dns_info = []
k = 0
loop = 50
localtime = time.strftime("%Y%m%d-%H%M%S")
a = "data_" + str(loop) + "_" + localtime + ".json"
print(a)

for k in range(loop):
    cmd = ["./dns-timing", "doh", "recursors", "domains"]
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        output = output.decode('unicode_escape')
        lines = output.splitlines()
        for line in lines:
            status, resolver, domain, \
                r_time, size_or_error, datetime = line.split(',', 6)
            if status == "ok":
                response_size = int(size_or_error)
                error = None
                temp = resolver.replace("https://", "")
                ping_name = temp.replace("/dns-query", "")
                try:
                    d = ping(ping_name, unit='ms')
                    all_dns_info.append({
                        'status': status,
                        'resolver': resolver,
                        'domain': domain,
                        'rtime': r_time,
                        'size_or_error': response_size,
                        'ping_time': d,
                        'datetime': datetime})
                except Exception as e:
                    print('ping error:', e)
                    d = None
                    all_dns_info.append({
                        'status': status,
                        'resolver': resolver,
                        'domain': domain,
                        'rtime': r_time,
                        'size_or_error': response_size,
                        'ping_time': d,
                        'datetime': datetime})
            else:
                print(line)
                response_size = None
                error = None
                r_time = None
                d = None
                all_dns_info.append({
                    'status': status,
                    'resolver': resolver,
                    'domain': domain,
                    'rtime': r_time,
                    'size_or_error': error,
                    'ping_time': d,
                    'datetime': datetime})
    except subprocess.CalledProcessError as e:
        print("CalledProcessError: {0} {1}".format(e.stdout, e.stderr))
    except Exception as e:
        print("Exception: {0}".format(e))
    k = k + 1

with open(a, "w") as outfile:
    json.dump(all_dns_info, outfile)
