---
title: API | lambda instances list
description: Lists all lambda instances
---

# API - lambda instances list - Description

Lambda instances list call, given an authentication token through the header Authorization,
will firstly check the validity of the token. If the token is invalid, the API will reply
with a "401 Unauthorized" code. If the token is valid, the API will return all the lambda
instances in JSON format along with a "200 OK" code. If there are no lambda instances the array
of the returned lambda instances will be empty. Lambda instances can be viewed in pages with
a specified number of instances per page. This is possible by specifying the "limit" and "offset"
GET variables on the URL of the call(offset can be ommited). If "offset" is specified without
"limit", or has a zero or negative value, it will be ignored. If "limit" is less than zero, the API
will reply with a "400 Bad Request" code.


## Basic Parameters

Type            | Description
----------------|--------------------------
**Description** | lambda instances list
**URL**         | /api/lambda-instances/
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
name  | The name of the lambda instance | Lambda Instance
id  | Unique key identifying a lambda instance | None
status | The status code of the response | None
next | The URL to be used to list the next lambda instance | null
previous | The URL to be used to list the previous lambda instance | null
count | The number of existing lambda instances | None

## Example

In this example we are going to list all the available lambda instances.

The request in curl

```
curl -X GET -H "Authentication:Token tJ3b3f32f23ceuqdoS_TH7m0d6yxmlWL1r2ralKcttY" 'http://<hostname>/api/lambda-instances/'
```


### Response body

If the authentication token is correct, a sample response is


```
{
  "status": {
    "short_description": "Lambda instances.",
    "code": 200
  },
  "data": [
    {
      "name": "My first Lambda Instance",
      "id": "9ac8e7ab-57f9-48a6-af18-ef8a749b1e8c"
    },
    {
      "name": "Lambda Instance 1",
      "id": "bc206a2a-b220-43e5-9d76-a7774de5c377"
    },
    {
      "name": "Lambda Instance 2",
      "id": "b141f48c-787b-4345-af6d-1e2e84a45c7e"
    },
    {
      "name": "Lambda Instance 3",
      "id": "8d8b574b-742e-4b90-9926-3c034dc40516"
    },
    {
      "name": "Lambda Instance 4",
      "id": "bbe29514-4f21-4960-89b3-becd82515ef3"
    }
  ]
}
```

For the case where the authentication token is not correct, refer to [Authentication page](Authentication.md).

In this example we are going to list a limit of 2 lambda instances, starting from the third lambda instance.

The request in curl

```
curl -X GET -H "Authentication:Token tJ3b3f32f23ceuqdoS_TH7m0d6yxmlWL1r2ralKcttY" 'http://<hostname>/backend/lambda-instances/?limit=2&offset=3'
```

If the authentication token is correct, a sample response is

```
{
  "pagination": {
    "count":5,
    "next":null,
    "previous":"http://<hostname>/api/lambda-instances/?limit=2&offset=1",
  },
  "data":[
    {"name":"Lambda Instance 3","id":"8d8b574b-742e-4b90-9926-3c034dc40516"},
    {"name":"Lambda Instance 4","id":"bbe29514-4f21-4960-89b3-becd82515ef3"}
  ],
  "status": {
    "short_description": "Lambda instances.",
    "code": 200
  }
}
```

### Response messages

The main response messages are:

- HTTP/1.1 200 OK : (Success)
- HTTP/1.1 400 BAD REQUEST : (Fail)
- HTTP/1.1 401 UNAUTHORIZED : (Fail)
