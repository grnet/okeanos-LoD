from django.db import models
from uuid import uuid4

"""
OBJECTS
"""


class User(models.Model):
    """
    Stores information about every lambda-user.
    id: the okeanos id of the user.
    token: the okeanos token of the user.
    """
    id = models.AutoField("id", primary_key=True)
    uuid = models.CharField("uuid", null=False, blank=False,
                            unique=True, default="", max_length=255,
                            help_text="Unique user id asign by Astakos")
    name = models.CharField("name", max_length=200, default="", null=True, blank=True)

    def __unicode__(self):
        info = "User id: " + str(self.id)
        return info

    class Meta:
        verbose_name = "User"
        app_label = 'backend'
        # db_tablespace = "tables"

    def is_authenticated(self, *args):
        return True


class Project(models.Model):
    """
    Stores information about every okeanos project that has been used with the LoD.
    id: the okeanos id of the project.
    description: a small description of the project.
    """
    id = models.AutoField("Project ID", primary_key=True, null=False, blank=False,
                          unique=True, default="",
                          help_text="Project id provided by kamaki.")
    description = models.TextField("Project Description", default="",
                                   help_text="The description of a project.")

    def __unicode__(self):
        info = "Project id: " + str(self.id) + "\n" + \
               "Description: " + str(self.description)
        return info

    class Meta:
        verbose_name = "Project"
        app_label = 'backend'


class Application(models.Model):
    id = models.AutoField("id", primary_key=True, unique=True, help_text="Application id.")
    uuid = models.UUIDField("uuid", unique=True, default=uuid4,
                            help_text="Application uuid.")
    name = models.CharField(max_length=100, default="", null=True, blank=True)
    project_id = models.UUIDField("project_id", unique=False, default=uuid4,
                                  help_text="Project id.")
    path = models.CharField(max_length=400, default="lambda_applications")
    description = models.CharField(max_length=400, blank=True, default='')
    owner = models.ForeignKey(User, default=None, on_delete=models.SET_NULL, null=True, blank=True)
    failure_message = models.TextField(default="", null=True, blank=True,
                                       help_text="Error message regarding this application.")
    execution_environment_name = models.CharField(max_length=100, default="", null=True, blank=True)

    UPLOADED = "0"
    UPLOADING = "1"
    FAILED = "2"
    status_choices = (
        (UPLOADED, 'UPLOADED'),
        (UPLOADING, 'UPLOADING'),
        (FAILED, 'FAILED'),
    )
    status = models.CharField(max_length=10, choices=status_choices, default=UPLOADING,
                              help_text="The status of this application.")

    BATCH = "0"
    STREAMING = "1"
    type_choices = (
        (BATCH, 'BATCH'),
        (STREAMING, 'STREAMING')
    )
    type = models.CharField(max_length=10, null=False, choices=type_choices, default=None,
                            help_text="The type of this application.")

    class Meta:
        verbose_name = "ProjectFile"
        app_label = "backend"

    def __unicode__(self):
        info = "Id: " + str(self.id) + "\n" + \
               "Description: " + str(self.description) + "\n" + \
               "Status: " + str(self.status) + "\n" + \
               "Type: " + str(self.type)
        return info

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Application, self).save(*args, **kwargs)



class Token(models.Model):
    user = models.OneToOneField(User, related_name='kamaki_token')
    key = models.CharField(max_length=100, null=True)
    creation_date = models.DateTimeField('Creation Date')

    class Meta:
        verbose_name = "Token"
        app_label = "backend"


class LambdaInstance(models.Model):
    """
    Stores every lambda instance created for the LoD service.
    id: a unique identifier the service creates for every Lambda Instance.
    uuid: A unique id asigned to every Lambda Instance. This key will be used by the API
          to reference a specific Lambda Instance.
    failure_message: Message that denotes the reason of failure of the lambda instance.
    :model: models.Server
    """
    id = models.AutoField("Instance ID", primary_key=True, null=False,
                          help_text="Auto-increment instance id.")
    # To store instance info, create a python dictionary with the needed information an use
    # json.dumps(dict) to create a string out of the given dictionary. To parse the info use
    # json.loads() method.
    instance_info = models.TextField('Instance info', blank=False, null=False, default='{}',
                                     help_text="Instance information in json format.")

    name = models.CharField(max_length=100, default="Lambda Instance",
                            help_text="A name given to the instance.")

    uuid = models.UUIDField("Instance UUID", null=False, unique=True, editable=False,
                            help_text="Unique key assigned to every instance.")

    failure_message = models.TextField(default="", null=True, blank=True,
                                       help_text="Error message regarding this lambda instance")

    STARTED = "0"
    STOPPED = "1"
    PENDING = "2"
    STARTING = "3"
    STOPPING = "4"
    DESTROYING = "5"
    DESTROYED = "6"
    SCALING_UP = "7"
    SCALING_DOWN = "8"
    FAILED = "9"
    CLUSTER_CREATED = "10"
    CLUSTER_FAILED = "11"
    INIT_DONE = "12"
    INIT_FAILED = "13"
    COMMONS_INSTALLED = "14"
    COMMONS_FAILED = "15"
    HADOOP_INSTALLED = "16"
    HADOOP_FAILED = "17"
    KAFKA_INSTALLED = "18"
    KAFKA_FAILED = "19"
    FLINK_INSTALLED = "20"
    FLINK_FAILED = "21"
    FLUME_INSTALLED = "22"
    FLUME_FAILED = "23"
    status_choices = (
        (STARTED, 'STARTED'),
        (STOPPED, 'STOPPED'),
        (PENDING, 'PENDING'),
        (STARTING, 'STARTING'),
        (STOPPING, 'STOPPING'),
        (DESTROYING, 'DESTROYING'),
        (DESTROYED, 'DESTROYED'),
        (SCALING_UP, 'SCALING_UP'),
        (SCALING_DOWN, 'SCALING_DOWN'),
        (FAILED, 'FAILED'),
        (CLUSTER_CREATED, 'CLUSTER_CREATED'),
        (CLUSTER_FAILED, 'CLUSTER_FAILED'),
        (INIT_DONE, 'INIT_DONE'),
        (INIT_FAILED, 'INIT_FAILED'),
        (COMMONS_INSTALLED, 'COMMONS_INSTALLED'),
        (COMMONS_FAILED, 'COMMONS_FAILED'),
        (HADOOP_INSTALLED, 'HADOOP_INSTALLED'),
        (HADOOP_FAILED, 'HADOOP_FAILED'),
        (KAFKA_INSTALLED, 'KAFKA_INSTALLED'),
        (KAFKA_FAILED, 'KAFKA_FAILED'),
        (FLINK_INSTALLED, 'FLINK_INSTALLED'),
        (FLINK_FAILED, 'FLINK_FAILED'),
        (FLUME_INSTALLED, 'FLUME_INSTALLED'),
        (FLUME_FAILED, 'FLUME_FAILED')
    )
    status = models.CharField(max_length=10, choices=status_choices, default=PENDING,
                              help_text="The status of this instance.")

    master_node = models.ForeignKey('Server', blank=True, null=True, default=None,
                                       on_delete=models.CASCADE)

    started_batch = models.BooleanField(default=False,
                                        help_text="True, if batch job is started")
    started_streaming = models.BooleanField(default=False,
                                            help_text="True, if streaming job is started")

    def __unicode__(self):
        info = "Instance id: " + str(self.id) + "\n" + \
               "Instance info: " + str(self.instance_info)
        return info

    def save(self, *args, **kwargs):
        self.full_clean()
        super(LambdaInstance, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Lambda Instance"
        app_label = 'backend'


class Server(models.Model):
    """
    Stores information about every server created for the LoD service.
    id: the okeanos id of the server.
    hostname: the hostname of the server.
    cput: the cpus of the server.
    ram: the ram of the server.
    disk: the disk of the server.
    pub_ip: the public ip of the server.
    pub_ip_id: the id assigned to this public ip by ~okeanos.
    priv_ip: the private ip of the server.
    lambda_instance: the lambda instance the server belongs to.
    :model: models.LambdaInstance.
    """
    id = models.BigIntegerField("Server ID", primary_key=True, null=False, blank=False,
                                unique=True, default="",
                                help_text="Server id provided by kamaki.")

    hostname = models.TextField('Hostname', default="", help_text="Hostname of the server.")
    cpus = models.IntegerField("CPUs", null=True, help_text="Number of cpus.")
    ram = models.IntegerField("RAM", null=True, help_text="Amount of ram.")
    disk = models.IntegerField("Hard Drive", null=True, help_text="Amount of disk space.")
    pub_ip = models.GenericIPAddressField("Public ip", null=True, help_text="Public ip of server.")
    pub_ip_id = models.BigIntegerField("~okeanos id of public ip", null=True, blank=False,
                                       unique=True)
    priv_ip = models.GenericIPAddressField("Private ip", null=True,
                                           help_text="Private ip of server.")
    lambda_instance = models.ForeignKey(LambdaInstance, null=False, blank=False, unique=False,
                                        default=None, on_delete=models.CASCADE,
                                        related_name="servers")

    def __unicode__(self):
        info = "Server id: " + str(self.id) + "\n" + \
               "Hostname: " + str(self.hostname) + "\n" + \
               "CPUs: " + str(self.cpus) + "\n" + \
               "Hard Drive: " + str(self.disk) + "\n" + \
               "RAM: " + str(self.ram) + "\n" + \
               "Public ip: " + str(self.pub_ip) + "\n" + \
               "Private ip: " + str(self.priv_ip) + \
               "Lambda Instance id: " + str(self.lambda_instance.id)
        return info

    class Meta:
        verbose_name = "Server"
        app_label = 'backend'


class PrivateNetwork(models.Model):
    """
    Stores  information about every private network created for the LoD service.
    id: a unique identifier.
    subnet: the subnet of the network.
    gateway: the gateway of the network.
    lambda_instance: the lambda instance that this network belongs to.
    :model: models.LambdaInstance
    """
    id = models.BigIntegerField("Network ID",
                                primary_key=True, null=False, blank=False,
                                unique=True, default="",
                                help_text="Private network id provided by kamaki.")
    subnet = models.CharField(max_length=100)
    gateway = models.GenericIPAddressField("Gateway", null=False, blank=False, unique=False)
    lambda_instance = models.ForeignKey(LambdaInstance, null=False, blank=False, unique=False,
                                        default=None, on_delete=models.CASCADE,
                                        related_name="private_network")

    def __unicode__(self):
        info = "Network id: " + str(self.id) + "\n" + \
               "Subnet: " + str(self.subnet) + "\n" + \
               "Gateway: " + str(self.gateway) + "\n" + \
               "Lambda Instance id: " + str(self.lambda_instance.id)
        return info

    class Meta:
        verbose_name = "PrivateNetwork"
        app_label = 'backend'


"""
OBJECT CONNECTIONS
"""


class LambdaInstanceProjectConnection(models.Model):
    """
    Connection table for lambda instance and project.
    :model: models.LambdaInstance
    :model: models.Project
    """
    project = models.ForeignKey(Project, null=False, blank=False, unique=False,
                                on_delete=models.CASCADE)
    lambda_instance = models.ForeignKey(LambdaInstance, null=False, blank=False, unique=False,
                                        on_delete=models.CASCADE)

    def __unicode__(self):
        info = "Project: " + self.project + "\n" + \
               "LambdaInstance: " + self.lambda_instance
        return info

    class Meta:
        verbose_name = "LambdaInstanceProjectConnection"
        app_label = 'backend'


class LambdaInstanceApplicationConnection(models.Model):
    """
    Connection table for lambda instance and application.
    lambda_instance: models.LambdaInstance
    application: models.Application
    """

    lambda_instance = models.ForeignKey(LambdaInstance, null=False, blank=False, unique=False,
                                        related_name="applications", on_delete=models.CASCADE)
    application = models.ForeignKey(Application, null=False, blank=False, unique=False,
                                    related_name="lambda_instances", on_delete=models.CASCADE)
    started = models.BooleanField(default=False,
                                  help_text="True, if application is started")
