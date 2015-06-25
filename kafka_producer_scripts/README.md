# lambda instance demo

## Kafka data producer

Runs random tweet generator script (currently placed in /root/data-generator.py), and sends the output to the Kafka topic "input-tweets".

### Prerequisites

- Run on Debian 8.0 node
- Python and Kafka must be installed
- data-generator.py must be placed in /root

### How to run

Create (touch) a file named "runrand" in root.
Run the rand_kafka_producer.sh
The script will run until the runrand file is deleted, producing random tweets every second.
