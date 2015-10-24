package org.grnet.stream;

import org.apache.flink.api.common.functions.FlatMapFunction;
import org.apache.flink.api.java.tuple.Tuple4;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.connectors.kafka.KafkaSink;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaConsumer082;
import org.apache.flink.streaming.util.serialization.SerializationSchema;
import org.apache.flink.streaming.util.serialization.SimpleStringSchema;
import org.apache.flink.util.Collector;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Properties;

public class Main {

    public static void main(String[] args) throws Exception {

        String zookeeper= "master:2181";
        String consumerGroupId = "consumer-stream";
        String kafkaBroker = "master:9092";
        String inputTopic = "input";
        String outputTopic = "stream-output";

        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

        Properties kafkaConsumerProperties = new Properties();
        kafkaConsumerProperties.setProperty("bootstrap.servers", kafkaBroker);
        kafkaConsumerProperties.setProperty("zookeeper.connect", zookeeper);
        kafkaConsumerProperties.setProperty("group.id", consumerGroupId);

        // Read input message from Kafka topic input and send it to the splitter class
        DataStream<Tuple4<String, Integer, String, String>> text = env
                .addSource(new FlinkKafkaConsumer082<>(inputTopic, new SimpleStringSchema(),
                        kafkaConsumerProperties))
                .flatMap(new Splitter())
                .groupBy(0)
                .sum(1)
                .addSink(new KafkaSink<Tuple4<String, Integer, String, String>>(kafkaBroker,
                        outputTopic, new tuple4serialization()));

        //run the process
        env.execute("Stream Word Count");
    }

    public static class tuple4serialization implements SerializationSchema<Tuple4<String, Integer,
            String, String>, byte[]> {
        public byte[] serialize(Tuple4<String, Integer, String, String> element) {
            return element.toString().getBytes();
        }
    }

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
}
