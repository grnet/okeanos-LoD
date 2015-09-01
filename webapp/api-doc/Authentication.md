---
title: 'API | authentication'
description: authentication token validation
---

# API - authentication - Description
The authentication call, given an authentication token throught the header x-api-key, will  connect to the okeanos authentication service and check the validity of the given key. If the key  is valid then the api will reply with a 200 success code otherwise it will return an 401 error with  details concerning the error it had

## Basic Parameters
| **Description** | authentication token validation | | **URL**         | /backend/authentication         | | **HTTP Method** | GET                             | | **Security**    | Basic Authentication            |

### Headers

Type          | Description          | Required | Default value | Example value
------------- | -------------------- | -------- | ------------- | -------------------------------------------------
Authorization | authentication token | `Yes`    | None          | Token tJ3b3f32f23ceuqdoS_TH7m0d6yxmlWL1r2ralKcttR |

## Example
Example of simple validation of an api key

```
curl -X GET -H "Authorization:Token tJ3b3f32f23ceuqdoS_TH7m0d6yxmlWL1r2ralKcttY"
'http://<url>:<port>/backend/authenticate/'
```

### Response body
if the authentication token is correct then the response is

```
{
  "result": "success"
}
```

if the authentication token is not correct then the response is

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
