# Description
In this directory you can find a custom Apache kafka producer. The aim of this
producer is to demonstrate the Java API of the Apache Kafka and how it can be
used to send data to a remote host.


# Contents
In the following paragraphs we will go through the contents of this directory
and we will also provide information regarding the usage of the Apache Kafka
producer.

## Source Code
The source code of our example, is a modified version of the example provided
by Apache Kafka [here]. The addition we have made is to add some command line
arguments processing so that the producer can be used through the command line.

## Building
To build the producer we use Apache Maven. The required `pom.xml` file is can
be found at this directory. To build the producer run the command:

```
mvn clean compile
```

We suggest you statically compile the producer so you can use it on any machine.
To statically compile the producer you can run the command:

```
mvn clean compile assembly:assembly
```

## Usage
To run the producer, run

```
java -jar producer-1.0-jar-with-dependencies.jar --ip-address=<remote-ip> -l
```

where:

| Parameter   | Description
| ----------- | -----------
| remote-ip   | The public IPv4 of the remote machine where Apache Zookeeper is located

The `-l` flag tells the producer to continuously monitor the terminal and send
every message that you type to it.

To get information regarding the command line parameters of the producer, run:

```
java -jar producer-1.0-jar-with-dependencies.jar
```

Upon execution, this producer will connect to the remote host and start sending
the data you type on your console to the specified topic.


# Notes
You should note that, the topic you choose, should have at least one partition
with leader the Master Node of the Lambda Instance so it can be accessible from
the outside world.

When running the producer, you will notice that it produces a lot of logs.
That is due to Apache Kafka and its default configuration. To change that,
you can modify the `log4j.properties` file in `src/main/resource` directory.

[here]: https://commons.apache.org/proper/commons-cli/
