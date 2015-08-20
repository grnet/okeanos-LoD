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
    id = models.CharField("UUID", primary_key=True, null=False, blank=False,
                          unique=True, default="", max_length=255,
                          help_text="Unique user id asign by Astakos")

    def __unicode__(self):
        return str(self.id)

    class Meta:
        verbose_name = "User"
        app_label = 'backend'
        db_tablespace = "tables"


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
        return self.id

    class Meta:
        verbose_name = "Project"
        app_label = 'backend'

class Cluster(models.Model):
    """
    Stores every cluster created for the LoD service.
    id: a unique identifier the service creates for every cluster.
    :model: models.Server
    :model: models.Cluster_info
    """
    id = models.AutoField("Cluster ID", primary_key=True, null=False,
                          help_text="Auto-increment cluster id.")
    # OneToOneField is a ForeignKey with unique=True. Django recommends
    # using OneToOneField instead of a ForeignKey
    # with unique=True.
    # master_server = models.OneToOneField(Server, null=True, blank=True, on_delete=models.CASCADE)
    cluster_info = models.TextField('Cluster info', help_text="Cluster information in xml format.")

    def __unicode__(self):
        info = "Cluster id: " + str(self.id) + "\n" + \
               "Cluster info: " + str(self.cluster_info)
        return info

    class Meta:
        verbose_name = "Cluster"
        app_label = 'backend'

class Server(models.Model):
    """
    Stores information about every server created for the LoD service.
    id: the okeanos id of the server.
    """
    id = models.AutoField("Server ID", primary_key=True, null=False, blank=False,
                          unique=True, default="",
                          help_text="Server id provided by kamaki.")
    cpus = models.IntegerField("CPUs", null=True, help_text="Number of cpus.")
    ram = models.IntegerField("RAM", null=True, help_text="Amount of ram.")
    disk = models.IntegerField("Hard Drive", null=True, help_text="Amount of disk space.")
    pub_ip = models.GenericIPAddressField("Public ip", null=True, help_text="Public ip of server.")
    priv_ip = models.GenericIPAddressField("Private ip", null=True,
                                           help_text="Private ip of server.")
    cluster = models.ForeignKey(Cluster, null=False, blank=False, unique=False,
                                default=None, on_delete=models.CASCADE)

    def __unicode__(self):
        info = "Server id: " + str(self.id) + "\n" + \
               "CPUs: " + str(self.cpus) + "\n" + \
               "Hard Drive: " + str(self.disk) + "\n" + \
               "RAM: " + str(self.ram) + "\n" + \
               "Public ip: " + str(self.pub_ip) + "\n" + \
               "Private ip: " + str(self.priv_ip) + \
               "Cluster id: " + str(self.cluster.id)
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
    """
    id = models.AutoField("Network ID",
                          primary_key=True, null=False, blank=False,
                          unique=True, default="",
                          help_text="Private network id provided by kamaki.")
    subnet = models.CharField(max_length=100)
    gateway = models.GenericIPAddressField("Gateway", null=False,
                                           blank=False, unique=False)

    def __unicode__(self):
        return self.id

    class Meta:
        verbose_name = "PrivateNetwork"
        app_label = 'backend'

"""
OBJECT CONNECTIONS
"""

"""
class ClusterServerConnection(models.Model):

    Connection table for cluster and server.
    :model: models.Server
    :model: models.Cluster

    server = models.ForeignKey(Server, null=False, blank=False, unique=False,
                                  on_delete=models.CASCADE)
    cluster = models.ForeignKey(Cluster, null=False, blank=False, unique=False,
                                   on_delete=models.CASCADE)

    def __unicode__(self):
        info = "Cluster : " + str(self.cluster) + "\n" + \
               "Server: " + str(self.server)
        return info

    class Meta:
        verbose_name = "ClusterServerConnection"
        app_label = 'backend'
"""

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

    class Meta:
        verbose_name = "ClusterNetworkConnection"
        app_label = 'backend'

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

    class Meta:
        verbose_name = "ClusterProjectConnection"
        app_label = 'backend'
