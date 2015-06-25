#!/bin/bash

# Change zookeeper-host and application-master-host with the ips of the zookeeper host and the Apache Flink Application Master host. Tis command will create a live feed from topic input
# to the port 9999 of the Application Master host. The stream job should then read the port 9999. The Application Master is responsible for distributing the data to the appropriate machines.
/usr/local/kafka/bin/kafka-console-consumer.sh --consumer.config /usr/local/kafka/config/consumer.properties --zookeeper zookeeper-host:2181  --topic input | nc -lk application-master-host -p 9999;
