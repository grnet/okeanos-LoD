---
title: 'API | User ~okeanos projects'
description: Retrieve the ~okeanos to which the user is a member
---

# API - User ~okeanos projects - Description
User ~okeanos projects call, given an authentication token through the header Authorization,
will connect to ~okeanos service and retrieve the project to which the user is a member.
If the token is valid, the API will reply with a "200 Success" code, along with all the
project names and ids. If the token is invalid, the API will reply with a "401 Unauthorized"
error along with details regarding the error.


## Basic Parameters
|Type             | Description
|-----------------|--------------------------
| **Description** | ~okeanos projects
| **URL**         | /api/user-okeanos-projects/
| **HTTP Method** | GET
| **Security**    | Basic Authentication

### Headers

Type          | Description          | Required | Default value | Example value
------------- | -------------------- | -------- | ------------- | ----------------------------
Authorization | ~okeanos authentication token. If you have an account you may find the authentication token at (Dashboad-> API Access) https://accounts.okeanos.grnet.gr/ui/api_access. | `Yes`    | None          | Token tJ3b3f32f23ceuqdoS_..

## Example
In the following example we will request the ~okeanos projects of a specified user.

```
curl -X GET -H "Authorization:Token tJ3b3f32f23ceuqdoS_TH7m0d6yxmlWL1r2ralKcttY" 'http://<hostname>/api/user-okeanos-projects/'
```

### Response body
If the authentication token is correct then the response is

```
{
  "status": {
    "short_description": "~okeanos projects",
    "code": 200
  },
  "data": [
    {
      "id": "e9ccbc1b-81f9-4c46-9258-a579f9f0d030",
      "name": "lambda.grnet.gr"
    },
    {
      "id": "089c8bea-cc17-4d30-b35c-460b443d19c6",
      "name": "system:089c8bea-cc17-4d30-b35c-460b443d19c6"
    }
  ]
}
```

For the case where the authentication token is not correct, refer to [Authentication page](Authentication.md).

### Response messages
The main response messages are:

 - HTTP/1.1 200 OK : (Success)
 - HTTP/1.1 401 UNAUTHORIZED : (Fail)
