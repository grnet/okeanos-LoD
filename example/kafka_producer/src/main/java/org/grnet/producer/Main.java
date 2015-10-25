package org.grnet.producer;

import java.util.Properties;

import kafka.javaapi.producer.Producer;
import kafka.producer.KeyedMessage;
import kafka.producer.ProducerConfig;

import org.apache.commons.cli.Options;
import org.apache.commons.cli.ParseException;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.DefaultParser;
import org.apache.commons.cli.HelpFormatter;


/**
 *  @class: Class that wraps the main Apache Kafka producer functionality.
 */
public class Main {

  /**
   * Main method that takes a message through the command line and send it to a remote Apache Kafka
   * broker.
   *
   * @param args For information regarding command line arguments, please refer to
   *             https://commons.apache.org/proper/commons-cli/
   */
  public static void main(String[] args) throws ParseException {
    // Organize command line arguments.
    Options commandLineOptions = new Options();

    commandLineOptions.addOption("m", "message", true, "The message to be sent to Apache Kafka");
    commandLineOptions.addOption("a", "ip-address", true, "The IP address of the remote host");
    commandLineOptions.addOption("p", "port", false, "The port of the remote host (default 9092)");
    commandLineOptions.addOption("t", "topic", false, "The topic that the message should be sent" +
        "(default 'input')");
    commandLineOptions.addOption("c", "chosen-partition", false, "The partition of the topic" +
        "(default 0)");

    CommandLineParser commandLineParser = new DefaultParser();
    CommandLine commandLine = commandLineParser.parse(commandLineOptions, args);

    if (args.length == 0) {
      HelpFormatter helpFormatter = new HelpFormatter();
      helpFormatter.printHelp("java -jar [jar-name] [options]",
          commandLineOptions);
      return;
    }

    // Parse provided command line arguments.
    String message;
    String remoteIP;
    String remotePort = "9092";
    String kafkaTopic = "input";

    if (!commandLine.hasOption('m')) {
      throw new IllegalArgumentException("No message was provided...");
    }
    else {
      message = commandLine.getOptionValue('m');
    }

    if (!commandLine.hasOption('a')) {
      throw new IllegalArgumentException("No remote IP address was provided...");
    }
    else {
      remoteIP = commandLine.getOptionValue('a');
    }

    if (commandLine.hasOption('p')) {
      remotePort = commandLine.getOptionValue('p');
    }

    if (commandLine.hasOption('t')) {
      kafkaTopic = commandLine.getOptionValue('t');
    }

    if (commandLine.hasOption('c')) {
      SimplePartitioner.chosenPartition = Integer.parseInt(commandLine.getOptionValue('c'));
    }

    // Create an Apache Kafka producer and send the given message.
    Properties props = new Properties();
    props.put("metadata.broker.list", remoteIP + ":" + remotePort);
    props.put("serializer.class", "kafka.serializer.StringEncoder");
    props.put("partitioner.class", "org.grnet.producer.SimplePartitioner");
    props.put("request.required.acks", "1");
    ProducerConfig config = new ProducerConfig(props);

    Producer<String, String> producer = new Producer<String, String>(config);

    KeyedMessage<String, String> data = new KeyedMessage<String, String>(kafkaTopic, message);
    producer.send(data);

    // Close the Apache Kafka producer.
    producer.close();
  }

}
