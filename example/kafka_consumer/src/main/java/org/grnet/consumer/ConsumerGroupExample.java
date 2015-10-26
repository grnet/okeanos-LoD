package org.grnet.consumer;

import kafka.consumer.ConsumerConfig;
import kafka.consumer.KafkaStream;
import kafka.javaapi.consumer.ConsumerConnector;

import org.apache.commons.cli.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

/**
 *  @class: Class that wraps the main Apache Kafka consumer functionality.
 *
 *  For more information regarding this example, please refer to
 *  https://cwiki.apache.org/confluence/display/KAFKA/Consumer+Group+Example
 */
public class ConsumerGroupExample {
  private final ConsumerConnector consumer;
  private final String topic;
  private  ExecutorService executor;

  public ConsumerGroupExample(String a_zookeeper, String a_groupId, String a_topic) {
    consumer = kafka.consumer.Consumer.createJavaConsumerConnector(
        createConsumerConfig(a_zookeeper, a_groupId));
    this.topic = a_topic;
  }

  public void shutdown() {
    if (consumer != null) consumer.shutdown();
    if (executor != null) executor.shutdown();
    try {
      if (!executor.awaitTermination(5000, TimeUnit.MILLISECONDS)) {
        System.out.println("Timed out waiting for consumer threads to shut down," +
            "exiting uncleanly");
      }
    } catch (InterruptedException e) {
      System.out.println("Interrupted during shutdown, exiting uncleanly");
    }
  }

  public void run(int a_numThreads) {
    Map<String, Integer> topicCountMap = new HashMap<String, Integer>();
    topicCountMap.put(topic, new Integer(a_numThreads));
    Map<String, List<KafkaStream<byte[], byte[]>>> consumerMap =
        consumer.createMessageStreams(topicCountMap);
    List<KafkaStream<byte[], byte[]>> streams = consumerMap.get(topic);

    // now launch all the threads
    //
    executor = Executors.newFixedThreadPool(a_numThreads);

    // now create an object to consume the messages
    //
    int threadNumber = 0;
    for (final KafkaStream stream : streams) {
      executor.submit(new ConsumerTest(stream, threadNumber));
      threadNumber++;
    }
  }

  private static ConsumerConfig createConsumerConfig(String a_zookeeper, String a_groupId) {
    Properties props = new Properties();
    props.put("zookeeper.connect", a_zookeeper);
    props.put("group.id", a_groupId);
    props.put("zookeeper.session.timeout.ms", "5000");
    props.put("zookeeper.sync.time.ms", "200");
    props.put("auto.commit.interval.ms", "1000");

    return new ConsumerConfig(props);
  }

  /**
   *  Main method that reads messages from a remote Apache Kafka installation and prints it to the
   *  console.
   *
   *  @param args For more information regarding command line arguments, please refer to
   *              https://commons.apache.org/proper/commons-cli/
   */
  public static void main(String[] args) throws ParseException {
    // Organize command line arguments.
    Options commandLineOptions = new Options();

    commandLineOptions.addOption("a", "id-address", true, "The IP address of the remote host");
    commandLineOptions.addOption("t", "topic", true, "The topic to read from");
    commandLineOptions.addOption("p", "port", true, "The port of the remote host (default 2181)");
    commandLineOptions.addOption("g", "group-id", true, "The id of this group of consumers " +
        "(default custom-consumer)");
    commandLineOptions.addOption("c", "concurrency", true, "The number of threads to be used for " +
        "consuming the messages (default 1)");

    CommandLineParser commandLineParser = new DefaultParser();
    CommandLine commandLine = commandLineParser.parse(commandLineOptions, args);

    if (args.length == 0) {
      HelpFormatter helpFormatter = new HelpFormatter();
      helpFormatter.printHelp("java -jar [jar-name] [options]", commandLineOptions);
      return;
    }

    // Parse provided command line arguments.
    String zooKeeper;
    String groupId = "custom-consumer";
    String topic;
    int threads = 1;

    if (!commandLine.hasOption('a')) {
      throw new IllegalArgumentException("No remote IP address was provided...");
    }
    else {
      zooKeeper = commandLine.getOptionValue('a');
    }

    if (!commandLine.hasOption('t')) {
      throw new IllegalArgumentException("No topic was provided...");
    }
    else {
      topic = commandLine.getOptionValue('t');
    }

    if (!commandLine.hasOption('p')) {
      zooKeeper += ":2181";
    }
    else {
      zooKeeper += ":" + commandLine.getOptionValue('p');
    }

    if (commandLine.hasOption('g')) {
      groupId = commandLine.getOptionValue('g');
    }

    if (commandLine.hasOption('c')) {
      threads = Integer.parseInt(commandLine.getOptionValue('c'));
    }

    ConsumerGroupExample example = new ConsumerGroupExample(zooKeeper, groupId, topic);
    example.run(threads);

    try {
      // Note that this will pull main thread to sleep for 10 minutes while the consumer threads
      // will read the messages from the remote Apache Kafka installation.
      // In case you want to put main thread to sleep forever until interrupted, use
      // Thread.currentThread().wait();
      Thread.sleep(10 * 60 * 1000);

    } catch (InterruptedException ie) {

    }
    example.shutdown();
  }

}
