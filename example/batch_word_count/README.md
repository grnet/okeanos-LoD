# Description
In this directory you can find an example of an Apache Flink job of batch type.
Concretely, jobs of this type can process big batches of data repeatedly with a
time interval between two executions. You should notice that its your
responsibility for the job to stay 'alive' and execute at the time intervals you
prefer.


# Contents
In the following paragraphs we will go through the contents of this directory
and will provide information regarding the usage of this job.

## Source Code

### Input-Output
In `src` directory you can find the source code of the job. The job is designed
to read data from HDFS, process and the save the results back to HDFS and also
send it to an Apache Kafka topic. The input and output HDFS directories, the
machine where Apache Kafka is running and the name of the topic are configured
at the beginning of the program:

```
// HDFS configuration.
String inputHDFSDirectory = "hdfs:///user/flink/input";
String outputHDFSDirectory = "hdfs:///user/flink/output";

// Apache Kafka configuration.
String outputTopic = "batch-output";
String kafkaBroker = "master:9092";
```

You should change these values to meet your requirements.

### Execution Flow
The execution flow of the job consists of three(3) stages. In the first stage,
the input data are read from HDFS:

```
// get input data
            DataSet<String> text = env.readTextFile(inputHDFSDirectory);
```

In the second stage, these data are processed:

```
DataSet<Tuple4<String, Integer, String, String>> counts =
    // split up the lines
    text.flatMap(new LineSplitter())
        // group by the tuple field "0" and sum up tuple field "1"
        .groupBy(0)
        .sum(1);
```

The processing is done using a FlatMapFunction which we will describe later.

In the final stage, the results from the processing are sent to Apache Kafka:

```
// Write result to Kafka
            KafkaConnection kb = new KafkaConnection(outputTopic, kafkaBroker);
            List<Tuple4<String, Integer, String, String>> elements = counts.collect();
            for (Tuple4<String, Integer, String, String> e : elements) {
                kb.write((e.toString()));
            }
```

and are also saved to HDFS:

```
counts.writeAsText(outputHDFSDirectory, FileSystem.WriteMode.OVERWRITE);
```

This procedure then repeats at a chosen interval.


### FlatMapFunction
The FlatMapFunction is the core of the processing procedure. It defines the
way the data will be processed. In this example, we provide a FlatMapFunction
that will split every input line in words and count them. After that, each
word is split into letters and the letters are also counted.

### Building
We use Apache Maven for build our job. It is advised to statically build your
job before sending it to a Lambda Instance for execution. You can statically
build this job by running:

```
mvn clean compile assembly:assembly
```

You can find the required by Maven pom file in this directory.
