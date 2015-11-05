---
title: API | lambda instance details
description: Returns the details of a specified lambda instance
---

# API - lambda instance details - Description

Lambda instance details call, given an authentication token through the header authentication,
will firstly check the validity of the token. If the token is invalid, the API will reply with a
"401 Unauthorized" code. If the token is valid, the API will search for the specified lambda
instance. If the specified lambda instance does not exist, the API will reply with a
"404 Not Found" code. If the specified lambda instance exists, the API will reply with the details
of it along with a "200 OK" code. It is possible to only get the status relevant details or the
information relevant details of the lambda instance. This can be done by using the "filter" GET
parameter with the request. The values that this parameter should have are "info" or "status".

## Basic Parameters

Type   | Description
-------|-----------------
**Description** | Get details of a specified lambda instance
**URL**         | /api/lambda-instances/[lambda-instance-id]/
**HTTP Method** | GET
**Security**    | Basic Authentication


### Headers

Type | Description | Required | Default value | Example value
------|-------------|----------|---------------|---------------
Authorization | ~okeanos authentication token. If you have an account you may find the authentication token at (Dashboad-> API Access) https://accounts.okeanos.grnet.gr/ui/api_access. | `Yes` | None | Token tJ3b3f32f23ceuqdoS


### Parameters

Name  | Description | Required | Default value | Example value
------|-------------|----------|---------------|---------------
lambda-instance-id  | The id of the specified lambda instance. For more information see [List Lambda instances page](LambdaInstancesList.md) . |`Yes` |None| 3f763964-d519-4fd2-916d-b5cfbe3b878b
filter | Specifies which details to return | `No` | None | info


## Example

In this example we are going to get the details of the lambda instance with id 3f763964-d519-4fd2-916d-b5cfbe3b878b

The request in curl

```
curl -X GET -H "Authorization:Token tJ3b3f32f23ceuqdoS_TH7m0d6yxmlWL1r2ralKcttY" \
 'https://<hostname>/api/lambda-instances/3f763964-d519-4fd2-916d-b5cfbe3b878b/'
```


### Response body

If the authentication token is correct, a sample response is

```
{
  "status": {
    "short_description": "Lambda instance details",
    "code": 200
  },
  "data": [
    {
      "info": {
        "instance_info": {
          "project_name": "lambda.grnet.gr",
          "master_name": "lambda-master-2",
          "vcpus_master": 4,
          "network_request": 1,
          "disk_slave": 20,
          "slaves": 2,
          "ram_slave": 4096,
          "ram_master": 4096,
          "vcpus_slave": 4,
          "ip_allocation": "master",
          "disk_master": 20,
          "master_node_id": 10000
        },
        "id": "3f763964-d519-4fd2-916d-b5cfbe3b878b",
        "name": "My first Lambda Instance"
      },
      "status": {
        "message": "CLUSTER_FAILED",
        "code": "11",
        "details": "~okeanos cluster build has failed.",
        "failure_message": "Cyclades VMs out of limit\n"
      }
      "applications": [
        {
          "name": "project.jar"
          "started": true,
          "type": "BATCH",
          "id": "eb9b1cda-1c81-4850-92f3-897b01d4685c"
        }
      ]
    }
  ]
}
```

In this example we are going to get only the status details of the lambda instance with id 3f763964-d519-4fd2-916d-b5cfbe3b878b

The request in curl

```
curl -X GET -H "Authorization: Token tJ3b3f32f23ceuqdoS_TH7m0d6yxmlWL1r2ralKcttY" 'https://<hostname>/api/lambda-instances/3f763964-d519-4fd2-916d-b5cfbe3b878b/?filter=status'
```


### Response body

If the authentication token is correct, a sample response is

```
{
  "status": {
    "short_description": "Lambda instance details.",
    "code": 200
  },
  "data": [
    {
      "status": {
        "message": "CLUSTER_FAILED",
        "code": "11",
        "details": "~okeanos cluster build has failed.",
        "failure_message": "Cyclades VMs out of limit\n"
      },
      "id": "3f763964-d519-4fd2-916d-b5cfbe3b878b",
      "name": "My first Lambda Instance"
    }
  ]
}
```

For the case where the authentication token is not correct, refer to [Authentication page](Authentication.md).

### Response messages

The main response messages are:

- HTTP/1.1 200 OK : (Success)
- HTTP/1.1 401 UNAUTHORIZED : (Fail)
- HTTP/1.1 404 NOT FOUND : (Fail)
