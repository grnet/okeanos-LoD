---
title: 'API | upload_file'
description: upload a file to the server
---

# API - upload_file - Description
This call is used to upload a file to the service-vm so that it can be used by the user to run  applications on any of the owned clusters.

## Basic Parameters

**Description**              | **URL**             | **HTTP Method** | **Security**
---------------------------- | ------------------- | --------------- | --------------------
Upload a file to the server  | /backend/user_files | PUT             | Token Authentication |
Get a list of uploaded files | /backend/user_files | GET             | Token Authentication |
Delete an uploaded file      | /backend/user_files | DELETE          | Token Authentication |

### Headers

Type          | Description          | Required | Default value | Example value
------------- | -------------------- | -------- | ------------- | -------------------------------------------
Authorization | Authentication token | `Yes`    | None          | tJ3b3f32f23ceuqdoS_TH7m0d6yxmlWL1r2ralKcttY |

### Body Parameters

Name          | Description             | Required | Default value | Example value
------------- | ----------------------- | -------- | ------------- | -------------
'file'        | file to be uploaded     | `Yes`    | None          |               |
'description' | description of the file | `No`     | None          |               |

## Example
Example upload PUT
```
curl -X PUT -H "Authorization: Token tJ3b39yg7mceuqdoS_TH7m0d6yxmlWLMDenalKcttR" -F "file=project.jar" -F "description=Science project executable" 'http://snf-670397.vm.okeanos.grnet.gr/backend/upload_file/'
```

Example upload GET
```
curl -X GET -H "Authorization: Token tJ3b39yg7mceuqdoS_TH7m0d6yxmlWLMDenalKcttR" 'http://snf-670397.vm.okeanos.grnet.gr/backend/upload_file/'
```

Example upload DELETE
```
curl -X DELETE -H "Authorization: Token tJ3b39yg7mceuqdoS_TH7m0d6yxmlWLMDenalKcttR" -F "id=15" 'http://snf-670397.vm.okeanos.grnet.gr/backend/upload_file/'
```

### Response body

```
{
  "result": "success"
}
```

### Response messages
he main response messages are:
- HTTP/1.1 200 OK : (Success)
- HTTP/1.1 401 UNAUTHORIZED : (Fail)
