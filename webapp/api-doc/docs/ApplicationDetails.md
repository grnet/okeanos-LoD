---
title: API | application details
description: Returns the details of a specified application
---

# API - application details - Description

Application details call, given an authentication token through the header authentication,
will firstly check the validity of the token. If the token is invalid, the API will reply with a
"401 Unauthorized" code. If the token is valid, the API will search for the specified application. If the specified application does not exist, the API will reply with a
"404 Not Found" code. If the specified application exists, the API will reply with the details
of it along with a "200 OK" code.


## Basic Parameters

|Type | Description
------|-------------
| **Description** | Details of an application
| **URL**         | /api/apps/[application-id]/
| **HTTP Method** | GET
| **Security**    | Basic Authentication


### Headers

Type | Description | Required | Default value | Example value
------|-------------|----------|---------------|---------------
Authorization | ~okeanos authentication token. If you have an account you may find the authentication token at (Dashboad-> API Access) https://accounts.okeanos.grnet.gr/ui/api_access. | `Yes` | None | Token tJ3b3f32f23ceuqdoS


### Parameters

Name  | Description | Required | Default value | Example value
------|-------------|----------|---------------|---------------
application-id  | The id of the specified lambda application. For more information see [List applications page](ApplicationsList.md) . |`Yes` |None| eb9b1cda-1c81-4850-92f3-897b01d4685c


## Example

In this example we are going to get the details of the application with id eb9b1cda-1c81-4850-92f3-897b01d4685c

The request in curl

```
curl -X GET -H "Authorization: Token tJ3b3f32f23ceuqdoS_TH7m0d6yxmlWL1r2ralKcttY" \
'https://<hostname>/api/apps/eb9b1cda-1c81-4850-92f3-897b01d4685c/'
```


### Response body

```
{
  "status": {
    "short_description": "Application details",
    "code": 200
  },
  "data": [
    {
      "name": "test_file_1",
      "path": "lambda_applications",
      "type": "BATCH",
      "description": "My first application",
      "status": {
        "message": "UPLOADED",
        "code": "0",
        "detail": "Application has been successfully uploaded."
      },
      "lambda_instances": [
        {
          "started": false,
          "id": "3bc97580-45e1-4c39-90ae-0c2178431526",
          "name": "My first Lambda Instance"
          "status": {
            "message": "STARTED",
            "code": "0",
            "detail": "Lambda instance has been started"
          },
        }
      ],
      "id": "eb9b1cda-1c81-4850-92f3-897b01d4685c"
    }
  ]
}
```


### Response messages

The main response messages are:

- HTTP/1.1 200 OK : (Success)
- HTTP/1.1 401 UNAUTHORIZED : (Fail)
- HTTP/1.1 404 NOT FOUND : (Fail)
