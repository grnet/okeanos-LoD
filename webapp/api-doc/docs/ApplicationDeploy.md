---
title: API | application deploy
description: Deploys an application on a specified lambda instance.
---

# API - application deploy - Description

Application deploy call, given an authentication token through the header Authorization,
will firstly check the validity of the token. If the token is invalid, the API will reply
with a "401 Unauthorized" code. If the token is valid, the API will check if the lambda instance and the application exist. If any of these two doesn't exist, the API will reply with a "404 Not Found" code. If both the application and the lambda instance exist the API
will reply with a "202 Accepted" code and will start deploying the specified application on the specified lambda instance.

## Basic Parameters

|Type | Description
------|-------------
| **Description** | application deploy
| **URL**         | /api/apps/[application-id]/deploy/
| **HTTP Method** | POST
| **Security**    | Basic Authentication


### Headers

Type  | Description | Required | Default value | Example value
----------|-------------|----------|---------------|---------------
Authorization | ~okeanos authentication token. If you have an account you may find the authentication token at (Dashboad-> API Access) https://accounts.okeanos.grnet.gr/ui/api_access. | `Yes` | None | Token tJ3b3f32f23ceuqdoS_..


### Parameters

Name | Description | Required | Default value | Example value
------|-------------|----------|---------------|---------------
application-id  | The id of the application to be deployed |`Yes` |None| 3f763964-d519-4fd2-916d-b5cfbe3b878b
lambda-instance-id | The id of the lambda instance on which the application will be deployed |`Yes`| None| 3f763964-d519-4fd2-916d-b5cfbe3b878b


## Example

In this example we are going to deploy the application with id 7186be3f-22ca-4e59-8e5f-fc381e92a67c on the lambda instance with id
9ac8e7ab-57f9-48a6-af18-ef8a749b1e8c

The request in curl

```
curl -X POST -H "Authorization: Token tJ3b3f32f23ceuqdoS_TH7m0d6yxmlWL1r2ralKcttY" -F "lambda_instance_id=9ac8e7ab-57f9-48a6-af18-ef8a749b1e8c" 'http://<hostname>/api/apps/7186be3f-22ca-4e59-8e5f-fc381e92a67c/deploy/'
```


### Response body

If the authentication token is correct, the response will be

```
{
  "status": {
    "short-description": "Your request to deploy the specified application has been accepted.",
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
