---
title: 'API | authentication'
description: authentication token validation
---

# API - authentication - Description
The authentication call, given an authentication token through the header Authorization, will
connect to the ~okeanos authentication service and check the validity of the given token. If
the token is valid then the API will reply with a "200 Success" code, otherwise it will return
an "401 Unauthorized" error along with details regarding the error.

## Basic Parameters
|Type             | Description
|-----------------|--------------------------
| **Description** | Authentication token validation
| **URL**         | /api/authenticate/
| **HTTP Method** | GET
| **Security**    | Basic Authentication

### Headers

Type          | Description          | Required | Default value | Example value
------------- | -------------------- | -------- | ------------- | ----------------------------
Authorization | ~okeanos authentication token. If you have an account you may find the authentication token at (Dashboad-> API Access) https://accounts.okeanos.grnet.gr/ui/api_access. | `Yes`    | None          | Token tJ3b3f32f23ceuqdoS_..

## Example
Example of simple validation of an API token

```
curl -X GET -H "Authorization:Token tJ3b3f32f23ceuqdoS_TH7m0d6yxmlWL1r2ralKcttY" \
 'https://<hostname>/api/authenticate/'
```

### Response body
If the authentication token is correct then the response is

```
{
  "status": 200,
  "result": "Success",
  "data": {"name":"Lambda User"}
}
```

If the authentication token is not correct then the response is

```
{
  "errors": [
    {
      "message": "Invalid token",
      "code": 401,
      "details": "unauthorized"
    }
  ]
}
```

### Response messages
The main response messages are:

 - HTTP/1.1 200 OK : (Success)
 - HTTP/1.1 401 UNAUTHORIZED : (Fail)
