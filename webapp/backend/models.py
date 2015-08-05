from django.db import models

"""
OBJECTS
"""

class User(models.Model):
    id = models.CharField("UUID", primary_key=True, null=False, blank=False, unique=True, default="", max_length=255, help_text="Unique user id asign by Astakos")
    token = models.CharField("Okeanos Token", null=True, blank=True, unique=True, default="", max_length=64, help_text="Token provided by ~okeanos.")

class Project(models.Model):
    id = models.AutoField("Project ID", primary_key=True, null=False, blank=False, unique=True, default="", help_text="Project id provided by kamaki.")
    description = models.TextField("Project Description", null=True, blank=True, unique=False, default="", help_text="The description of a project.")

class Cluster(models.Model):
    id = models.AutoField("Cluster ID", primary_key=True, null=False, help_text="Auto-increment cluster id.")
    # OneToOneField is a ForeignKey with unique=True. Django recommends using OneToOneField instead of a ForeignKey
    # with unique=True.
    master_server = models.OneToOneField('Server', null=True, blank=True, on_delete=models.CASCADE)
    cluster_info_id = models.OneToOneField('Cluster_info', null=True, blank=True, on_delete=models.CASCADE)

class Server(models.Model):
    id = models.AutoField("Server ID", primary_key=True, null=False, blank=False, unique=True, default="", help_text="Server id provided by kamaki.")
    hostname = models.CharField("Hostname", null=False, blank=False, unique=True, max_length=100)
    public_ip = models.GenericIPAddressField("Public IP", null=False, blank=False, unique=True)
    private_ip = models.GenericIPAddressField("Private IP", null=False, blank=False, unique=False)

class Cluster_info(models.Model):
    id = models.AutoField("Cluster_info ID", primary_key=True, null=False, blank=False, unique=True, help_text="Cluster_info id autoincremented.")
    HDFS_info = models.ForeignKey('HDFS_info', null=False, blank=False, unique=True, on_delete=models.CASCADE)
    Yarn_info = models.ForeignKey('Yarn_info', null=False, blank=False, unique=True, on_delete=models.CASCADE)
    Flink_info = models.ForeignKey('Flink_info', null=False, blank=False, unique=True, on_delete=models.CASCADE)
    Kafka_info = models.ForeignKey('Kafka_info', null=False, blank=False, unique=True, on_delete=models.CASCADE)
    cpus_per_machine = models.IntegerField("cpus_per_machine", unique=False)
    ram_per_machine = models.IntegerField("ram_per_machine", unique=False)
    disk_per_machine = models.IntegerField("disk_per_machine", unique=False)

class HDFS_info(models.Model):
    id = models.AutoField("HDFS_info ID", primary_key=True, null=False, blank=False, unique=True, help_text="HDFS_info id autoincremented.")
    state = models.ForeignKey('State', null=False, blank=False, unique=True, on_delete=models.CASCADE)
    replication_factor = models.IntegerField("replication_factor", unique=False)

class Flink_info(models.Model):
    id = models.AutoField("Flink_info ID", primary_key=True, null=False, blank=False, unique=True, help_text="Flink_info id autoincremented.")
    state = models.ForeignKey('State', null=False, blank=False, unique=True, on_delete=models.CASCADE)
    application_master = models.ForeignKey('Server', null=False, blank=False, unique=True, on_delete=models.CASCADE)
    task_managers_number = models.IntegerField("task_managers_number", unique=False)
    task_manager_memory = models.IntegerField("task_manager_memory", unique=False)
    task_manager_cpus = models.IntegerField("task_manager_cpus", unique=False)
    batch_cpus = models.IntegerField("batch_cpus", unique=False)
    stream_cpus = models.IntegerField("stream_cpus", unique=False)

class Yarn_info(models.Model):
    id = models.AutoField("Yarn_info ID", primary_key=True, null=False, blank=False, unique=True, help_text="Yarn_info id autoincremented.")
    state = models.ForeignKey('State', null=False, blank=False, unique=True, on_delete=models.CASCADE)

class Kafka_info(models.Model):
    id = models.AutoField("Kafka_info ID", primary_key=True, null=False, blank=False, unique=True, help_text="Kafka_info id autoincremented.")
    state = models.ForeignKey('State', null=False, blank=False, unique=True, on_delete=models.CASCADE)

class Application(models.Model):
    id = models.AutoField("Aplication ID", primary_key=True, null=False, blank=False, unique=True, help_text="Aplication id autoincremented.")
    name = models.CharField('Name', max_length=100)

class Topic(models.Model):
    id = models.AutoField("Topic ID", primary_key=True, null=False, blank=False, unique=True, help_text="Topic id autoincremented.")
    name = models.CharField('Name', max_length=100)

class State(models.Model):
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

class PrivateNetwork(models.Model):
    id = models.AutoField("Network ID", primary_key=True, null=False, blank=False, unique=True, default="", help_text="Private network id provided by kamaki.")
    subnet = models.CharField(max_length=100)
    gateway = models.GenericIPAddressField("Gateway", null=False, blank=False, unique=False)

class UserProjectConnection(models.Model):
    user_id = models.ForeignKey('User', null=False, blank=False, unique=False, on_delete=models.CASCADE)
    project_id = models.ForeignKey('Project', null=False, blank=False, unique=False, on_delete=models.CASCADE)

class UserClusterConnection(models.Model):
    user_id = models.ForeignKey('User', null=False, blank=False, unique=False, on_delete=models.CASCADE)
    cluster_id = models.ForeignKey('Cluster', null=False, blank=False, unique=False, on_delete=models.CASCADE)

class ClusterServerConnection(models.Model):
    server_id = models.ForeignKey('Server', null=False, blank=False, unique=False, on_delete=models.CASCADE)
    cluster_id = models.ForeignKey('Cluster', null=False, blank=False, unique=False, on_delete=models.CASCADE)

class ClusterNetworkConnection(models.Model):
    network_id = models.ForeignKey('PrivateNetwork', null=False, blank=False, unique=False, on_delete=models.CASCADE)
    cluster_id = models.ForeignKey('Cluster', null=False, blank=False, unique=False, on_delete=models.CASCADE)

class ClusterProjectConnection(models.Model):
    project_id = models.ForeignKey('Project', null=False, blank=False, unique=False, on_delete=models.CASCADE)
    cluster_id = models.ForeignKey('Cluster', null=False, blank=False, unique=False, on_delete=models.CASCADE)

class FlinkApplicationConnection(models.Model):
    flink_id = models.ForeignKey('Flink_info', null=False, blank=False, unique=False, on_delete=models.CASCADE)
    application_id = models.ForeignKey('Application', null=False, blank=False, unique=False, on_delete=models.CASCADE)

class KafkaTopicConnection(models.Model):
    kafka_id = models.ForeignKey('Kafka_info', null=False, blank=False, unique=False, on_delete=models.CASCADE)
    topic_id = models.ForeignKey('Topic', null=False, blank=False, unique=False, on_delete=models.CASCADE)
