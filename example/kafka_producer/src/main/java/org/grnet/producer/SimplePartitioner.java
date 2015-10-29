package org.grnet.producer;

import kafka.producer.Partitioner;
import kafka.utils.VerifiableProperties;

/**
 *  @class: This class can be used to configure the way a partition of the target topic is chosen.
 */
public class SimplePartitioner implements Partitioner {
  public SimplePartitioner (VerifiableProperties props) {

  }

  public int partition (Object key, int a_numPartitions) {
    return chosenPartition;
  }

  public static int chosenPartition = 0;

}
