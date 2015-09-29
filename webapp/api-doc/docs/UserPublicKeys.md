---
title: 'API | User Public Keys'
description: Retrieve user's public keys from okeanos account
---

# API - User Public Keys - Description
The User public keys call, given an authentication token through the header Authorization, will
connect to the ~okeanos service and retrieve the user's saved public keys. If
the token is valid then the API will reply with a "200 Success" code, along with all the user's
public keys and the names that has been assigned to them. if the token is invalid it will return
an "401 Unauthorized" error along with details regarding the error.

## Basic Parameters
|Type             | Description
|-----------------|--------------------------
| **Description** | authentication token validation
| **URL**         | /api/user-public-keys/
| **HTTP Method** | GET
| **Security**    | Basic Authentication

### Headers

Type          | Description          | Required | Default value | Example value
------------- | -------------------- | -------- | ------------- | ----------------------------
Authorization | ~okeanos authentication token. If you have an account you may find the authentication token at (Dashboad-> API Access) https://accounts.okeanos.grnet.gr/ui/api_access. | `Yes`    | None          | Token tJ3b3f32f23ceuqdoS_..

## Example
Example of simple validation of an API token

```
curl -X GET -H "Authorization:Token tJ3b3f32f23ceuqdoS_TH7m0d6yxmlWL1r2ralKcttY" 'http://<hostname>/api/user-publickeys/'
```

### Response body
If the authentication token is correct then the response is

```
{
  "status": {
    "short_description": "Public keys uploaded to ~okeanos.",
    "code": 200
  },
  "data": [
    {
      "content": "ssh-rsa gfadsgdssAfadsds...",
      "fingerprint": "FC:ds:...",
      "id": 1000,
      "name": "key-1",
      "uri": "/userdata/keys/1000"
    },
  ]
}
```

For the case where the authentication token is not correct, refer to [Authentication page](Authentication.md).

### Response messages
The main response messages are:

 - HTTP/1.1 200 OK : (Success)
 - HTTP/1.1 401 UNAUTHORIZED : (Fail)
