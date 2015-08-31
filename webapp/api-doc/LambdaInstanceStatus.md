---
title: API | lambda instance status
description: returns the status of a specified lambda instance
---

# API - lambda instance status - Description

Lambda instance status call, given an authentication token through the header x-api-key, will firstly check the validity of the token. If the token is invalid, the API will reply with an 401 error. If the token is valid, the API will search for the specified lambda instance. If the specified lambda instance does not exists, the API will reply with an 404 Not found code. If the specified lambda instance exists, the API will reply with the status of it along with a 200 success code.

## Basic Parameters

Type | Description |
-------|-----------------|
**Description** | lambda instance status
**URL**         | /backend/lambda-instances/[uuid]/status
**HTTP Method** | GET
**Security**    | Basic Authentication


### Headers

Type | Description | Required | Default value | Example value |
------|-------------|----------|---------------|---------------|
x-api-key | ~okeanos authentication token. If you have an account you may find the authentication token at (Dashboad-> API Access) https://accounts.okeanos.grnet.gr/ui/api_access. | `Yes` |None| tJ3b3f32f23ceuqdoS_TH7m0d6yxmlWL1r2ralKcttY

### Parameters

Name | Description | Required | Default value | Example value |
------|-------------|----------|---------------|---------------|
uuid  | The uuid of the specified lambda instance. For more information see LambdaInstanceList page. |`Yes` |None| 3

### Keywords in response
Name | Description | Default value |
------|------------|---------------|
name | The name of the lambda instance | Lambda Instance
uuid | Unique integer identifying a lambda instance | None
id   | Unique integer used to enumerate lambda instances | Auto Increment
status | The status of lambda instance | PENDING

The possible values of the keyword status are:
STARTED, STOPPED, PENDING, STARTING, STOPING, DESTROYING, DESTROYED, SCALING_UP, SCALING_DOWN, FAILED.

## Example

In this example we are going to get the status of the lambda instance with uuid 3

The request in curl

```
    curl -kgX GET -H 'x-api-key: tJ3b3f32f23ceuqdoS_TH7m0d6yxmlWL1r2ralKcttY' -G 'http://<url>:<port>/backend/lambda-instances/3/status'
```


### Response body

If the authentication is correct, a sample response is

```
{
  "data": {
    "status": "STARTED", "id": 14, "name": "Lambda Instance 2", "uuid": 1
  }
}
```

For the case where the authentication token is not correct, refer to Authentication page.

### Response messages

The main response messages are:

- HTTP/1.1 201 OK : (Success)
- HTTP/1.1 404 NOT FOUND : (Fail)
- HTTP/1.1 401 UNAUTHORIZED : (Fail)
