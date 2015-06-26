package stream.streamingtagcount;

import org.apache.flink.api.common.functions.FlatMapFunction;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.util.Collector;

/**
 *
 * @author Efi Kaltirimidou
 */
public class TagCount {

    public static void main(String[] args) throws Exception {
        
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        
        //read input message from port 9999 of host and send it to the splitter class
        DataStream<Tuple2<String, Integer>> dataStream = env
                .socketTextStream("0.0.0.0", 9999)
                .flatMap(new Splitter())
                .groupBy(0)
                .sum(1);
        
        //write results to this file
        dataStream.writeAsText("/root/streaming_output");
        
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
