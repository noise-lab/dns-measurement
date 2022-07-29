import geoip2.webservice
import json
#textfile=open("recursor_location_data.txt","a")
#with geoip2.webservice.Client(581949,'pOQnZNxO1PRlvPZH', 'geolite.info') as client:
#	response = client.city('https://dns.arapurayil.com/dns-query')	
#	print(response.country.iso_code)
#	print(response.country.name)
#	print(response.city.name)
resolver_ip_info = []
with open('all_resolver_ip_address', 'r') as f:
	for line in f:
		try:
			y = line.split()
			temp = str(y).replace('[','').replace(']','')
			new = temp.strip("'")
			print(new)
			#print(new.split(','))
			resolver, ip = new.split(',')
			print(resolver)
			print(ip)
			#new_ip = temp.strip("'")
			#print(resolver, new_ip)
			with geoip2.webservice.Client(581949,'pOQnZNxO1PRlvPZH', 'geolite.info') as client:
				if ip == "None":
					resolver_ip_info.append({'resolver': resolver, 'IP_address': None, 'country_iso_code': None, 'country_name': None, 'city_name':  None})
				else:
					response = client.city(ip)
					country_iso_code = response.country.iso_code
					country_name = response.country.name
					city_name = response.city.name
					resolver_ip_info.append({'resolver': resolver, 'IP_address': ip, 'country_iso_code': country_iso_code, 'country_name': country_name, 'city_name':  city_name})
					print(resolver, ip, country_iso_code, country_name, city_name)
		except Exception as e:
			err = 'Error parsing DNS output for website {0}: {1}'
print(resolver_ip_info)
with open("resolver_geolocation.json", "a") as outfile:
	json.dump(resolver_ip_info, outfile)
