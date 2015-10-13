# Description
Scripts to deploy ~okeanos-LoD Central Service.


# Usage
Running

```
./create.sh <okeanos-token> <public_key_path> <private_key_path>
```

will create a Central Service VM that will host the application which will collect statistical
data about ~okeanos-LoD service.

Running

```
./destroy.sh <okeanos-token> <public_key_path> <private_key_path>
```

will destroy the Central VM and release its resources(a public ip).


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


# File Arrangement
For everything to work properly, place `create.sh`, `destroy.sh` and `utils.py`inside the same directory.


# Clarifications
Make sure that the paths for the public and the private ssh keys are absolute and not relative paths.
