# Description
Scripts to fully deploy ~okeanos-LoD service.


# Usage
Running

```
./create.sh <okeanos-token> <public_key_path> <private_key_path>
```

will create a Service VM that will host the API of ~okeanos-LoD service, a Central VM that will be
used to collect statistical data about ~okeanos-LoD service usage and a Lambda Instance through
the API. Moreover, a given application will be deployed and started on the Lambda Instance.

Running

```
./destroy.sh <okeanos-token> <public_key_path> <private_key_path>
```

will destroy everything that has been created with `create.sh` script.

# Usage for Continuous Integration
To use these scripts for Continuous Integration, simply run

```
./destroy.sh <okeanos-token> <public_key_path> <private_key_path>
./create.sh <okeanos-token> <public_key_path> <private_key_path>
```

each time a new pull request is merged on the branch you want to test. Note that, the first time
these scripts are deployed, `destroy.sh` script need not be called.


# Requirements
For everything to work properly, the following packages need to be installed:

* `git`  
* `python-dev`  
* `virtualenv`  


# Files Arrangement
For everything to work properly, place `create.sh`,`destroy.sh`,`manage_application.py`,`manage_lambda_instance.py`, `utils.py` and the application you want to start on the
lambda instance inside the same directory.

Note that, the name of the application file is hardcoded inside the `create.sh` file. The default name is `stream-1.0-jar-with-dependencies.jar`.


# Clarifications
Make sure that the paths for the public and the private ssh keys are absolute and not relative paths.
