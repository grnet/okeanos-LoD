---
title: API | application delete
description: Delete an uploaded application
---

# API - application delete - Description

Application delete call, given an authentication token through the header authentication,
will firstly check the validity of the token. If the token is invalid, the API will reply with
a "401 Unauthorized" code. If the token is valid, the API will search for the specified
application. If the specified application does not exist, the API will reply with a
"404 Not Found" code. If the specified application exists, the API will reply with a
"202 ACCEPTED" code and will start deleting the specified application from Pithos.

## Basic Parameters

|Type | Description
------|-------------
**Description** | application delete
**URL**         | /api/apps/[application-id]/
**HTTP Method** | DELETE
**Security**    | Basic Authentication


### Headers

Type | Description | Required | Default value | Example value
------|-------------|----------|---------------|---------------
Authorization | ~okeanos authentication token. If you have an account you may find the authentication token at (Dashboad-> API Access) https://accounts.okeanos.grnet.gr/ui/api_access. | `Yes` | None | Token tJ3b3f32f23ceuqdoS_..


### Parameters

Name | Description | Required | Default value | Example value
------|-------------|----------|---------------|---------------
application-id  | The id of the specified application. For more information see [List Applications](ApplicationsList.md). |`Yes` |None| 3f763964-d519-4fd2-916d-b5cfbe3b878b


## Example

In this example we are going to delete the application with id 84dfb596-3abb-401e-99fc-c6f0057dedab

The request in curl

```
curl -X DELETE -H "Authorization: Token tJ3b3f32f23ceuqdoS_TH7m0d6yxmlWL1r2ralKcttY" 'http://<hostname>/api/apps/84dfb596-3abb-401e-99fc-c6f0057dedab/'
```


### Response body

```
{
  "status": {
    "short-description": "Your request to delete the specified application has been accepted.",
    "code": 202
  }
}
```

### Response messages

The main response messages are:

- HTTP/1.1 201 OK : (Success)
- HTTP/1.1 401 UNAUTHORIZED : (Fail)
- HTTP/1.1 404 NOT FOUND : (Fail)
