---
title: API | lambda instance details
description: Returns the details of a specified lambda instance
---

# API - lambda instance details - Description

Lambda instance details call, given an authentication token through the header x-api-key, will firstly check the validity of the token. If the token is invalid, the API will reply with a "401 Unauthorized" code. If the token is valid, the API will search for the specified lambda instance. If the specified lambda instance does not exist, the API will reply with a "404 Not Found" code. If the specified lambda instance exists, the API will reply with the details of it along with a "200 OK" code.

## Basic Parameters

Type   | Description
-------|-----------------
**Description** | lambda instance details
**URL**         | /backend/lambda-instances/[uuid]
**HTTP Method** | GET
**Security**    | Basic Authentication


### Headers

Type | Description | Required | Default value | Example value
------|-------------|----------|---------------|---------------
Authorization | ~okeanos authentication token. If you have an account you may find the authentication token at (Dashboad-> API Access) https://accounts.okeanos.grnet.gr/ui/api_access. | `Yes` | None | tJ3b3f32f23ceuqdoS


### Parameters

Name  | Description | Required | Default value | Example value
------|-------------|----------|---------------|---------------
uuid  | The uuid of the specified lambda instance. For more information see [List Lambda instances page](LambdaInstanceList.md) . |`Yes` |None| 3

### Keywords in response

Name | Description | Default value
------|------------|---------------
name | The name of the lambda instance | Lambda Instance
uuid | Unique integer identifying a lambda instance | None
id   | Unique integer used to enumerate lambda instances | Auto Increment

## Example

In this example we are going to get the details of the lambda instance with uuid 3

The request in curl

```
curl -X GET -H "x-api-key: tJ3b3f32f23ceuqdoS_TH7m0d6yxmlWL1r2ralKcttY" 'http://<url>/backend/lambda-instances/3/'
```


### Response body

If the authentication token is correct, a sample response is

```
{
  "data": {
    "details": {
      "cluster": {
        "number_of_slaves": 12,
        "cpus_per_machine": 8,
        "ram_per_machine": 4094,
        "disk_per_machine": 40,
        "master_ip": "81.82.83.84"
      },
      "hdfs": {
        "replication_factor": 12
      },
      "flink": {
        "number_of_task_managers": 12,
        "cpus_per_task_manager": 8,
        "ram_per_task_manager": 1024,
        "cpus_batch": 4,
        "cpus_stream": 4
      },
      "kafka": {
        "number_of_kafka_topics": 3,
        "topics": [
          {"name": "input_batch_topic"},
          {"name": "input_stream_topic"},
          {"name": "output_topic"}
        ]
      }
    },
    "uuid": 1,
    "name": "Lambda Instance 2",
    "id": 14
  }
}
```

For the case where the authentication token is not correct, refer to [Authentication page](Authentication.md).

### Response messages

The main response messages are:

- HTTP/1.1 200 OK : (Success)
- HTTP/1.1 401 UNAUTHORIZED : (Fail)
- HTTP/1.1 404 NOT FOUND : (Fail)
