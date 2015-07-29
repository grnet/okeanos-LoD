from django.db import models

class User(models.Model):
    id = models.CharField("UUID", null=False, blank=False, unique=True, default="", max_length=255,
                          help_text="Unique user id asign by Astakos")
    token = models.CharField("Okeanos Token", null=True, blank=True, unique=True, default="", max_length=64,
                             help_text="Token provided by ~okeanos.")

class Project(models.Model):
    id = models.AutoField("Project ID", primary_key=True, null=False, blank=False, unique=True, default="", help_text="Project id provided by kamaki.")
    description = models.TextField("Project Description", null=True, blank=True, unique=False, default="",
                                   help_text="The description of a project.")

class Cluster(models.Model):
    id = models.AutoField("Cluster ID", primary_key=True, null=False, help_text="Auto-increment cluster id.")
    master_server = models.ForeignKey('Server', null=True, blank=True, unique=True, on_delete=models.CASCADE)

class Server(models.Model):
    id = models.AutoField("Server ID", primary_key=True, null=False, blank=False, unique=True, default="", help_text="Server id provided by kamaki.")
    hostname = models.CharField(max_length=100)
    public_ip = models.CharField(max_length=100)
    private_ip = models.CharField(max_length=100)

class PrivateNetwork(models.Model):
    id = models.AutoField("Network ID", primary_key=True, null=False, blank=False, unique=True, default="", help_text="Private network id provided by kamaki.")
    subnet = models.CharField(max_length=100)
    gateway = models.CharField(max_length=100)

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
    network_id = models.ForeignKey('Project', null=False, blank=False, unique=False, on_delete=models.CASCADE)
    cluster_id = models.ForeignKey('Cluster', null=False, blank=False, unique=False, on_delete=models.CASCADE)
