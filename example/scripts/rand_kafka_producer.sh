#!/bin/bash

while [ -f "runrand" ]; do
   python data-generator.py | /usr/local/kafka/bin/kafka-console-producer.sh --broker-list 192.168.0.3:9092 --topic input
   sleep 1
done
