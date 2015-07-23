from django.db import models

class User(models.Model):
    id = models.CharField("UUID", null=False, blank=False, unique=True, default="", max_length=255,
                          help_text="Unique user id asign by Astakos")
    token = models.CharField("Okeanos Token", null=True, blank=True, unique=True, default="", max_length=64,
                             help_text="Token provided by ~okeanos.")

class Projects(models.Model):
    id = models.AutoField("Project ID", primary_key=True, null=False, help_text="Auto-increment project id.")
    description = models.TextField("Project Description", null=True, blank=True, unique=False, default="",
                                   help_text="The description of a project.")

class Clusters(models.Model):
    id = models.AutoField("Cluster ID", primary_key=True, null=False, help_text="Auto-increment cluster id.")

class Cluster(models.Model):
    id = models.ForeignKey('Clusters', primary_key=True, null=False, blank=False, unique=True, on_delete=models.CASCADE)
    master_id = models.CharField(max_length=100)
    slaves_id = models.CharField(max_length=100)
    vpn = models.CharField(max_length=100)
    ips_id = models.CharField(max_length=100)

class UserProjectConnection(models.Model):
    user_id = models.ForeignKey('User', null=False, blank=False, unique=False, on_delete=models.CASCADE)
    project_id = models.ForeignKey('Projects', null=False, blank=False, unique=False, on_delete=models.CASCADE)

class UserClusterConnection(models.Model):
    user_id = models.ForeignKey('User', null=False, blank=False, unique=False, on_delete=models.CASCADE)
    cluster_id = models.ForeignKey('Clusters', null=False, blank=False, unique=False, on_delete=models.CASCADE)