#!/bin/bash

echo "Resolver measurements started. Press Ctrl+C to stop."
while true
do
    sudo python3 resolver_data.py
done
echo "Stopping resolver measurements."
