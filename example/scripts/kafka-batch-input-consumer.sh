#!/bin/bash

# Get the messages from Kafka and store them to a temporary file.
/usr/local/kafka/bin/kafka-console-consumer.sh --consumer.config /usr/local/kafka/config/consumer-batch.properties --zookeeper localhost:2181 --topic input > temporary_input;

timestamp=$(date +"%F_%H_%M_%S");

# The last 12 lines of the file are created from the timeout exception thrown by the
# kafka-console-consumer.sh script and they should be removed.
head -n -12 temporary_input > temporary_input2;

# Store the final file on HDFS.
$(/usr/local/hadoop/bin/hdfs dfs -put temporary_input2 /user/root/input/tweets_$timestamp);

# Remove all temporary files.
rm temporary_input;
rm temporary_input2;
