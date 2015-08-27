---
title: API | create lambda instance
description: create a new lambda instance
---

# API - create lambda instance - Description

Lambda instance creation call. Given an authentication token through the header x-api-key, and the instance specifications through other HTTP headers, it will firstly check the validity of the token. If the token is invalid, the API will reply with a 401 error. If the token is valid, the API will start creating a new lambda instance, using the instance specifications specified via the HTTP headers. Then, the API will reply with the details of the cluster in creation, along with a 200 success code.

## Basic Parameters

Type | Description |
-------|-----------------|
 **Description** | create a new lambda instance
 **URL**         | /backend/create_lambda_instance
 **HTTP Method** | GET
 **Security**    | Basic Authentication


### Headers

Type | Description | Required | Default value | Example value |
------|-------------|----------|---------------|---------------|
x-api-key | ~okeanos authentication token. If you have an account you may find the authentication token at (Dashboad-> API Access) https://accounts.okeanos.grnet.gr/ui/api_access. | `Yes` | None | tJ3b3f32f23ceuqdoS_TH7m0d6yxmlWL1r2ralKcttY
x-auth-url | ~okeanos authentication url. If you have an account you may find the authentication url at (Dashboad-> API Access) https://accounts.okeanos.grnet.gr/ui/api_access. | `Yes` | None | https://accounts.okeanos.grnet.gr/identity/v2.0
cloud-name | The cloud name specified in the .kamakirc file | `Yes` | None | lambda
master-name | Name of the master node | `Yes` | None | lambda-master
slaves | Number of slaves | `Yes` | None | 3
vcpus-master | Number of CPUs of the master node | `Yes` | None | 4
vcpus-slave | Number of CPUs of each slave node | `Yes` | None | 2
ram-master | Amount of RAM of master node in MB | `Yes` | None | 4096
ram-master | Amount of RAM of each slave node in MB | `Yes` | None | 2048
disk-master | Amount of HDD space of master node in GB | `Yes` | None | 40
disk-slave | Amount of HDD space of each slave node in GB | `Yes` | None | 40
ip-allocation | Allocation of public ips. Choose between none, master, all | `Yes` | None | master
network-request | Number of private networks | `Yes` | None | 1
project-name | Name of the project | `Yes` | None | lambda.grnet.gr


## Example

In this example we are going to create a new lambda instance, using the specs specified by the HTTP headers.

The request in curl

```
curl -X GET -H "x-api-key: tJ3b3f32f23ceuqdoS_TH7m0d6yxmlWL1r2ralKcttY" -H "x-auth-url: https://accounts.okeanos.grnet.gr/identity/v2.0" -H "cloud-name: lambda" -H "master-name: test-master" -H "slaves: 1" -H "vcpus-master: 4" -H "vcpus-slave: 4" -H "ram-master: 2048" -H "ram-slave: 2048" -H "disk-master: 40" -H "disk-slave: 40" -H "ip-allocation: master" -H "network-request: 1" -H "project-name: lambda.grnet.gr" 'http://snf-671502.vm.okeanos.grnet.gr/backend/create_lambda_instance/'
```


### Response body

If the authentication token and url is correct, and all the headers are given correctly, a sample response is

```
{
  "specs": {
    "master_name": "test-master",
    "slaves": 1,
    "vcpus_master": 4,
    "vcpus_slave": 4,
    "ram_master": 2048,
    "ram_slave": 2048,
    "disk_master": 40,
    "disk_slave": 40,
    "ip_allocation": "master",
    "network_request": 1,
    "project_name": "lambda.grnet.gr"
  }
}
```


### Response messages

The main response messages are:

- HTTP/1.1 201 OK : (Success)
- HTTP/1.1 401 UNAUTHORIZED : (Fail)
