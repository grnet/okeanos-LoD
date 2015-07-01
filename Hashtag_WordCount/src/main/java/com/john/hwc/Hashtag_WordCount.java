package com.john.hwc;

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

import org.apache.flink.api.java.DataSet;
import org.apache.flink.api.java.ExecutionEnvironment;
import org.apache.flink.api.common.functions.FlatMapFunction;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.api.java.tuple.Tuple3;
import org.apache.flink.api.java.tuple.Tuple4;
import org.apache.flink.core.fs.FileSystem;
import org.apache.flink.util.Collector;

import java.text.DateFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Implements the "Hashtag_WordCount" program that computes a simple hashtag occurrence histogram
 * over some randomly generated tweets
 *
 * <p>
 * This example shows how to:
 * <ul>
 * <li>write a simple Flink program.
 * <li>use Tuple data types.
 * <li>write and use user-defined functio±ns.
 * </ul>
 *
 */
public class Hashtag_WordCount {

    //
    //	Program
    //

    public static void main(String[] args) throws Exception {

        // set up the execution environment
        final ExecutionEnvironment env = ExecutionEnvironment.getExecutionEnvironment();

        // get input data
        DataSet<String> text = env.readTextFile("hdfs:///user/root/input");

        DataSet<Tuple4<String, Integer, String, String>> counts =
                // split up the lines in pairs (2-tuples) containing: (word,1)
                text.flatMap(new LineSplitter())
                        // group by the tuple field "0" and sum up tuple field "1"
                        .groupBy(0)
                        .sum(1);


        // emit result to hdfs
        counts.writeAsText("hdfs:///user/root/output", FileSystem.WriteMode.OVERWRITE);
        //timestamp.writeAsText("hdfs:///user/root/output", FileSystem.WriteMode.OVERWRITE);

        // execute program
        env.execute("Hashtag WordCount");
    }

    //
    // 	User Functions
    //

    /**
     * Implements the string tokenizer that splits sentences into words as a user-defined
     * FlatMapFunction. The function takes a line (String) and splits it into
     * multiple pairs in the form of "(hashtag,1)" (Tuple2<String, Integer>).
     */
    public static final class LineSplitter implements FlatMapFunction<String, Tuple4<String, Integer, String, String>> {

        @Override
        public void flatMap(String value, Collector<Tuple4<String, Integer, String, String>> out) {

            // Acquire hashtags
            List<String> hashtags = new ArrayList<String>();
            Matcher m = Pattern.compile("#(\\w+)")
                    .matcher(value.toLowerCase());
            while (m.find()) {
                hashtags.add(m.group(0));
            }
            String[] tokens = hashtags.toArray(new String[hashtags.size()]);

            //SimpleDateFormat sdf = new SimpleDateFormat("dd-MM-yyyy,HH:mm:ss");
            SimpleDateFormat sdfd = new SimpleDateFormat(" dd-MM-yyyy");
            SimpleDateFormat sdft = new SimpleDateFormat(" HH:mm:ss");
            Date dateobj = new Date();
            String date = sdfd.format(dateobj);
            String time = sdft.format(dateobj);

            // emit the pairs
            for (String token : tokens) {
                if (token.length() > 0) {
                    out.collect(new Tuple4<String, Integer, String, String>(token, 1, date, time));
                }
            }
        }
    }
}
