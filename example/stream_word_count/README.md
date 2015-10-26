# Description
In this directory you can find an example of an Apache Flink job of stream type.
Concretely, jobs of this type can process data in real time using the
`streamExecutionEnvironment` of Apache Flink. You should notice that, jobs of
stream type never end. That means that, once initiated, this job will process
any data that are provided as input and will stay idle while no input data are
provided.


# Contents
In the following paragraphs we will go through the contents of this file and
will provide information regarding the usage of this job.

## Source Code

### Input-Output
In `src` directory you can find the source code of the job. This job is
designed to read data from an Apache Kafka topic, process it and send the
results to another Apache Kafka topic. The machine where Apache Kafka is
deployed and also the names of the input and the output topics are configured
at the beginning of the program:

```
String zookeeper= "master:2181";
String consumerGroupId = "consumer-stream";
String kafkaBroker = "master:9092";
String inputTopic = "input";
String outputTopic = "stream-output";
```

You should change these parameters to meet your requirements.

### Execution Flow
The execution flow of the job is described by the following commands:

```
// Read input message from Kafka topic input and send it to the splitter class
        DataStream<Tuple4<String, Integer, String, String>> text = env
                .addSource(new FlinkKafkaConsumer082<>(inputTopic, new SimpleStringSchema(),
                        kafkaConsumerProperties))
                .flatMap(new Splitter())
                .groupBy(0)
                .sum(1)
                .addSink(new KafkaSink<Tuple4<String, Integer, String, String>>(kafkaBroker,
                        outputTopic, new tuple4serialization()));
```

Input data are fetched from Apache Kafka using a `FlinkKafkaConsumer082` as the
source. The data are then processed using a custom made splitter as a
`flatMap`. We will describe our custom splitter in a bit. Finaly, the processed
data are sent to an Apache Kafka topic using a `KafkaSink` as a sink.

### Serializer
When adding a sink, you should specify the way you want your data to be
serialized in order to be sent to their destination. The serializer you will
provide will be used to serialize each message before sending it to the output
destination. The serializer of our implementation transforms the message to
a String and the returns its bytes.

### FlatMapFunction
The FlatMapFunction is the core of the stream job. This is the function that
describes how the data will be processed. We use a Splitter as our
FlatMapFunction. From the code which we attach here for easy reference

```
// Receives the messages, splits it to words and then emits each word and number of appearance.
public static class Splitter implements FlatMapFunction<String, Tuple4<String, Integer, String,
        String>> {
    public void flatMap(String sentence,Collector<Tuple4<String, Integer, String, String>> out)
            throws Exception {
        String words[] = sentence.split(" ");
        for (String word : words){
            word = word.trim().replace("'", "");

            SimpleDateFormat dateFormat = new SimpleDateFormat("dd-MM-yyyy");
            SimpleDateFormat timeFormat = new SimpleDateFormat("HH:mm:ss");

            Date date = new Date();
            String dateFormatted = dateFormat.format(date);
            String timeFormatted = timeFormat.format(date);

            out.collect(new Tuple4<String, Integer, String, String>(word, 1, dateFormatted,
                    timeFormatted));
        }
    }
}
```

you can see that the splitter breaks each message to its words(words are defined
by spaces). It then appends to each word a time and a date and send it to the
output and increaces the respective word counter by one(1).

## Building
We use Apache Maven for building our job. It is adviced to statically build your job
before sending it to a Lambda Instance for execution. You can statically build
this job by running:

```
mvn clean compile assembly:assembly
```

You can find the required by Maven pom file in this directory.
