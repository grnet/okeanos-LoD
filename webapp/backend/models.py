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

class Project(models.Model):
    """
    Stores information about every okeanos project that has been used with the LoD.
    id: the okeanos id of the project.
    description: a small description of the project.
    """
    id = models.AutoField("Project ID", primary_key=True, null=False, blank=False, unique=True, default="", help_text="Project id provided by kamaki.")
    description = models.TextField("Project Description", default="",
                                    help_text="The description of a project.")

class Server(models.Model):
    """
    Stores information about every server created for the LoD service.
    id: the okeanos id of the server.
    """
    id = models.AutoField("Server ID", primary_key=True, null=False, blank=False, unique=True, default="", help_text="Server id provided by kamaki.")

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
    master_server = models.OneToOneField(Server, null=True, blank=True, on_delete=models.CASCADE)
    cluster_info = models.CharField('Cluster info', help_text="Cluster information in xml format.")

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

"""
OBJECT CONNECTIONS
"""

class UserProjectConnection(models.Model):
    """
    Connection table for user and project.
    :model: models.User
    :model: models.Project
    """
    user_id = models.ForeignKey(User, null=False, blank=False, unique=False,
                                on_delete=models.CASCADE)
    project_id = models.ForeignKey(Project, null=False, blank=False, unique=False,
                                   on_delete=models.CASCADE)

class UserClusterConnection(models.Model):
    """
    Connection table for user and cluster.
    :model: models.User
    :model: models.Cluster
    """
    user_id = models.ForeignKey(User, null=False, blank=False, unique=False,
                                on_delete=models.CASCADE)
    cluster_id = models.ForeignKey(Cluster, null=False, blank=False, unique=False,
                                   on_delete=models.CASCADE)

class ClusterServerConnection(models.Model):
    """
    Connection table for cluster and server.
    :model: models.Server
    :model: models.Cluster
    """
    server_id = models.ForeignKey(Server, null=False, blank=False, unique=False,
                                  on_delete=models.CASCADE)
    cluster_id = models.ForeignKey(Cluster, null=False, blank=False, unique=False,
                                   on_delete=models.CASCADE)

class ClusterNetworkConnection(models.Model):
    """
    Connection table for cluster and private network.
    :model: models.PrivateNetwork
    :model: models.Cluster
    """
    network_id = models.ForeignKey(PrivateNetwork, null=False, blank=False, unique=False,
                                   on_delete=models.CASCADE)
    cluster_id = models.ForeignKey(Cluster, null=False, blank=False, unique=False,
                                   on_delete=models.CASCADE)

class ClusterProjectConnection(models.Model):
    """
    Connection table for cluster and project.
    :model: models.Cluster
    :model: models.Project
    """
    project_id = models.ForeignKey(Project, null=False, blank=False, unique=False,
                                   on_delete=models.CASCADE)
    cluster_id = models.ForeignKey(Cluster, null=False, blank=False, unique=False,
                                   on_delete=models.CASCADE)
