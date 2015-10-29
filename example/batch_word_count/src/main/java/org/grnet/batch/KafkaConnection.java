package org.grnet.batch;

import kafka.javaapi.producer.Producer;
import kafka.producer.KeyedMessage;
import kafka.producer.ProducerConfig;

import java.util.Properties;

/**
 *  @class: Implements a connector to Apache Kafka.
 */
public class KafkaConnection {

  private Producer<String, String> producer;
  private Properties props;
  private String topicId;
  private String brokerAddr;

  public KafkaConnection(String topicId, String brokerAddr) {
    this.topicId = topicId;
    this.brokerAddr = brokerAddr;

    props = new Properties();
    props.put("metadata.broker.list", brokerAddr);
    props.put("serializer.class", "kafka.serializer.StringEncoder");
    props.put("request.required.acks", "1");
    ProducerConfig config = new ProducerConfig(props);
    producer = new Producer<String, String>(config);
  }

  public void write(String s) {
    producer.send(new KeyedMessage<String, String>(topicId, s));
  }

}
