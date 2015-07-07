package stream.streamingtagcount;

import org.apache.flink.api.common.functions.FlatMapFunction;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.connectors.kafka.KafkaSink;
import org.apache.flink.streaming.connectors.kafka.KafkaSource;
import org.apache.flink.streaming.connectors.util.SimpleStringSchema;
import org.apache.flink.util.Collector;

/**
 *
 * @author Efi Kaltirimidou
 */
public class TagCount {

    public static void main(String[] args) throws Exception {

        String zookeeper= "snf-xxxxxx:2181", consGId = "consumer-stream", inputTopic = "input", outputTopic = "stream-output",
                outputFile = "/root/streaming_output";

        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

        // Read input message from Kafka topic input and send it to the splitter class
        DataStream<Tuple2<String, Integer>> text = env
                .addSource(new KafkaSource<String>(zookeeper, consGId, inputTopic, new SimpleStringSchema()))
                .flatMap(new Splitter())
                .groupBy(0)
                .sum(1);

        //read input message from port 9999 of host and send it to the splitter class
        /*DataStream<Tuple2<String, Integer>> dataStream = env
                .socketTextStream("0.0.0.0", 9999)
                .flatMap(new Splitter())
                .groupBy(0)
                .sum(1);*/

        //write results to this file
        text.writeAsText(outputFile);
        
        //run the process
        env.execute("Socket Stream WordCount");
    }
    
    //receives the messages, splits it between the words and the hashtags and then emits each hashtag and number of appearence
    public static class Splitter implements FlatMapFunction<String, Tuple2<String, Integer>> {
        public void flatMap(String sentence, Collector<Tuple2<String, Integer>> out) throws Exception {
            String words[] = sentence.split(",");
            String tags = words[1].trim();
            tags = tags.replace("'", "");
            for (String word: tags.split(" ")) {
                out.collect(new Tuple2<>(word, 1));
            }
        }
    }
    
}
