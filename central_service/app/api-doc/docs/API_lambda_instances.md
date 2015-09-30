# Lambda Instances related API calls


## Create Lambda Instance Record


### API Call

Type | Description |
-------|-----------------|
 **Description** | create a new lambda instance record
 **URL**         | /api/lambda_instances/
 **HTTP Method** | POST
 **Security**    | Basic Authentication

#### Parameters

| Parameter | Description | Required | Default Value | Example Value |
| --- | --- | --- | --- | --- |
| uuid | The Unique Identifier of the lamdba instance, as identified from the service vm | Yes | None |'24b8a635-8d71-4016-b8f5-c4a14348ed8f'
| name | The name of the lamdba instance. | Yes | None | 'My first lambda instance'
| instance_info | JSON encoded info about the lambda instance. | Yes | None |  |
| status | The status of the lambda instance. | Yes | None | "20" |
| failure_message | (optional) A message related to the failed status of the lamdbda instance | Yes | "" | "SSH connection timed out." |

#### Headers

Type | Description | Required | Default value | Example value
------|-------------|----------|---------------|---------------
Authorization | ~okeanos authentication token. If you have an account you may find the authentication token at (Dashboad-> API Access) https://accounts.okeanos.grnet.gr/ui/api_access. | `Yes` | None | Token tJ3b3f32f23ceuqdoS_..

### Example API call

`curl -X POST -H "Content-Type: application/json" -H "Authorization:Token tJ3b3f32f23ceuqdoS_TH7m0d6yxmlWL1r2ralKcttR" -d '{"uuid": "24b8a635-8d71-4016-b8f5-c4a14348ed8f", "name": "My frist Lambda instance", "instance_info": "", "status": "20", "failure_message": "OK"}' 'http://<hostname>/api/lambda_instances/'`

### Response

```json
{
  "status": {
    "short_description": "Your request to create a new lambda instance has been accepted.",
    "code": 202
  },
  "data": [
    {
      "id": "24b8a635-8d71-4016-b8f5-c4a14348ed9f"
    }
  ]
}

```

## Update Lambda Instance Status

### API Call

Type | Description |
-------|-----------------|
 **Description** | update the status of the lambda instance
 **URL**         | /api/lambda_instances/[uuid]
 **HTTP Method** | POST
 **Security**    | Basic Authentication

#### Parameters

| Parameter | Description | Required | Default Value | Example Value |
| --- | --- | --- | --- | --- |
| status | The status of the lambda instance. | Yes | None | "20" |
| failure_message | A message related to the failed status of the lamdbda instance | Yes | "" | "SSH connection timed out." |

#### Headers

Type | Description | Required | Default value | Example value
------|-------------|----------|---------------|---------------
Authorization | ~okeanos authentication token. If you have an account you may find the authentication token at (Dashboad-> API Access) https://accounts.okeanos.grnet.gr/ui/api_access. | `Yes` | None | Token tJ3b3f32f23ceuqdoS_..

### Example API call

`curl -X POST -H "Content-Type: application/json" -H "Authorization:Token tJ3b3f32f23ceuqdoS_TH7m0d6yxmlWL1r2ralKcttR" -d '{"status": "20", "failure_message": "OK"}' 'http://<hostname>/api/lambda_instances/24b8a635-8d71-4016-b8f5-c4a14348ed8f'`

### Response

```json
{
  "status": {
    "short_description": "Lambda instances status update accepted.",
    "code": 202
  },
  "data": [
    {
      "id": "24b8a635-8d71-4016-b8f5-c4a14348ed8f"
    }
  ]
}

```

## Delete Lambda Instance

### API Call

Type | Description |
-------|-----------------|
 **Description** | delete the specified lambda instance
 **URL**         | /api/lambda_instances/[uuid]
 **HTTP Method** | DELETE
 **Security**    | Basic Authentication


#### Headers

Type | Description | Required | Default value | Example value
------|-------------|----------|---------------|---------------
Authorization | ~okeanos authentication token. If you have an account you may find the authentication token at (Dashboad-> API Access) https://accounts.okeanos.grnet.gr/ui/api_access. | `Yes` | None | Token tJ3b3f32f23ceuqdoS_..

### Example API call

`curl -X DELETE -H "Content-Type: application/json" -H "Authorization:Token tJ3b3f32f23ceuqdoS_TH7m0d6yxmlWL1r2ralKcttR" 'http://<hostname>/api/lambda_instances/24b8a635-8d71-4016-b8f5-c4a14348ed8f'`

### Response

```json
{
  "status": {
    "short_description": "Your request to destroy the specified lambda instance has been accepted.",
    "code": 202
  },
  "data": [
    {
      "id": "24b8a635-8d71-4016-b8f5-c4a14348ed8f"
    }
  ]
}

```

## List Lambda Instances

### API Call

Type | Description |
-------|-----------------|
 **Description** | lists the lambda instances of the specified user
 **URL**         | /api/lambda_instances/
 **HTTP Method** | GET
 **Security**    | Basic Authentication


#### Headers

Type | Description | Required | Default value | Example value
------|-------------|----------|---------------|---------------
Authorization | ~okeanos authentication token. If you have an account you may find the authentication token at (Dashboad-> API Access) https://accounts.okeanos.grnet.gr/ui/api_access. | `Yes` | None | Token tJ3b3f32f23ceuqdoS_..

### Example API call

`curl -X GET -H "Content-Type: application/json" -H "Authorization:Token tJ3b3f32f23ceuqdoS_TH7m0d6yxmlWL1r2ralKcttR" 'http://<hostname>/api/lambda_instances/'`

### Response

```json


```

## Count Lambda Instances


### API Call

Type | Description |
-------|-----------------|
 **Description** | counts the active lambda instances and returns its count
 **URL**         | /api/lambda_instances/count
 **HTTP Method** | GET


### Example API call

`curl -X DELETE -H "Content-Type: application/json" 'http://<hostname>/api/lambda_instances/count`

### Response

```json
{
  "status": {
    "short_description": "Lamdba instances count.",
    "code": 200
  },
  "data": {
    "count": "2"
  }
}

```
