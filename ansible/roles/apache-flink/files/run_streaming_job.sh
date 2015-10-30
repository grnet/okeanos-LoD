#!/bin/bash

export JARFILE=example.jar

execution_environment_name=""

function finish {
  id="$(/usr/local/flink/bin/flink list | grep "$execution_environment_name" | cut -f4 -d" ")"

  /usr/local/flink/bin/flink cancel $id
}

if [ "$execution_environment_name" != "" ]
then
  trap finish EXIT
fi

/usr/local/flink/bin/flink run $JARFILE

