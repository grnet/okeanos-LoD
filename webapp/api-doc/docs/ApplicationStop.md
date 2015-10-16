---
title: API | application stop
description: Stops an application on a specified lambda instance
---

# API - application stop - Description

Application stop call, given an authentication token through the header Authorization,
will firstly check the validity of the token. If the token is invalid, the API will reply
with a "401 Unauthorized" code. If the token is valid, the API will check if the lambda instance and the application exist, and if the application is deployed on the instance. If any of these conditions is not met, the API will reply with a "404 Not Found" code. If the application has already been stopped on the specified lambda instance, or the respective job type slot on the lambda instance is free, the API will reply with a "409 Conflict" code. If the application is deployed on the lambda instance, has not been stopped, and its job slot is occupied, the API
will reply with a "202 Accepted" code and will stop the application on the lambda instance.

## Basic Parameters

Type | Description |
-------|-----------------|
**Description** | application stop
**URL**         | /api/apps/[application-id]/stop/
**HTTP Method** | POST
**Security**    | Basic Authentication


### Headers

Type  | Description | Required | Default value | Example value
----------|-------------|----------|---------------|---------------
Authorization | ~okeanos authentication token. If you have an account you may find the authentication token at (Dashboad-> API Access) https://accounts.okeanos.grnet.gr/ui/api_access. | `Yes` | None | Token tJ3b3f32f23ceuqdoS_..


### Parameters

Name | Description | Required | Default value | Example value
------|-------------|----------|---------------|---------------
application-id  | The id of the application to be stopped | `Yes` | None |7186be3f-22ca-4e59-8e5f-fc381e92a67c
lambda-instance-id | The id of the lambda instance on which the application will be stopped | `Yes` | None |9ac8e7ab-57f9-48a6-af18-ef8a749b1e8c


## Example

In this example we are going to stop the application with id 7186be3f-22ca-4e59-8e5f-fc381e92a67c on the lambda instance with id
9ac8e7ab-57f9-48a6-af18-ef8a749b1e8c

The request in curl

```
curl -X POST -H "Authorization: Token tJ3b3f32f23ceuqdoS_TH7m0d6yxmlWL1r2ralKcttY" -F "lambda_instance_id=9ac8e7ab-57f9-48a6-af18-ef8a749b1e8c" 'http://<hostname>/api/apps/7186be3f-22ca-4e59-8e5f-fc381e92a67c/stop/'
```


### Response body

If the authentication token is correct, the response will be

```
{
  "status": {
    "short-description": "Your request to stop the specified application has been accepted",
    "code": 202
  }
}
```


For the case where the authentication token is not correct, refer to [Authentication page](Authentication.md).


### Response messages

The main response messages are:

- HTTP/1.1 202 ACCEPTED : (Success)
- HTTP/1.1 401 UNAUTHORIZED : (Fail)
- HTTP/1.1 404 NOT FOUND : (Fail)
- HTTP/1.1 409 CONFLICT : (Fail)
