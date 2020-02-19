import json
import collections
import subprocess
import tldextract


def get_doh_sizes(har, resolver_uri="https://1.1.1.1/dns-query"):
    domains = get_unique_domains(har)
    all_sizes = {}
    for d in domains:
        # Use curl/doh to get the amount of TLS/HTTP/DoH data send and received in bytes
        try: 
            output = subprocess.check_output(["curl-doh/doh", "-v", d, resolver_uri], 
                                              stderr=subprocess.STDOUT, timeout=5)
        except Exception as e:
            print("curl/doh error:", e)
            all_sizes[d] = {}
            continue

        # Parse the output of curl/doh
        sizes = {'tls':  {'Send': 0, 'Recv': 0},
                 'http': {'Send': 0, 'Recv': 0},
                 'dns':  {'Send': 0, 'Recv': 0}}
        try:
            output = output.decode("utf-8")
            output = output.splitlines()
            for line in output:
                if line.startswith("<= Recv") or line.startswith("=> Send"):
                    direction, protocol, bytes_processed = parse_doh_output(line)
                    sizes[protocol][direction] += bytes_processed
        except Exception as e:
            print("Error parsing curl/doh output:", e)
            all_sizes[d] = {}
            continue
        all_sizes[d] = sizes

    return all_sizes


def parse_doh_output(line):
    # Parse out what kind direction data went on the wire
    line = line.split(", ")
    event = line[0].split(" ")
    direction = event[1]

    # Parse out what protocol the data belongs to
    protocol_debug = event[2]
    if protocol_debug == "SSL":
        protocol = "tls"
    elif protocol_debug == "header":
        protocol = "http"
    elif protocol_debug == "data":
        protocol = "dns"

    # Parse out how many bytes were sent/received
    bytes_processed = line[1].split(" ")
    bytes_processed = int(bytes_processed[0])
    return direction, protocol, bytes_processed


def get_dns_sizes(har, resolver_ip="1.1.1.1"):
    domains = get_unique_domains(har)
    all_sizes = {}
    for d in domains:
        # Use dig to get the amount of DNS data received in bytes
        try:
            nameserver = "@{0}".format(resolver_ip)
            output = subprocess.check_output(["dig", nameserver, "-4", d], 
                                               stderr=subprocess.STDOUT, timeout=2)
        except Exception as e:
            print("dig error:", e)
            all_sizes[d] = {}
            continue

        # Parse the output of dig
        sizes = {'dns': {'Recv': 0}}
        try:
            output = output.decode("utf-8")
            output = output.splitlines()
            for line in output:
                if line.startswith(";; MSG SIZE  rcvd:"):
                    bytes_received = int(line.split(";; MSG SIZE  rcvd:")[1])
                    sizes['dns']['Recv'] += bytes_received
        except Exception as e:
            print("Error parsing dig output:", e)
            all_sizes[d] = {}
            continue
        all_sizes[d] = sizes
    
    return all_sizes


def get_unique_domains(har):
    if not har:
        return []

    if "entries" not in har:
        return []
    entries = har["entries"]

    if len(entries) == 0:
        return []

    domains = []
    for entry in entries:
        # If a DNS request was made, record the timings
        if "request" not in entry:
            continue
        request = entry["request"]

        if "url" not in request:
            continue
        url = request["url"]

        ext = tldextract.extract(url)
        if ext.subdomain:
            fqdn = ext.subdomain + "." + ext.domain + "." + ext.suffix
        else:
            fqdn = ext.domain + "." + ext.suffix
        domains.append(fqdn)
    return list(set(domains))


if __name__ == "__main__":
    # Test DoH response size code
    sizes = get_doh_sizes("www.nytimes.com", "https://1.1.1.1/dns-query")
    print(sizes)

    sizes = get_doh_sizes("www.nytimes.com", "https://dns.quad9.net/dns-query")
    print(sizes)

    # Test DNS response size code
    sizes = get_dns_sizes("www.nytimes.com", "1.1.1.1")
    print(sizes)

    sizes = get_dns_sizes("www.nytimes.com", "9.9.9.9")
    print(sizes)
