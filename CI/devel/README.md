# Description
Scripts to fully deploy ~okeanos-LoD service.


# Usage
Running

```
./create.sh <okeanos-token> <public_key_path> <private_key_path>
```

will create a Service VM that will host the API of ~okeanos-LoD service, a Central VM that will be
used to collect statistical data about ~okeanos-LoD service usage and a Lambda Instance through
the API.

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

