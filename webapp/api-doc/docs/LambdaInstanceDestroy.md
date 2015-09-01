---
title: API | lambda instance destroy
description: Destroys a specified lambda instance
---

# API - lambda instance destroy - Description

[A descriptive paragraph about the call]
Lambda instance destroy call, given an authentication token through the header x-api-key,
will firstly check te validity of the token. If the token is invalid, the API wil reply with
a "401 Unauthorized" code. If the token is valid, the API will destroy all the VMs of the
specified lambda instance along with the corresponding public ip and the private network and
will also return a "202 ACCEPTED" code.

## Basic Parameters

|Type            | Description
|----------------|--------------------------
| **Description** | lambda instance destroy
| **URL**         | backend/lambda-instances/[uuid]/destroy
| **HTTP Method** | POST
| **Security**    | Basic Authentication


### Headers

Type | Description | Required | Default value | Example value 
------|-------------|----------|---------------|---------------
x-api-key | ~okeanos authentication token. If you have an account you may find the authentication token at (Dashboad-> API Access) https://accounts.okeanos.grnet.gr/ui/api_access. | `Yes` | None | tJ3b3f32f23ceuqdoS_..


### Parameters

Name | Description | Required | Default value | Example value 
------|-------------|----------|---------------|---------------
uuid  | The uuid of the specified lambda instance. For more information see [List Lambda instances page](LambdaInstanceList.md). |`Yes` |None| 3


## Example

In this example we are going to destroy the lambda instance with uuid 3

The request in curl

```
curl -X POST -H "x-api-key: tJ3b3f32f23ceuqdoS_TH7m0d6yxmlWL1r2ralKcttY" 'http://<url>/backend/lambda-instances/3/destroy'
```


### Response body

If the authentication is correct the response will be

```
{
  "result": "Success"
}
```

For the case where the authentication token is not correct, refer to [Authentication page](Authentication.md).

### Response messages

The main response messages are:

- HTTP/1.1 202 ACCEPTED : (Success)
- HTTP/1.1 401 UNAUTHORIZED : (Fail)
