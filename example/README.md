# lambda instance demo



## Prerequisites

- Hadoop (HDFS & YARN) must be installed and running (tested version 2.7.0)
- Flink must be installed and running (batch job requires 0.9.0, streaming job requires 0.8.1)
- Kafka must be installed and running (tested version 2.10-0.8.2.1)

## Things to do before running the examples
- Place the Kafka configurations provided into /usr/local/kafka/config/.
- Run create-input-topic.sh script to create the input topic named "input".
- Create (touch) a file named "runrand" in root.
- Run the scripts/rand_kafka_producer.sh. The script will run until the runrand file is deleted, producing random tweets every second.




## Batch process demo

Contains a java class (flink batch job) responsible for counting the hashtags of random tweets. The input tweets are read from hdfs.  The wordcount result is sent to a Kafka topic and also output into the hdfs. 

### Things to do before running the batch process demo

- Static compile the project using "mvn clean compile assembly:single" on the project root (maven is required).
- Create a Kafka topic named batch-output.


### How to run

- First, run  scripts/kafka-batch-input-consumer.sh
- After that, run flink run hwc-1.0-jar-with-dependencies.jar -v -p &lt;number of processes&gt;
- The above can also be set as a crontab, to run the batch job at regular intervals.

### How to get the output

- The wordcount output will be sent into the Kafka topic named batch-output.
- The wordcount output will also be placed into the hdfs directory /user/root/output. Each worker will have it's own output file, named after it's number.




## Stream process demo

Contains a java class (flink stream job) responsible for counting the hashtags of random tweets. The input tweets are read from Kafka. The wordcount result is stored into the local filesystem.

### Things to do before running the stream process demo

- Replace the String zookeeper with your zookeeper hostname.
- Build the project using "mvn clean package" on the project root (maven is required).
- Create a Kafka topic named stream-output.
 
### How to run

flink run StreamingTagCount-1.0.jar -v -p &lt;number of processes&gt;

### How to get the output

- The wordcount output will also be placed into the local file /root/streaming_output, in any of the nodes.
- TODO: The wordcount output will be sent into the Kafka topic named stream-output.
