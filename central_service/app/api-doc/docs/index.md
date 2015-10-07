# API Overview

## Operations (performed by the API)


### User related
* Create user **no api call, created from the HTTP headers**
> The user creation will be done automatically from the api when a new authentication is made by a User not previously existent inside the database.

* Count **GET /api/users/count**, (*authorization not needed*)
> The user will be able to make an API call and get the number of total users having lambda instances on the ~okeanos infrastructure.


### Lambda instances related
* Create lambda instance **POST /api/lambda_instances/**
> The service vm will issue an API call towards the central service, creating a new lambda instance.  
**The service vm will have to know the user's ~okeanos token.**

* Destroy lambda instance **DELETE /api/lambda-instances/[uuid]**
> The service vm will issue an API call towards the central service, deleting the lambda instance.  
**The whole lambda cluster can be deleted from inside the kamaki API or the Web interface**  

* Update lambda instance **POST /api/lambda_instances/[uuid]/status**
> The service vm will issue and API call towards the central service, updating the status field and, perhaps, the failure message of the lambda instance.

* List **GET /api/lambda_instances**
> The user will be able to make an API call and get a list of all of their lambda instances running on the ~okeanos infrastructure.

* Count **GET /api/lambda_instances/count** (*authorization not needed*)
> The user will be able to make an API call and get the number of total lambda instances running on the ~okeanos infrastructure.

### Lambda applications related
* Create lambda application **POST /api/lambda_applications/**
> The service vm will issue an API call towards the central service, creating a new lambda application. It will have to pass both the user authentication token and the uuid of the lambda application.  
**Will not be tracking application started from outside the service vm api**

* Destroy lambda application **DELETE /api/lambda_applications/[uuid]**
> The service vm will issue an API call towards the central service, deleting the lambda application.  
**Will not be tracking application deleted from outside the service vm api** 

* Update lambda application **POST /api/lambda_applications/[uuid]/status**
> The service vm will issue and API call towards the central service, updating the status field and, perhaps, the failure message of the lambda application.

* List **GET /api/lambda_applications**
> The user will be able to make an API call and retrieve a list of all of their lambda applications running on the ~okeanos infrastructure.

* Count **GET /api/lambda_applications/count** (*authorization not needed*)
> The user will be able to make an API call and get the number of total lambda applications running on the ~okeanos infrastructure.