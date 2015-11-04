---
title: API | application upload
description: Upload an application
---

# API - application upload - Description

Application upload call, given an authentication token through the header authentication,
will firstly check the validity of the token. If the token is invalid, the API will reply with
a "401 Unauthorized" code. If the token is valid, the API will reply with a "202 ACCEPTED" code
and will start uploading the provided application to Pithos+.

## Basic Parameters

|Type | Description
------|-------------
**Description** | Upload an application
**URL**         | api/apps/
**HTTP Method** | POST
**Security**    | Basic Authentication


### Headers

Type | Description | Required | Default value | Example value
------|-------------|----------|---------------|---------------
Authorization | ~okeanos authentication token. If you have an account you may find the authentication token at (Dashboad-> API Access) https://accounts.okeanos.grnet.gr/ui/api_access. | `Yes` | None | Token tJ3b3f32f23ceuqdoS_..


### Parameters

Name | Description | Required | Default value | Example value
------|-------------|----------|---------------|---------------
description  | A description of the application | `No` |None|
file | The application file | `Yes` | None
type | The application type (batch/streaming) | `Yes` | None
project_name | The ~okeanos project name that has the needed quotas on Pithos+ | `No` | None


## Example

In this example we are going to upload an application with description "My application", file
name "test_project" and project name "lambda.grnet.gr".

The request in curl

```
curl -X POST -H "Authorization:Token tJ3b3f32f23ceuqdoS_TH7m0d6yxmlWL1r2ralKcttY" \
 -F "description=My application"  \
 -F "file=@batch-1.0-jar-with-dependencies.jar" \
 -F "type=batch" \
 -F "project_name=lambda.grnet.gr" \
 -F "execution_environment_name=Batch" \
 'https://<hostname>/api/apps/'
```


### Response body

If the authentication token is correct, a sample response would be

```
{
  "status": {
    "short_description": "Your request to upload the specified application has been accepted",
    "code": 202
  },
  "data": [
    {
      "id": "84dfb596-3abb-401e-99fc-c6f0057dedab",
      "links": {
        "self": "https://<hostname>/api/apps/84dfb596-3abb-401e-99fc-c6f0057dedab"
      }
    }
  ]
}
```

For the case where the authentication token is not correct, refer to [Authentication page](Authentication.md).

### Response messages

The main response messages are:

- HTTP/1.1 201 OK : (Success)
- HTTP/1.1 400 BAD REQUEST : (Fail)
- HTTP/1.1 401 UNAUTHORIZED : (Fail)
