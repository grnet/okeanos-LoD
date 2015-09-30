# Lambda Applications related API calls


## Create Lambda Application Record


### API Call

Type | Description |
-------|-----------------|
 **Description** | create a new lambda application record
 **URL**         | /api/lambda_applications/
 **HTTP Method** | POST
 **Security**    | Basic Authentication

#### Parameters

| Parameter | Description | Required | Default Value | Example Value |
| --- | --- | --- | --- | --- |
| uuid | The Unique Identifier of the lamdba application, as identified from the service vm. | Yes | None |'24b8a635-8d71-4016-b8f5-c4a14348ed8f'
| name | The name of the lamdba application. | Yes | None | 'My first lambda application'
| description | Description text about the lambda application. | Yes | None | "Testing the lambda cluster." |
| status | The status of the lambda application. | Yes | None | "2" |
| failure_message | (optional) A message related to the failed status of the lamdbda application | Yes | "" | "Segmentation fault." |

#### Headers

Type | Description | Required | Default value | Example value
------|-------------|----------|---------------|---------------
Authorization | ~okeanos authentication token. If you have an account you may find the authentication token at (Dashboad-> API Access) https://accounts.okeanos.grnet.gr/ui/api_access. | `Yes` | None | Token tJ3b3f32f23ceuqdoS_..

### Example API call

`curl -X POST -H "Content-Type: application/json" -H "Authorization:Token tJ3b3f32f23ceuqdoS_TH7m0d6yxmlWL1r2ralKcttR" -d '{"uuid": "24b8a635-8d71-4016-b8f5-c4a14348ed8f", "name": "My frist Lambda application", "description": "", "status": "2", "failure_message": "Segmentation fault."}' 'http://<hostname>/api/lambda_applications/'`

### Response

```json
{
  "status": {
    "short_description": "Your request to create the specified application has been accepted.",
    "code": 202
  },
  "data": [
    {
      "id": "24b8a635-8d71-4016-b8f5-c4a14348ed8f"
    }
  ]
}

```

## Update Lambda Application Status

### API Call

Type | Description |
-------|-----------------|
 **Description** | update the status of the lambda application
 **URL**         | /api/lambda_applications/[uuid]
 **HTTP Method** | POST
 **Security**    | Basic Authentication

#### Parameters

| Parameter | Description | Required | Default Value | Example Value |
| --- | --- | --- | --- | --- |
| status | The status of the lambda application. | Yes | None | "0" |
| failure_message | A message related to the failed status of the lamdbda application | Yes | "" | "No stdout found." |

#### Headers

Type | Description | Required | Default value | Example value
------|-------------|----------|---------------|---------------
Authorization | ~okeanos authentication token. If you have an account you may find the authentication token at (Dashboad-> API Access) https://accounts.okeanos.grnet.gr/ui/api_access. | `Yes` | None | Token tJ3b3f32f23ceuqdoS_..

### Example API call

`curl -X POST -H "Content-Type: application/json" -H "Authorization:Token tJ3b3f32f23ceuqdoS_TH7m0d6yxmlWL1r2ralKcttR" -d '{"status": "0", "failure_message": ""}' 'http://<hostname>/api/lambda_applications/24b8a635-8d71-4016-b8f5-c4a14348ed8f'`

### Response

```json
{
  "status": {
    "short_description": "Lambda application status update accepted.",
    "code": 202
  },
  "data": [
    {
      "id": "24b8a635-8d71-4016-b8f5-c4a14348ed8f"
    }
  ]
}

```

## Delete Lambda Application

### API Call

Type | Description |
-------|-----------------|
 **Description** | delete the specified lambda application
 **URL**         | /api/lambda_applications/[uuid]
 **HTTP Method** | DELETE
 **Security**    | Basic Authentication


#### Headers

Type | Description | Required | Default value | Example value
------|-------------|----------|---------------|---------------
Authorization | ~okeanos authentication token. If you have an account you may find the authentication token at (Dashboad-> API Access) https://accounts.okeanos.grnet.gr/ui/api_access. | `Yes` | None | Token tJ3b3f32f23ceuqdoS_..

### Example API call

`curl -X DELETE -H "Content-Type: application/json" -H "Authorization:Token tJ3b3f32f23ceuqdoS_TH7m0d6yxmlWL1r2ralKcttR" 'http://<hostname>/api/lambda_applications/24b8a635-8d71-4016-b8f5-c4a14348ed8f'`

### Response

```json
{
  "status": {
    "short_description": "Your request to destroy the specified lambda application has been accepted.",
    "code": 202
  },
  "data": [
    {
      "id": "24b8a635-8d71-4016-b8f5-c4a14348ed8f"
    }
  ]
}

```

## List Lambda Applications

### API Call

Type | Description |
-------|-----------------|
 **Description** | lists the lambda applications of the specific user being authorized.
 **URL**         | /api/lambda_applications/
 **HTTP Method** | GET
 **Security**    | Basic Authentication


#### Headers

Type | Description | Required | Default value | Example value
------|-------------|----------|---------------|---------------
Authorization | ~okeanos authentication token. If you have an account you may find the authentication token at (Dashboad-> API Access) https://accounts.okeanos.grnet.gr/ui/api_access. | `Yes` | None | Token tJ3b3f32f23ceuqdoS_..

### Example API call

`curl -X GET -H "Content-Type: application/json" -H "Authorization:Token tJ3b3f32f23ceuqdoS_TH7m0d6yxmlWL1r2ralKcttR" 'http://<hostname>/api/lambda_applications/'`

### Response

```json


```

## Count Lambda Instances


### API Call

Type | Description |
-------|-----------------|
 **Description** | counts the active lambda applications and returns its count
 **URL**         | /api/lambda_applications/count
 **HTTP Method** | GET


### Example API call

`curl -X DELETE -H "Content-Type: application/json" 'http://<hostname>/api/lambda_applications/count`

### Response

```json
{
  "status": {
    "short_description": "Lamdba applications count.",
    "code": 200
  },
  "data": {
    "count": "2"
  }
}

```
