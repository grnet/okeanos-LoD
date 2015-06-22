#!/bin/bash

while [ -f "/root/runrand" ]; do
   python /root/data-generator.py | /usr/lib/kafka_2.10-0.8.2.1/bin/kafka-console-producer.sh --broker-list snf-661306:9092 --topic input-tweets
   sleep 1
done

