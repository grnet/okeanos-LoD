#!/bin/bash

export JARFILE=example.jar

execution_environment_name=0

/usr/local/flink/bin/flink run $JARFILE

if [ $execution_environment_name != 0 ]
then
  id=$(/usr/local/flink/bin/flink list | grep "$execution_environment_name" | cut -f4 -d" ")

  /usr/local/flink/bin/flink cancel $id
fi

