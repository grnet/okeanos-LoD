from django.core.exceptions import ObjectDoesNotExist
from models import *


"""
User
"""

def get_User(user_id=1):
    """
    :returns: User with this id,returns None if User does not exists.
    """
    try:
        user = User.objects.get(id=user_id)
        return user
    except ObjectDoesNotExist:
        return None

def add_User(user_id=1):
    """
    Add a new User to the DB.
    :param id: the id provided by ~okeanos for this user.
    """
    user = User(id=user_id)
    user.save()


"""
Project
"""

def get_Project(project_id=1):
    """
    :returns: Project with this id,returns None if Project does not exists.
    """
    try:
        project = Project.objects.get(id=project_id)
        return project
    except DoesNotExist:
        return None

def add_Project(project_id=1, description=""):
    """
    Add a new Project to the DB.
    :param id: the id provided by ~okeanos for the project.
    """
    project = Project(id=project_id, description=description)
    cluster.save()

"""
Cluster
"""

def get_Cluster(cluster_id=1):
    """
    :returns: Cluster with this id,returns None if Cluster does not exists.
    """
    try:
        cluster = Cluster.objects.get(id=cluster_id)
        return cluster
    except DoesNotExist:
        return None

def add_Cluster(cluster_info=""):
    """
    Add a new Cluster to the DB.
    :param cluster_info: the content of the xml file containing information about
    the servers and services.
    """
    cluster = Cluster(cluster_info=cluster_info)
    cluster.save()

def get_Clusters():
    """
    :returns: All clusters from the DB.
    """
    return Cluster.objects.all()

def get_Cluster_by_PrivateNetwork(pn_id=1):
    """
    :returns: Cluster that contains this private network,returns None if no Cluster is found.
    """
    return ClusterNetworkConnection.objects.filter(id=pn_id)



"""
Server
"""

def get_Server(server_id=1):
    """
    :returns: Server with this id,returns None if Server does not exists.
    """
    try:
        server = Server.objects.get(id=server_id)
        return server
    except DoesNotExist:
        return None

def get_Servers_by_Cluster(cluster_id=1):
    """
    :returns: Servers that belong to this cluster,returns None if no Servers are found.
    """
    cluster = Cluster.objects.get(id=cluster_id)
    return Server.objects.filter(cluster=cluster)

def add_Server(server_id=1, cpus=1, disk=20, ram=2, pub_ip=None, priv_ip=None,
               Cluster=None):
    """
    Add a new Server to the DB.
    :param server_id: the id provided by ~okeanos when the server is created.
    """
    server = Server(id=server_id, cpus=cpus, disk=disk, ram=ram, pub_ip=pub_ip,
                    priv_ip=priv_ip, Cluster=Cluster)
    server.save()


"""
PrivateNetwork
"""

def get_PrivateNetwork(pn_id=1):
    """
    :returns: PrivateNetwork with this id,returns None if PrivateNetwork does not exists.
    """
    try:
        pn = PrivateNetwork.objects.get(id=pn_id)
        return pn
    except DoesNotExist:
        return None

def add_PrivateNetwork(pn_id=1, subnet='', gateway=None):
    """
    Add a new private network to the DB.
    :param pn_id: the id provided by ~okeanos when the private network is created.
    """
    pn = PrivateNetwork(id=pn_id, subnet=subnet, gateway=gateway)
    pn.save()

def get_PrivateNetwork_by_Cluster(cluster_id=1):
    """
    :returns: PrivateNetwork that belong to this cluster,returns None if no PrivateNetwork is found.
    """
    return ClusterNetworkConnection.objects.filter(cluster_id=cluster_id)

if __name__ == "__main__":
    settings.configure()
    django.setup()
