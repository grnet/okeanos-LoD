---
title: API | lambda instances count
description: Returns the number of lambda instances
---

# API - lambda instances count - Description

Lambda Instances count call, given an authentication token through the header Authorization,
will return the number of the Lambda Instances that are currently on the database and are not
destroyed, given that the token is valid. The status code of the response will be "200 Success".
If the token is invalid, the API will reply with a "401 Unauthorized" error along with details
regarding the error.

## Basic Parameters

|Type | Description
|------|-------------
| **Description** | lambda instances count
| **URL**         | /api/lambda-instances/count/  
| **HTTP Method** | GET
| **Security**    | Basic Authentication


### Headers

Type          | Description          | Required | Default value | Example value
------------- | -------------------- | -------- | ------------- | ----------------------------
Authorization | ~okeanos authentication token. If you have an account you may find the authentication token at (Dashboad-> API Access) https://accounts.okeanos.grnet.gr/ui/api_access. | `Yes`    | None          | Token tJ3b3f32f23ceuqdoS_..


## Example

In this example we are going to get the count of the lambda instances

The request in curl

```
curl -X GET -H "Authorization: Token tJ3b3f32f23ceuqdoS_TH7m0d6yxmlWL1r2ralKcttY" 'http://83.212.118.81/api/lambda-instances/count/'
```


### Response body

If the authentication token is correct then a possible response is

```
{
  "status": {
    "short_description": "Number of Lambda Instances",
    "code": 200
  },
  "data": [
    {
      "count": 2
    }
  ]
}
```

For the case where the authentication token is not correct, refer to [Authentication page](Authentication.md).

### Response messages
The main response messages are:

 - HTTP/1.1 200 OK : (Success)
 - HTTP/1.1 401 UNAUTHORIZED : (Fail)