---
title: API | upload_file 
description: upload a file to the server
---

# API - upload_file - Description 

This call is used to upload a file to the service-vm so that it can be used by the user to run 
applications on any of the owned clusters.

## Basic Parameters 

| **Description** | upload a file to the server |
| **URL**         | /backend/upload_file        |
| **HTTP Method** | POST                        |
| **Security**    | Basic Authentication        |


### Headers 

Type | Description | Required | Default value | Example value |
------|-------------|----------|---------------|---------------|
x-api-key | authentication token | `Yes` |None| tJ3b3f32f23ceuqdoS_TH7m0d6yxmlWL1r2ralKcttY |


### Body Parameters 

Name | Description | Required | Default value | Example value |
------|-------------|----------|---------------|---------------|
'file'  | file to be uploaded |`Yes` |        None|            |


## Example

Example of request

```
curl -X GET -H "x-api-key: tJ3b39yg7mceuqdoS_TH7m0d6yxmlWLMDenalKcttR" 'http://snf-670397.vm.okeanos.grnet.gr:8000/backend/upload_file/'
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


