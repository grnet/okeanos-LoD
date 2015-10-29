---
title: API | lambda instance action
description: Performs a specified action on a specified lambda instance
---

# API - lambda instance action - Description

Lambda instance action call, given an authentication token through the header authentication,
will firstly check the validity of the token. If the token is invalid, the API will reply with
a "401 Unauthorized" code. If the token is valid, the API will search for the specified lambda
instance. If the specified lambda instance does not exist, the API will reply with a
"404 Not Found" code. If the specified lambda instance exists, the API will reply with a
"202 ACCEPTED" code and will also begin to perform the specified action on the specified
lambda instance. The available actions are start and stop.

## Basic Parameters
Type | Description
-------|-----------------
**Description** | Start or stop a specified lambda instance 
**URL**         | api/lambda-instances/[lambda-instance-id]/
**HTTP Method** | POST
**Security**    | Basic Authentication


### Headers

Type | Description | Required | Default value | Example value
------|-------------|----------|---------------|---------------
Authorization | ~okeanos authentication token. If you have an account you may find the authentication token at (Dashboad-> API Access) https://accounts.okeanos.grnet.gr/ui/api_access. | `Yes` | None | Token tJ3b3f32f23ceuqdoS_..


### Parameters

Name | Description | Required | Default value | Example value
------|-------------|----------|---------------|---------------
lambda-instance-id  | The id of the specified lambda instance. For more information see [List Lambda instances page](LambdaInstancesList.md). |`Yes` |None| 3
action | The action to perform on the lambda instance | `Yes` | None | start


## Example

In this example we are going to start the lambda instance with id 9ac8e7ab-57f9-48a6-af18-ef8a749b1e8c

The request in curl

```
curl -X POST -H "Authentication:Token tJ3b3f32f23ceuqdoS_TH7m0d6yxmlWL1r2ralKcttY" \
 -F "action=start" \
 'http://<hostname>/api/lambda-instances/9ac8e7ab-57f9-48a6-af18-ef8a749b1e8c/'
```


### Response body

If the authentication is correct the response will be

```
{
  "status": {
    "code": 202,
    "short-description": "Your request has been accepted"
  }
}
```

For the case where the authentication token is not correct, refer to [Authentication page](Authentication.md).

### Response messages

The main response messages are:

- HTTP/1.1 202 ACCEPTED : (Success)
- HTTP/1.1 401 UNAUTHORIZED : (Fail)
- HTTP/1.1 404 NOT FOUND : (Fail)
