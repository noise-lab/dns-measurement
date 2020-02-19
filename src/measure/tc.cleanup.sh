#!/bin/bash

INTERFACE=eth0

echo "Clean up current shaping/filtering"
tc qdisc delete dev ${INTERFACE} root || true
tc qdisc delete dev ${INTERFACE} ingress || true
