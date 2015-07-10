package stream.streamingtagcount;

import org.apache.flink.api.common.functions.FlatMapFunction;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.api.java.tuple.Tuple4;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.connectors.kafka.KafkaSink;
import org.apache.flink.streaming.connectors.kafka.KafkaSource;
import org.apache.flink.streaming.connectors.util.SerializationSchema;
import org.apache.flink.streaming.connectors.util.SimpleStringSchema;
import org.apache.flink.util.Collector;

import java.text.SimpleDateFormat;
import java.util.Date;

/**
 *
 * @author Efi Kaltirimidou
 */
public class TagCount {

    public static void main(String[] args) throws Exception {

        String zookeeper= "snf-xxxxxx:2181", consGId = "consumer-stream", kafkaBroker = "snf-xxxxxx:9092", inputTopic = "input", outputTopic = "streaming-output",
                outputFile = "/root/streaming_output";

        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

        // Read input message from Kafka topic input and send it to the splitter class
        DataStream<Tuple4<String, Integer, String, String>> text = env
                .addSource(new KafkaSource<String>(zookeeper, consGId, inputTopic, new SimpleStringSchema()))
                .flatMap(new Splitter())
                .groupBy(0)
                .sum(1)
                .addSink(new KafkaSink<Tuple4<String, Integer, String, String>, String>(outputTopic, kafkaBroker, new tuple4serialization()));


        //write results to this file
        //text.writeAsText(outputFile);
        
        //run the process
        env.execute("Socket Stream WordCount");
    }

    public static class tuple4serialization implements SerializationSchema<Tuple4<String, Integer, String, String>, String> {
        public String serialize(Tuple4<String, Integer, String, String> element) {
            return element.toString();
        }
    }
    
    //receives the messages, splits it between the words and the hashtags and then emits each hashtag and number of appearance
    public static class Splitter implements FlatMapFunction<String, Tuple4<String, Integer, String, String>> {
        public void flatMap(String sentence, Collector<Tuple4<String, Integer, String, String>> out) throws Exception {
            String words[] = sentence.split(",");
            String tags = words[1].trim();
            tags = tags.replace("'", "");
            SimpleDateFormat sdfd = new SimpleDateFormat(" dd-MM-yyyy");
            SimpleDateFormat sdft = new SimpleDateFormat(" HH:mm:ss");
            Date dateobj = new Date();
            String date = sdfd.format(dateobj);
            String time = sdft.format(dateobj);
            for (String word: tags.split(" ")) {
                out.collect(new Tuple4<String, Integer, String, String>(word, 1, date, time));
            }
        }
    }
    
}
