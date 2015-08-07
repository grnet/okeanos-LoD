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
    id = models.CharField("UUID", primary_key=True, null=False, blank=False, unique=True, default="", max_length=255, help_text="Unique user id asign by Astakos")
    token = models.CharField("Okeanos Token", null=True, blank=True, unique=True, default="", max_length=64, help_text="Token provided by ~okeanos.")

class Project(models.Model):
    """
    Stores information about every okeanos project that has been used with the LoD.
    id: the okeanos id of the project.
    description: a small description of the project.
    """
    id = models.AutoField("Project ID", primary_key=True, null=False, blank=False, unique=True, default="", help_text="Project id provided by kamaki.")
    description = models.TextField("Project Description", null=True, blank=True, unique=False, default="", help_text="The description of a project.")

class Cluster(models.Model):
    """
    Stores every cluster created for the LoD service.
    id: a unique identifier the service creates for every cluster.
    :model: models.Server
    :model: models.Cluster_info
    """
    id = models.AutoField("Cluster ID", primary_key=True, null=False, help_text="Auto-increment cluster id.")
    # OneToOneField is a ForeignKey with unique=True. Django recommends using OneToOneField instead of a ForeignKey
    # with unique=True.
    master_server = models.OneToOneField('Server', null=True, blank=True, on_delete=models.CASCADE)
    cluster_info_id = models.ForeignKey('Cluster_info', on_delete=models.CASCADE)

class Server(models.Model):
    """
    Stores information about every server created for the LoD service.
    id: the okeanos id of the server.
    hostname: the name of the server.
    public ip: the public ip of the server if any.
    private ip: the private ip of the server.
    """
    id = models.AutoField("Server ID", primary_key=True, null=False, blank=False, unique=True, default="", help_text="Server id provided by kamaki.")
    hostname = models.CharField("Hostname", null=False, blank=False, unique=True, max_length=100)
    public_ip = models.GenericIPAddressField("Public IP", null=False, blank=False, unique=True)
    private_ip = models.GenericIPAddressField("Private IP", null=False, blank=False, unique=False)

class Cluster_info(models.Model):
    """
    Stores more detailed information about every cluster created for the LoD service.
    id: a unique identifier the service creates for every cluster_info object.
    :model: models.HDFS_info
    :model: models.Yarn_info
    :model: models.Flink_info
    :model: models.Kafka_info
    cpus_per_machine: number of cpus per server.
    ram_per_machine: amount of ram per server.
    disk_per_machine: amount of disk per server.
    """
    id = models.AutoField("Cluster_info ID", primary_key=True, null=False, blank=False, unique=True, help_text="Cluster_info id autoincremented.")
    HDFS_info = models.ForeignKey('HDFS_info', null=False, blank=False, unique=True, on_delete=models.CASCADE)
    Yarn_info = models.ForeignKey('Yarn_info', null=False, blank=False, unique=True, on_delete=models.CASCADE)
    Flink_info = models.ForeignKey('Flink_info', null=False, blank=False, unique=True, on_delete=models.CASCADE)
    Kafka_info = models.ForeignKey('Kafka_info', null=False, blank=False, unique=True, on_delete=models.CASCADE)
    cpus_per_machine = models.IntegerField("cpus_per_machine", unique=False)
    ram_per_machine = models.IntegerField("ram_per_machine", unique=False)
    disk_per_machine = models.IntegerField("disk_per_machine", unique=False)

class HDFS_info(models.Model):
    """
    Stores  information about the HDFS service of a lambda cluster.
    id: a unique identifier.
    state: the state of the service.
    :model: models.State
    replication_factor: the replication number set for HDFS.
    """
    id = models.AutoField("HDFS_info ID", primary_key=True, null=False, blank=False, unique=True, help_text="HDFS_info id autoincremented.")
    state = models.ForeignKey('State', null=False, blank=False, unique=True, on_delete=models.CASCADE)
    replication_factor = models.IntegerField("replication_factor", unique=False)

class Flink_info(models.Model):
    """
    Stores  information about the Flink service of a lambda cluster.
    id: a unique identifier.
    state: the state of the service.
    :model: models.State
    :model: models.Server
    application_master: the server which runs the yarn application master.
    task_managers_number: number of task managers for Flink.
    task_manager_cpus: number of cpus per task manager.
    batch_cpus: cpus used for batch jobs.
    stream_cpus: cpus used for stream jobs.
    """
    id = models.AutoField("Flink_info ID", primary_key=True, null=False, blank=False, unique=True, help_text="Flink_info id autoincremented.")
    state = models.ForeignKey('State', null=False, blank=False, unique=True, on_delete=models.CASCADE)
    application_master = models.ForeignKey('Server', null=False, blank=False, unique=True, on_delete=models.CASCADE)
    task_managers_number = models.IntegerField("task_managers_number", unique=False)
    task_manager_memory = models.IntegerField("task_manager_memory", unique=False)
    task_manager_cpus = models.IntegerField("task_manager_cpus", unique=False)
    batch_cpus = models.IntegerField("batch_cpus", unique=False)
    stream_cpus = models.IntegerField("stream_cpus", unique=False)

class Yarn_info(models.Model):
    """
    Stores  information about the Yarn service of a lambda cluster.
    id: a unique identifier.
    state: the state of the service.
    model: models.State
    """
    id = models.AutoField("Yarn_info ID", primary_key=True, null=False, blank=False, unique=True, help_text="Yarn_info id autoincremented.")
    state = models.ForeignKey('State', null=False, blank=False, unique=True, on_delete=models.CASCADE)

class Kafka_info(models.Model):
    """
    Stores  information about the Kafka service of a lambda cluster.
    id: a unique identifier.
    state: the state of the service.
    :model: models.State
    """
    id = models.AutoField("Kafka_info ID", primary_key=True, null=False, blank=False, unique=True, help_text="Kafka_info id autoincremented.")
    state = models.ForeignKey('State', null=False, blank=False, unique=True, on_delete=models.CASCADE)

class Application(models.Model):
    """
    Stores  information about every application the service ran.
    id: a unique identifier.
    name: the name of the application.
    """
    id = models.AutoField("Aplication ID", primary_key=True, null=False, blank=False, unique=True, help_text="Aplication id autoincremented.")
    name = models.CharField('Name', max_length=100)

class Topic(models.Model):
    """
    Stores  information about every topic created for Kafka.
    id: a unique identifier.
    name: name of the topic.
    """
    id = models.AutoField("Topic ID", primary_key=True, null=False, blank=False, unique=True, help_text="Topic id autoincremented.")
    name = models.CharField('Name', max_length=100)

class PrivateNetwork(models.Model):
    """
    Stores  information about every private network created for the LoD service.
    id: a unique identifier.
    subnet: the subnet of the network.
    gateway: the gateway of the network.
    """
    id = models.AutoField("Network ID", primary_key=True, null=False, blank=False, unique=True, default="", help_text="Private network id provided by kamaki.")
    subnet = models.CharField(max_length=100)
    gateway = models.GenericIPAddressField("Gateway", null=False, blank=False, unique=False)

class State(models.Model):
    """
    Defines the state of a service running on a lambda cluster.
    id: a unique identifier.
    name: the name of the state.
    """
    id = models.AutoField("State ID", primary_key=True, null=False, blank=False, unique=True, help_text="State id autoincremented.")
    name = models.CharField('Name', max_length=100)
    STARTED = 1
    STOPPED = 2
    PENDING = 3
    STARTING = 4
    STOPPING = 5
    DESTROYING = 6
    SCALING_UP = 7
    SCALING_DOWN = 8
    DELETING = 9
    state_choices = (
        (STARTED, 'STARTED')
        (STOPPED, 'STOPPED')
        (PENDING, 'PENDING')
        (STARTING, 'STARTING')
        (STOPPING, 'STOPPING')
        (DESTROYING, 'DESTROYING')
        (SCALING_UP, 'SCALING_UP')
        (SCALING_DOWN, 'SCALING_DOWN')
        (DELETING, 'DELETING')
    )
    state = models.CharField(max_length=20, choices=state_choices, default=BUILDING)

"""
OBJECT CONNECTIONS
"""

class UserProjectConnection(models.Model):
    """
    Connection table for user and project.
    :model: models.User
    :model: models.Project
    """
    user_id = models.ForeignKey('User', null=False, blank=False, unique=False, on_delete=models.CASCADE)
    project_id = models.ForeignKey('Project', null=False, blank=False, unique=False, on_delete=models.CASCADE)

class UserClusterConnection(models.Model):
    """
    Connection table for user and cluster.
    :model: models.User
    :model: models.Cluster
    """
    user_id = models.ForeignKey('User', null=False, blank=False, unique=False, on_delete=models.CASCADE)
    cluster_id = models.ForeignKey('Cluster', null=False, blank=False, unique=False, on_delete=models.CASCADE)

class ClusterServerConnection(models.Model):
    """
    Connection table for cluster and server.
    :model: models.Server
    :model: models.Cluster
    """
    server_id = models.ForeignKey('Server', null=False, blank=False, unique=False, on_delete=models.CASCADE)
    cluster_id = models.ForeignKey('Cluster', null=False, blank=False, unique=False, on_delete=models.CASCADE)

class ClusterNetworkConnection(models.Model):
    """
    Connection table for cluster and private network.
    :model: models.PrivateNetwork
    :model: models.Cluster
    """
    network_id = models.ForeignKey('PrivateNetwork', null=False, blank=False, unique=False, on_delete=models.CASCADE)
    cluster_id = models.ForeignKey('Cluster', null=False, blank=False, unique=False, on_delete=models.CASCADE)

class ClusterProjectConnection(models.Model):
    """
    Connection table for cluster and project.
    :model: models.Cluster
    :model: models.Project
    """
    project_id = models.ForeignKey('Project', null=False, blank=False, unique=False, on_delete=models.CASCADE)
    cluster_id = models.ForeignKey('Cluster', null=False, blank=False, unique=False, on_delete=models.CASCADE)

class FlinkApplicationConnection(models.Model):
    """
    Connection table for Flink and application.
    :model: models.Flink_info
    :model: models.Application
    """
    flink_id = models.ForeignKey('Flink_info', null=False, blank=False, unique=False, on_delete=models.CASCADE)
    application_id = models.ForeignKey('Application', null=False, blank=False, unique=False, on_delete=models.CASCADE)

class KafkaTopicConnection(models.Model):
    """
    Connection table for Kafka and topic.
    :model: models.Kafka_info
    :model: models.Topic
    """
    kafka_id = models.ForeignKey('Kafka_info', null=False, blank=False, unique=False, on_delete=models.CASCADE)
    topic_id = models.ForeignKey('Topic', null=False, blank=False, unique=False, on_delete=models.CASCADE)
