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
  "status": {
    "short_description": "Applications.",
    "code": 200
  },
  "data": [
    {
      "name": "project.jar",
      "id": "68e836e2-2ea4-4bb8-8b46-dcef869b3f08"
    },
    {
      "name": "test_file",
      "id": "1b9f7773-f19d-426d-bc29-5434844e4537"
    },
    {
      "name": "test_file_2",
      "id": "dddb18ae-5dab-4e9e-8914-3062b8853e24"
    },
    {
      "name": "test_file_3",
      "id": "b3e5d867-c882-4f5e-a5c2-75193866f44e"
    },
    {
      "name": "test_file_4",
      "id": "a5623a2e-7742-4299-8ca4-c05e811d2262"
    },
    {
      "name": "project1.jar",
      "id": "5bda8e92-6397-493d-9aeb-a2fcf67b19a4"
    },
    {
      "name": "application.jar",
      "id": "6fb97497-8d2c-45ed-bb7d-207e16b97c48"
    }
  ]
}```

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
  "data": [
    {
      "name": "test_file_3",
      "id": "b3e5d867-c882-4f5e-a5c2-75193866f44e"
    },
    {
      "name": "test_file_4",
      "id": "a5623a2e-7742-4299-8ca4-c05e811d2262"
    }
  ],
  "pagination": {
    "count": 7,
    "next": "http://<hostname>/api/apps/?limit=2&offset=5",
    "previous": "http://<hostname>/api/apps/?limit=2&offset=1"
  },
  "status": {
    "short_description": "Applications.",
    "code": 200
  }
}
```


### Response messages

The main response messages are:

- HTTP/1.1 200 OK : (Success)
- HTTP/1.1 400 BAD REQUEST : (Fail)
- HTTP/1.1 401 UNAUTHORIZED : (Fail)
