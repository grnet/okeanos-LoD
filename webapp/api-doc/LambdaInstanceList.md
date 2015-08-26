---
title: API | lambda instances list
description: lists all lambda instances
---

# API - lambda instances list - Description

The lambda instances list call, given an authentication token through the header x-api-key,
will firstly check the validity of the token. If the token is invalid, the API will reply
with an 401 error. If the token is valid, the API will list retrieve all the lambda
instances from the database and return them in json format allong with a 200 success code.
If there are no lambda instances on the database the API will reply with a 404 no instances
found code.

## Basic Parameters

| **Description** | lambda instances list       |
| **URL**         | /backend/lambda-instances   |
| **HTTP Method** | GET                         |
| **Security**    | Basic Authentication        |


### Headers

Type | Description | Required | Default value | Example value |
------|-------------|----------|---------------|---------------|
x-api-key | authentication token | `Yes` |None| tJ3b3f32f23ceuqdoS_TH7m0d6yxmlWL1r2ralKcttY


### Parameters

Name | Description | Required | Default value | Example value |
------|-------------|----------|---------------|---------------|
limit  | number of lambda instances on each page |`No` |None| 3
page   | the number of the page to return | `No` |None| 2


## Example

In this example we are going to list all the available lambda instances

The request in curl

<pre><code>
    curl -kgX GET -H 'x-api-key: tJ3b3f32f23ceuqdoS_TH7m0d6yxmlWL1r2ralKcttY' -G 'http://<url>:<port>/backend/lambda-instances'
</code></pre>


### Response body

If the authentication token is correct, a sample response is

<pre><code>
{
  "data": [
    {"uuid": 1, "name": "Physics Lambda Instance", "id": 1},
    {"uuid": 2, "name": "Machine Learning Lambda Instance", "id": 3},
    {"uuid": 3, "name": "Another Lambda Instance", "id": 4},
    {"uuid": 4, "name": "Lambda Instance", "id": 5},
    {"uuid": 5, "name": "Lambda Instance for students", "id": 7},
  ]
}
</code></pre>

If the authentication token is not correct, then the response is

<pre><code>
{
  "errors": [
    {
      "unauthorized": {
        "message": "Invalid token",
        "code": 401,
        "details": ""
      }
    }
  ]
}
</code></pre>

In this example we are going to list the 2nd page of the lambda instances with a limit of 2
lambda instance in each page.

<pre><code>
    curl -kgX GET -H 'x-api-key: tJ3b3f32f23ceuqdoS_TH7m0d6yxmlWL1r2ralKcttY' -G 'http://<url>:<port>/backend/lambda-instances/?limit=2&page=2'
</code></pre>

If the authentication token is correct, a sample response is

<pre><code>
{
  "data": [
    {"uuid": 3, "name": "Another Lambda Instance", "id": 4},
    {"uuid": 4, "name": "Lambda Instance", "id": 5},
  ]
}
</code></pre>

### Response messages

The main response messages are:

- HTTP/1.1 201 OK : (Success)
- HTTP/1.1 404 NO INSTANCES FOUND : (Fail)
- HTTP/1.1 401 UNAUTHORIZED : (Fail)
- HTTP/1.1 500 ZERO OR NEGATIVE INDEXING IS NOT SUPPORTED : (Fail)
