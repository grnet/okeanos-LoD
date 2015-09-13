---
title: API | applications list
description: Lists all applications
---

# API - applications list - Description

Applications list call, given an authentication token through the header Authorization,
will firstly check the validity of the token. If the token is invalid, the API will reply
with a "401 Unauthorized" code. If the token is valid, the API will return all the applications in JSON format along with a "200 OK" code. If there are no applications the array
of the returned applications will be empty. Applications can be viewed in pages with
a specified number of them per page. This is possible by specifying the "limit" and "offset"
GET variables on the URL of the call(offset can be ommited). If "offset" is specified without
"limit", or has a zero or negative value, it will be ignored. If "limit" is less than zero, the API
will reply with a "400 Bad Request" code.

## Basic Parameters

|Type | Description
------|-------------
**Description** | applications list
**URL**         | /api/apps/
**HTTP Method** | GET
**Security**    | Basic Authentication


### Headers

Type  | Description | Required | Default value | Example value
----------|-------------|----------|---------------|---------------
Authorization | ~okeanos authentication token. If you have an account you may find the authentication token at (Dashboad-> API Access) https://accounts.okeanos.grnet.gr/ui/api_access. | `Yes` | None | Token tJ3b3f32f23ceuqdoS_..


### Parameters

Name   | Description | Required | Default value | Example value
-------|-------------|----------|---------------|---------------
limit  | number of lambda instances on each page | `No` | None | 3
offset   | the first lambda instance of the page | `No` | None | 2


### Keywords in response
Name  | Description | Default value
------|------------|---------------
name  | The name of the application | None
id  | Unique key identifying a lambda i | None
status | The status code of the response | None
next | The URL to be used to list the next lambda instance | null
previous | The URL to be used to list the previous lambda instance | null
count | The number of existing lambda instances | None
description | The description of the application | None
path | The path on Pithos where the application is saved |


## Example

In this example we are going to list all the available applications.

The request in curl

```
curl -X GET -H "Authorization: Token tJ3b3f32f23ceuqdoS_TH7m0d6yxmlWL1r2ralKcttY" 'http://<hostname>/api/apps/'
```


### Response body

If the authentication token is correct, a sample response is


```
{
  "status": 200,
  "data": [
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
    },
    {
      "name": "test_file_2",
      "path": "lambda_applications",
      "description": "My first application.",
      "status": "UPLOADED",
      "code": "0",
      "id": "99bb434c-e50e-4ca8-9f5e-0825fef09c92"
    },
    {
      "name": "test_file_3",
      "path": "lambda_applications",
      "description": "My first application.",
      "status": "UPLOADED",
      "code": "0",
      "id": "a1e21dec-475d-4e56-9763-3e42e2c61935"
    },
    {
      "name": "test_file_4",
      "path": "lambda_applications",
      "description": "My first application.",
      "status": "UPLOADED",
      "code": "0",
      "id": "56bfd480-e5a3-44b0-b111-e4a6be6c93cf"
    },
    {
      "name": "test_file_5",
      "path": "lambda_applications",
      "description": "My first application.",
      "status": "UPLOADED",
      "code": "0",
      "id": "d2e00532-d643-434c-9717-cd923a77f331"
    }
  ]
}
```

For the case where the authentication token is not correct, refer to [Authentication page](Authentication.md).

In this example we are going to list a limit of 2 applications, starting from the third
application.

The request in url

```
curl -X GET -H "Authorization: Token tJ3b3f32f23ceuqdoS_TH7m0d6yxmlWL1r2ralKcttY" 'http://<hostname>/api/apps/?limit=2&offset=3'
```

If the authentication token is correct, a sample response is

```
{
  "count": 7,
  "next": "http://83.212.118.182/api/apps/?limit=2&offset=5",
  "previous": "http://83.212.118.182/api/apps/?limit=2&offset=1",
  "data": [
    {
      "name": "test_file_2",
      "path": "lambda_applications",
      "description": "My first application.",
      "status": "UPLOADED",
      "code": "0",
      "id": "99bb434c-e50e-4ca8-9f5e-0825fef09c92"
    },
    {
      "name": "test_file_3",
      "path": "lambda_applications",
      "description": "My first application.",
      "status": "UPLOADED",
      "code": "0",
      "id": "a1e21dec-475d-4e56-9763-3e42e2c61935"
    }
  ],
  "status": 200
}
```


### Response messages

The main response messages are:

- HTTP/1.1 200 OK : (Success)
- HTTP/1.1 400 BAD REQUEST : (Fail)
- HTTP/1.1 401 UNAUTHORIZED : (Fail)
