# from django.core.exceptions import ObjectDoesNotExist
# from models import User, Project, Cluster, Server, ClusterProjectConnection, PrivateNetwork
#
#
# """
# User
# """
#
#
# def get_User(user_id):
#     """
#     :returns: User with this id,returns None if User does not exists.
#     """
#     try:
#         user = User.objects.get(id=user_id)
#         return user
#     except ObjectDoesNotExist:
#         return None
#
#
# def add_User(user_id):
#     """
#     Add a new User to the DB.
#     :param id: the id provided by ~okeanos for this user.
#     """
#     user = User(id=user_id)
#     user.save()
#
#
# def delete_User(user_id):
#     """
#     Deletes the user with this id.
#     :returns: True if successfull,otherwise False.
#     """
#     user = get_User(user_id)
#     if user is not None:
#         user.delete()
#         return True
#     return False
#
# """
# Project
# """
#
#
# def get_Project(project_id):
#     """
#     :returns: Project with this id,returns None if Project does not exists.
#     """
#     try:
#         project = Project.objects.get(id=project_id)
#         return project
#     except DoesNotExist:
#         return None
#
#
# def add_Project(project_id, description=""):
#     """
#     Add a new Project to the DB.
#     :param id: the id provided by ~okeanos for the project.
#     """
#     project = Project(id=project_id, description=description)
#     project.save()
#
#
# def update_Project(project_id, description=""):
#     """
#     Update project to the DB.
#     :param id: the id of the project.
#     :param description: the new description of the project.
#     """
#     project = get_Project(project_id)
#     project.description = description
#     project.save()
#
#
# def get_Projects():
#     """
#     :returns: All the projects in DB.
#     """
#     return Project.objects.all()
#
#
# def get_Project_By_Cluster(cluster_id):
#     """
#     :returns: All the projects in DB that were used for this cluster.
#     """
#     return ClusterProjectConnection.objects.filter(cluster_id=cluster_id)
#
#
# def delete_Project(project_id):
#     """
#     Deletes the project with this id.
#     :returns: True if successfull,otherwise False.
#     """
#     project = get_Project(project_id)
#     if project is not None:
#         project.delete()
#         return True
#     return False
#
#
# """
# Cluster
# """
#
#
# def get_Cluster(cluster_id):
#     """
#     :returns: Cluster with this id,returns None if Cluster does not exists.
#     """
#     try:
#         cluster = Cluster.objects.get(id=cluster_id)
#         return cluster
#     except DoesNotExist:
#         return None
#
#
# def add_Cluster(cluster_info=""):
#     """
#     Add a new Cluster to the DB.
#     :param cluster_info: the content of the xml file containing information about
#     the servers and services.
#     """
#     cluster = Cluster(cluster_info=cluster_info)
#     cluster.save()
#
#
# def update_Cluster(cluster_id, cluster_info=""):
#     """
#     Update cluster to the DB.
#     :param id: the id of the cluster.
#     :param cluster_info: the content of the xml file containing information about
#     the servers and services.
#     """
#     cluster = get_Cluster(cluster_id)
#     cluster.description = description
#     cluster.save()
#
#
# def get_Clusters():
#     """
#     :returns: All clusters from the DB.
#     """
#     return Cluster.objects.all()
#
#
# def get_Project_By_Project(project_id):
#     """
#     :returns: All the clusters in DB that were used for project.
#     """
#     return ClusterProjectConnection.objects.filter(project_id=project_id)
#
#
# def delete_Cluster(cluster_id):
#     """
#     Deletes the cluster with this id.
#     :returns: True if successfull,otherwise False.
#     """
#     cluster = get_Cluster(cluster_id)
#     if cluster is not None:
#         cluster.delete()
#         return True
#     return False
#
#
# """
# Server
# """
#
#
# def get_Server(server_id=1):
#     """
#     :returns: Server with this id,returns None if Server does not exists.
#     """
#     try:
#         server = Server.objects.get(id=server_id)
#         return server
#     except DoesNotExist:
#         return None
#
#
# def get_Servers_by_Cluster(cluster_id=1):
#     """
#     :returns: Servers that belong to this cluster,returns None if no Servers are found.
#     """
#     cluster = Cluster.objects.get(id=cluster_id)
#     return Server.objects.filter(cluster=cluster)
#
#
# def add_Server(server_id=1, cpus=1, disk=20, ram=2, pub_ip=None, priv_ip=None,
#                Cluster=None, hostname=""):
#     """
#     Add a new Server to the DB.
#     :param server_id: the id provided by ~okeanos when the server is created.
#     :param cpus: number of cpus.
#     :param ram: amount of ram.
#     :param disk: amount of disk.
#     :param pub-ip: public ip of server.
#     :param priv_ip: private ip of server.
#     :param hostname: hostname of server.
#
#     """
#     server = Server(id=server_id, cpus=cpus, disk=disk, ram=ram, pub_ip=pub_ip,
#                     priv_ip=priv_ip, Cluster=Cluster, hostname=hostname)
#     server.save()
#
#
# def update_Server(server_id, cluster=None):
#     """
#     Update server to the DB.
#     :param id: the id of the server.
#     :parma cluster: the new cluster that the server belongs to.
#     """
#     server = get_Server(server_id)
#     server.cluster = cluster
#     server.save()
#
#
# def delete_Server(server_id):
#     """
#     Deletes the server with this id.
#     :returns: True if successfull,otherwise False.
#     """
#     server = get_Server(server_id)
#     if server is not None:
#         server.delete()
#         return True
#     return False
#
#
# """
# PrivateNetwork
# """
#
#
# def get_PrivateNetwork(pn_id):
#     """
#     :returns: PrivateNetwork with this id,returns None if PrivateNetwork does not exists.
#     """
#     try:
#         pn = PrivateNetwork.objects.get(id=pn_id)
#         return pn
#     except DoesNotExist:
#         return None
#
#
# def add_PrivateNetwork(pn_id, subnet='', gateway=None, cluster=None):
#     """
#     Add a new private network to the DB.
#     :param pn_id: the id provided by ~okeanos when the private network is created.
#     :param subnet: the subnet of the network.
#     :param gateway: the gateway of the network.
#     :param cluster: the cluster the network belongs to.
#     """
#     pn = PrivateNetwork(id=pn_id, subnet=subnet, gateway=gateway, cluster=cluster)
#     pn.save()
#
#
# def update_PrivateNetwork(pn_id, cluster=None):
#     """
#     Update private network to the DB.
#     :param id: the id of the private network.
#     :parma cluster: the new cluster that the network belongs to.
#     """
#     pn = get_PrivateNetwork(pn_id)
#     pn.cluster = cluster
#     pn.save()
#
#
# def get_PrivateNetwork_by_Cluster(pn_id):
#     """
#     :returns: PrivateNetwork that belong to this cluster,returns None
#     if no PrivateNetwork is found.
#     """
#     cluster = Cluster.objects.get(id=pn_id)
#     return PrivateNetwork.objects.filter(cluster=cluster)
#
#
# def delete_PrivateNetwork(pn_id):
#     """
#     Deletes the Private Network with this id.
#     :returns: True if successfull,otherwise False.
#     """
#     pn = get_PrivateNetwork(pn_id)
#     if pn is not None:
#         pn.delete()
#         return True
#     return False
#
#
# """
# ClusterProjectConnection
# """
#
#
# def add_ClusterProjectConnection(project, cluster):
#     """
#     Add a new cluster project connection to the DB.
#     :param cluster: the project.
#     :param project: the cluster.
#     """
#     con = ClusterProjectConnection(project=project, cluster=cluster)
#     con.save()
