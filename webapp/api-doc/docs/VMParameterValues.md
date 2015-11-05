---
title: 'API | VM parameter values'
description: Retrieve the ~okeanos to which the user is a member
---

# API - VM parameter values - Description
VM parameter values call, given an authentication token through the header Authorization, will connect to ~okeanos service and retrieve the allowed values
of the parameters for creating a VM on ~okeanos. If the token is valid, the API will reply with a "200 Success" code along with all the available values. If the token is
invalid, the API will reply with a "401 Unauthorized" error along with details regarding the error.


## Basic Parameters
|Type             | Description
|-----------------|--------------------------
| **Description** | Get VM parameter values.
| **URL**         | /api/vm-parameter-values/
| **HTTP Method** | GET
| **Security**    | Basic Authentication

### Headers

Type          | Description          | Required | Default value | Example value
------------- | -------------------- | -------- | ------------- | ----------------------------
Authorization | ~okeanos authentication token. If you have an account you may find the authentication token at (Dashboad-> API Access) https://accounts.okeanos.grnet.gr/ui/api_access. | `Yes`    | None          | Token tJ3b3f32f23ceuqdoS_..

## Example
In the following example we will fetch all the allowed values of the parameters
for creating a VM on ~okeanos.

```
curl -X GET -H "Authorization:Token tJ3b3f32f23ceuqdoS_TH7m0d6yxmlWL1r2ralKcttY" \
'https://<hostname>/api/vm-parameter-values/'
```

### Response body
If the authentication token is correct then the response is

```
{
  "status": {
    "short_description": "Allowed values of parameters for creating a Lambda Instance",
    "code": 200
  },
  "data": [
    {
      "disk": [
        5,
        10,
        20,
        40,
        60
      ],
      "vcpus": [
        1,
        2,
        4,
        8
      ],
      "ram": [
        512,
        1024,
        2048,
        4096,
        6144,
        8192
      ]
    }
  ]
}
```

For the case where the authentication token is not correct, refer to [Authentication page](Authentication.md).

### Response messages
The main response messages are:

 - HTTP/1.1 200 OK : (Success)
 - HTTP/1.1 401 UNAUTHORIZED : (Fail)
