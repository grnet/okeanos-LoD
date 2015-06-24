# lambda instance demo

## Batch process demo

Contains a java class (flink job) responsible for counting the hashtags of random tweets. The input tweets must be placed into hdfs, and the wordcount result is also output into the hdfs. 

### Things to do before running

- Build the project using "mvn clean package" on the project root (maven is required). Alternatively, use the compiled jar file (target directory).
- Put the input files into hdfs directory /user/root/input

### Prerequisites

- Hadoop (HDFS & YARN) must be installed and running (tested version 2.7.0)
- Flink must be installed and running (tested version 0.8.1)

### How to run

flink run hwc-1.0.jar -v -p &lt;number of processes&gt;

### How to get the output

The wordcount output will be placed into the hdfs directory /user/root/output. Each worker will have it's own output file, named after it's number.
