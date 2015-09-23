#!/bin/bash

# This script should be executed on the machine on which zookeeper is running. To execute it on another machine, change the
# "localhost" on the following command with the IP address of the machine that runs zookeeper.

/usr/local/kafka/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic input;
