# Description
In this directory you can find a custom Apache kafka consumer. The aim of this
consumer is to demonstrate the Java API of the Apache Kafka and how it can be
used to receive data from a remote host.


# Contents
In the following paragraphs we will go through the contents of this directory
and we will also provide information regarding the usage of the Apache Kafka
consumer.

## Source Code
The source code of our example, is a modified version of the example provided
by Apache Kafka [here]. The addition we have made is to add come command line
arguments processing so that the consumer can be used through the command line.

## Building
To build the consumer we use Apache Maven. The required `pom.xml` file is can
be found at this directory. To build the consumer run the command:

```
mvn clean compile
```

We suggest you statically compile the consumer so you can use it on any machine.
To statically compile the consumer you can run te command:

```
mvn clean compile assembly:assembly
```

## Usage
To run the consumer, run

```
java -jar consumer-1.0-jar-with-dependencies.jar -a <remote-ip> -p <remote-port> -g <group-id> -t <topic> -c <concurrency>
```

where:

| Parameter   | Description
| ----------- | -----------
| remote-ip   | The public IPv4 of the remote machine where Apache Zookeeper is located
| remote-port | The port of the remote machine where Apache Zookeeper listens
| group-id    | The Apache Kafka id for this group of consumers
| topic       | The topic from which this group of consumer will read data
| concurrency | The number of threads to be used by this group

To get information regarding the command line parameters of the consumer, run:

```
java -jar consumer-1.0-jar-with-dependencies.jar
```

Upon execution, this consumer will connect to the remote host and start fetching
data from the specified topic. The data will be displayed on the console.

[here]: https://cwiki.apache.org/confluence/display/KAFKA/Consumer+Group+Example
