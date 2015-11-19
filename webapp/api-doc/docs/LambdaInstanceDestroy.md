
# API - lambda instance destroy - Description

Lambda instance destroy call, given an authentication token through the header Authentication,
will firstly check the validity of the token. If the token is invalid, the API will reply with
a "401 Unauthorized" code. If the token is valid, the API will reply with a "202 ACCEPTED" code
and will start destroying all the VMs of the specified lambda instance along with the corresponding
public ip and private network.

## Basic Parameters

|Type            | Description
|----------------|--------------------------
| **Description** | Destroy a specified lambda instance
| **URL**         | api/lambda-instances/[lambda-instance-id]/
| **HTTP Method** | DELETE
| **Security**    | Basic Authentication


### Headers

Type | Description | Required | Default value | Example value
------|-------------|----------|---------------|---------------
Authorization | ~okeanos authentication token. If you have an account you may find the authentication token at (Dashboad-> API Access) https://accounts.okeanos.grnet.gr/ui/api_access. | `Yes` | None | Token tJ3b3f32f23ceuqdoS_..


### Parameters

Name | Description | Required | Default value | Example value
------|-------------|----------|---------------|---------------
lambda-instance-id  | The id of the specified lambda instance. For more information see [List Lambda instances page](LambdaInstancesList.md). |`Yes` |None| 3


## Example

In this example we are going to destroy the lambda instance with id 9ac8e7ab-57f9-48a6-af18-ef8a749b1e8c

The request in curl

```
curl -X DELETE -H "Authorization:Token tJ3b3f32f23ceuqdoS_TH7m0d6yxmlWL1r2ralKcttY" \
 'https://<hostname>/api/lambda-instances/9ac8e7ab-57f9-48a6-af18-ef8a749b1e8c/'
```


### Response body

If the authentication token is correct the response will be

```
{
  "status": {
    "code": 202,
    "short-description": "Your request to destroy the specified lambda instance has been accepted"
  }
}
```

For the case where the authentication token is not correct, refer to [Authentication page](Authentication.md).

### Response messages

The main response messages are:

- HTTP/1.1 202 ACCEPTED : (Success)
- HTTP/1.1 401 UNAUTHORIZED : (Fail)
- HTTP/1.1 404 NOT FOUND : (Fail)
