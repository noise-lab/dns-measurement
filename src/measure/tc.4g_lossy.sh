#!/bin/bash

set -ex

INTERFACE=eth0

# 3G
#LATENCY=150ms
#JITTER=8ms
#LOSS=2.1%
#RATE_UP=1mbit
#RATE_DOWN=1mbit
#BURST=256k

# 4G
# best values across providers
# via https://www.opensignal.com/reports/2019/01/usa/mobile-network-experience
LATENCY=53.3ms
JITTER=1ms
LOSS=1.5%
RATE_UP=7.44mbit
RATE_DOWN=22.1mbit
BURST=256k


echo "Clean up current shaping/filtering"
tc qdisc delete dev ${INTERFACE} root || true
tc qdisc delete dev ${INTERFACE} ingress || true

tc qdisc add dev ${INTERFACE} root handle 1:0 htb default 12
tc qdisc add dev ${INTERFACE} ingress

# Do not affect SSH and MySQL to neon.cs.princeton.edu
tc class add dev ${INTERFACE} parent 1:0 classid 1:11 htb rate 1gbit burst 1g
tc filter add dev ${INTERFACE} parent 1:0 protocol ip prio 1 u32 match ip sport 22 0xffff flowid 1:11
tc filter add dev ${INTERFACE} parent 1:0 protocol ip prio 1 u32 match ip dst 128.112.168.26/32 match ip dport 5432 0xffff flowid 1:11

echo "Slowing down egress to ${RATE_UP}/s"
tc class add dev ${INTERFACE} parent 1:0 classid 1:12 htb rate ${RATE_UP} burst ${BURST} prio 2

echo "Setting latency to ${LATENCY} +/- ${JITTER} with ${LOSS} loss"
tc qdisc add dev ${INTERFACE} parent 1:12 netem delay ${LATENCY} ${JITTER} loss ${LOSS}

echo "Slowing down ingress to ${RATE_DOWN}/s"
tc filter add dev ${INTERFACE} parent ffff: protocol ip prio 1 u32 match ip dport 22 0xffff flowid 1:11
tc filter add dev ${INTERFACE} parent ffff: protocol ip prio 1 u32 match ip src 128.112.168.26/32 match ip sport 5432 0xffff flowid 1:11
tc filter add dev ${INTERFACE} parent ffff: protocol ip prio 2 estimator 10ms 1s matchall action police rate ${RATE_DOWN} burst ${BURST} mtu ${BURST} peakrate ${RATE_DOWN} drop flowid 1:12
