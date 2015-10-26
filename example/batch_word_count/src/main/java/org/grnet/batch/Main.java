package org.grnet.batch;

/**
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import org.apache.flink.api.common.functions.FlatMapFunction;
import org.apache.flink.api.java.DataSet;
import org.apache.flink.api.java.ExecutionEnvironment;
import org.apache.flink.api.java.tuple.Tuple4;
import org.apache.flink.core.fs.FileSystem;
import org.apache.flink.util.Collector;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;

public class Main {
    public static void main(String[] args) throws Exception {
        // HDFS configuration.
        String inputHDFSDirectory = "hdfs:///user/flink/input";
        String outputHDFSDirectory = "hdfs:///user/flink/output";

        // Apache Kafka configuration.
        String outputTopic = "batch-output";
        String kafkaBroker = "master:9092";

        // set up the execution environment
        final ExecutionEnvironment env = ExecutionEnvironment.getExecutionEnvironment();

        // Repeat for ever.
        while(true) {
            // get input data
            DataSet<String> text = env.readTextFile(inputHDFSDirectory);

            DataSet<Tuple4<String, Integer, String, String>> counts =
                // split up the lines
                text.flatMap(new LineSplitter())
                    // group by the tuple field "0" and sum up tuple field "1"
                    .groupBy(0)
                    .sum(1);

            // Write result to Kafka
            KafkaConnection kb = new KafkaConnection(outputTopic, kafkaBroker);
            List<Tuple4<String, Integer, String, String>> elements = counts.collect();
            for (Tuple4<String, Integer, String, String> e : elements) {
                kb.write((e.toString()));
            }

            // emit result to hdfs
            counts.writeAsText(outputHDFSDirectory, FileSystem.WriteMode.OVERWRITE);

            // execute program
            env.execute();

            // Wait for a minute before repeating.
            Thread.sleep(1 * 60 * 1000);
        }
    }

    /**
     * Implements the string tokenizer that splits sentences into words and the words into letters
     * as a user-defined FlatMapFunction.
     */
    public static final class LineSplitter implements FlatMapFunction<String, Tuple4<String,
        Integer, String, String>> {

        @Override
        public void flatMap(String value, Collector<Tuple4<String, Integer, String, String>> out) {
            // Split the sentence into words.
            String words[] = value.split(" ");
            for (String word : words){
                word = word.trim().replace("'", "");

                SimpleDateFormat dateFormat = new SimpleDateFormat("dd-MM-yyyy");
                SimpleDateFormat timeFormat = new SimpleDateFormat("HH:mm:ss");

                Date date = new Date();
                String dateFormatted = dateFormat.format(date);
                String timeFormatted = timeFormat.format(date);

                out.collect(new Tuple4<String, Integer, String, String>(word, 1, dateFormatted,
                    timeFormatted));

                // Split each word into letters.
                for(int i = 0;i < word.length();i++){
                    out.collect(new Tuple4<String, Integer, String, String>("" + word.charAt(i), 1,
                        dateFormatted, timeFormatted));
                }
            }
        }
    }
}
