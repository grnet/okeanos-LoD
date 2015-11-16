

## Usage

Although, not intended to operate in this way, the Fokia library can be used to bootstrap and configure a λ instance. To install the Fokia library (locally) a user needs to have `pip` already installed and available.

The user must have (or create) a `~/.kamakirc` configuration file. Here is an example configuration:

```
[global]
default_cloud = lambda
; ca_certs = /path/to/certs

[cloud "lambda"]
url = https://accounts.okeanos.grnet.gr/identity/v2.0
token = your-okeanos-token
```

After checking out the [code base](https://github.com/grnet/okeanos-LoD) change directory into `core/` and install the Fokia prerequisites with the following command:

```bash
$ sudo pip install -r requirements.txt
```

Then install the Fokia library using the following command:

```bash
$ sudo python setup.py install
```

To bootstrap a λ instance the `lambda_instance_manager.py` executable inside the `core/fokia/` folder can be used. The available options are shown in the listing below:

```sh
$ python lambda_instance_manager.py -h
usage: lambda_instance_manager.py [-h] [--master-name MASTER_NAME]
                                  [--slaves SLAVES]
                                  [--vcpus_master VCPUS_MASTER]
                                  [--vcpus_slave VCPUS_SLAVE]
                                  [--ram_master RAM_MASTER]
                                  [--ram_slave RAM_SLAVE]
                                  [--disk_master DISK_MASTER]
                                  [--disk_slave DISK_SLAVE]
                                  [--project-name PROJECT_NAME]

optional arguments:
  --master-name MASTER_NAME
                        Name of Flink master VM [default: lambda-master]
  --slaves SLAVES       Number of Flink slaves [default: 1]
  --vcpus_master VCPUS_MASTER
                        Number of CPUs on Flink master [default: 4]
  --vcpus_slave VCPUS_SLAVE
                        Number of CPUs on Flink slave(s) [default: 4]
  --ram_master RAM_MASTER
                        Size of RAM on Flink master (in MB) [default: 4096MB]
  --ram_slave RAM_SLAVE
                        Size of RAM on Flink slave(s) (in MB) [default: 4096MB]
  --disk_master DISK_MASTER
                        Size of disk on Flink master (in GB) [default: 40GB]
  --disk_slave DISK_SLAVE
                        Size of disk on Flink slave(s) (in GB) [default: 40GB]
```


