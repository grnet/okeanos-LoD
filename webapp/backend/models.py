from django.db import models

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


class ProjectFile(models.Model):
    id = models.AutoField("File ID", primary_key=True, unique=True, help_text="Project file id.")
    name = models.CharField(max_length=100)
    path = models.CharField(max_length=400)
    description = models.CharField(max_length=400,blank=True, default='')
    owner = models.ForeignKey(User, default=None, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "ProjectFile"
        app_label = "backend"


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

    uuid = models.BigIntegerField("Instance UUID", null=False, unique=True,
                                  help_text="Unique key asigned to every instance.")

    STARTED = "0"
    STOPPED = "1"
    PENDING = "2"
    STARTING = "3"
    STOPPING = "4"
    DESTROYING = "5"
    DESTROYED = "6"
    SCALING_UP = "7"
    SCALING_DOWN = "8"
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
    )
    status = models.CharField(max_length=10, choices=status_choices, default=PENDING,
                              help_text="The status of this instance.")

    def __unicode__(self):
        info = "Instance id: " + str(self.id) + "\n" + \
               "Instance info: " + str(self.instance_info)
        return info

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
    priv_ip: the private ip of the server.
    lambda_instance: the lambda instance the server belongs to.
    :model: models.LambdaInstance.
    """
    id = models.AutoField("Server ID", primary_key=True, null=False, blank=False,
                          unique=True, default="",
                          help_text="Server id provided by kamaki.")

    hostname = models.TextField('Hostname', default="", help_text="Hostname of the server.")
    cpus = models.IntegerField("CPUs", null=True, help_text="Number of cpus.")
    ram = models.IntegerField("RAM", null=True, help_text="Amount of ram.")
    disk = models.IntegerField("Hard Drive", null=True, help_text="Amount of disk space.")
    pub_ip = models.GenericIPAddressField("Public ip", null=True, help_text="Public ip of server.")
    priv_ip = models.GenericIPAddressField("Private ip", null=True,
                                           help_text="Private ip of server.")
    lambda_instance = models.ForeignKey(LambdaInstance, null=False, blank=False, unique=False,
                                        default=None, on_delete=models.CASCADE)

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
    id = models.AutoField("Network ID",
                          primary_key=True, null=False, blank=False,
                          unique=True, default="",
                          help_text="Private network id provided by kamaki.")
    subnet = models.CharField(max_length=100)
    gateway = models.GenericIPAddressField("Gateway", null=False, blank=False, unique=False)
    lambda_instance = models.ForeignKey(LambdaInstance, null=False, blank=False, unique=False,
                                        default=None, on_delete=models.CASCADE)

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
