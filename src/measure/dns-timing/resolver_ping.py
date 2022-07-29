from ping3 import ping
import json

#delays = []
ping_data = []
with open('all_resolver_ip_address', 'r') as f:
	for line in f:
		y = line.split()
		temp = str(y).replace('[','').replace(']','')
		new = temp.strip("'")
		resolver, ip = new.split(',')
		print(ip)
		count = 5
		a = 0
		delays = []
		for i in range(count):
			try:
				d = ping(ip, unit='ms')
				if d:
					delays.append(d)
			except Exception as e:
				print('ping error:', e)
		for k in delays:
			a += k
		avg_ping = a/5
		print(avg_ping)
		ping_data.append({'resolver': resolver, 'IP_address': ip, 'avg_ping_time': avg_ping})
print(delays)
with open("ping_times.json", "a") as outfile:
        json.dump(ping_data, outfile)
