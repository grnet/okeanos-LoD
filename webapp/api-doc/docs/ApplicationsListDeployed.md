---
title: API | application list deployed
description: Lists the deployed application on the lambda instance
---

# API - application list deployed - Description

application list deployed call, given an authentication token through the header Authorization,
will firstly check the validity of the token. If the token is invalid, the API will reply
with a "401 Unauthorized" code. If the token is valid, the API will check if the specified lambda instance exists. If it doesn't, the API will response with a "404 Not Found" code. If the specified lambda instance exists, the API will return all the applications deployed on that lambda instance in JSON format along with a "200 OK" code. If there are no lambda instances the array of the returned applications will be empty. Applications can be viewed in pages with a specified number of instances per page. This is possible by specifying the "limit" and "offset" GET variables on the URL of the call(offset can be ommited). If "offset" is specified without "limit", or has a zero or negative value, it will be ignored. If "limit" is less than zero, the API will reply with a "400 Bad Request" code.

## Basic Parameters

|Type | Description
------|-------------
**Description** | application list deployed
**URL**         | /api/apps/[lambda-instance-id]/
**HTTP Method** | GET
**Security**    | Basic Authentication


### Headers

Type  | Description | Required | Default value | Example value
----------|-------------|----------|---------------|---------------
Authorization | ~okeanos authentication token. If you have an account you may find the authentication token at (Dashboad-> API Access) https://accounts.okeanos.grnet.gr/ui/api_access. | `Yes` | None | Token tJ3b3f32f23ceuqdoS_..



### Parameters

Name | Description | Required | Default value | Example value
------|-------------|----------|---------------|---------------
lambda-instance-id  | The id of the lambda instance |`Yes` |None|


## Example

In this example we are going to list all the deployed application on the lambda instance
with id 9ac8e7ab-57f9-48a6-af18-ef8a749b1e8c

The request in curl

```
curl -X GET -H "Authorization: Token tJ3b3f32f23ceuqdoS_TH7m0d6yxmlWL1r2ralKcttY" 'http://<hostname>/api/apps/9ac8e7ab-57f9-48a6-af18-ef8a749b1e8c/list-deployed/'
```


### Response body

If the authentication token is correct, a sample response would be

```
{
  "status": 200,
  "data": [
    {
      "name": "test_file_5",
      "path": "lambda_applications",
      "description": "My first application.",
      "status": "UPLOADED",
      "code": "0",
      "id": "d2e00532-d643-434c-9717-cd923a77f331"
    },
    {
      "name": "test_big",
      "path": "lambda_applications",
      "description": "My first application.",
      "status": "UPLOADED",
      "code": "0",
      "id": "7186be3f-22ca-4e59-8e5f-fc381e92a67c"
    },
    {
      "name": "test_file",
      "path": "lambda_applications",
      "description": "My first application.",
      "status": "UPLOADED",
      "code": "0",
      "id": "7c177dc2-4196-4b6e-ad43-4e316273ec39"
    },
    {
      "name": "test_file_1",
      "path": "lambda_applications",
      "description": "My first application.",
      "status": "UPLOADED",
      "code": "0",
      "id": "4abe753e-84b8-43f5-9f1e-b97b120609f8"
    }
  ]
}
```

For the case where the authentication token is not correct, refer to [Authentication page](Authentication.md).

In this example we are going to list a limit of 2 applications, starting from the third
application that are deployed on the lambda instance with id 9ac8e7ab-57f9-48a6-af18-ef8a749b1e8c

The request in curl

```
curl -X GET -H "Authorization: Token tJ3b3f32f23ceuqdoS_TH7m0d6yxmlWL1r2ralKcttY" 'http://<hostname>/api/apps/9ac8e7ab-57f9-48a6-af18-ef8a749b1e8c/list-deployed/?limit=2&offset=3'
```

If the authentication token is correect, a sample response would be

```
{
  "count": 4,
  "next": null,
  "previous": "http://83.212.118.182/api/apps/9ac8e7ab-57f9-48a6-af18-ef8a749b1e8c/list-deployed/?limit=2&offset=1",
  "data": [
    {
      "name": "test_file_1",
      "path": "lambda_applications",
      "description": "My first application.",
      "status": "UPLOADED",
      "code": "0",
      "id": "4abe753e-84b8-43f5-9f1e-b97b120609f8"
    }
  ],
  "status": 200
}
```

### Response messages

The main response messages are:

- HTTP/1.1 202 ACCEPTED : (Success)
- HTTP/1.1 401 UNAUTHORIZED : (Fail)
- HTTP/1.1 404 NOT FOUND : (Fail)
