#!/bin/bash

# Change "zookeeper-host" with the IP address of the machine that runs Apache Zookeeper.
# Change "application-master-host" with the IP address of the machine tha runs the Apache Flink Application Master.
# This command will create a live feed of data, from the topic "input" to the port 9999 of the Application Master host.
# The stream job will then read the data from the port 9999.
# The Application Master is responsible for distributing the data to the machines that run the Apache Flink job.

/usr/local/kafka/bin/kafka-console-consumer.sh --consumer.config /usr/local/kafka/config/consumer-stream.properties --zookeeper zookeeper-host:2181  --topic input | nc -lk application-master-host -p 9999;
