from django.db import models
import uuid


class User(models.Model):
    """
    Stores information about every lambda-user.
    id: Auto generated id for the database.
    uuid: Unique Identifier for each user.
    """
    id = models.AutoField("id", primary_key=True)
    uuid = models.CharField("uuid", null=False, blank=False,
                            unique=True, default="", max_length=255,
                            help_text="Unique user id assigned by Astakos")

    def __unicode__(self):
        info = "User id: " + str(self.id)
        return info

    class Meta:
        verbose_name = "User"
        app_label = 'backend'
        # db_tablespace = "tables"

    def is_authenticated(self, *args):
        return True


class Token(models.Model):
    """
    Model representing the authentication token of a user.
    One-to-one relationship with the User.
    """
    user = models.OneToOneField(User, related_name='kamaki_token')
    key = models.CharField(max_length=100, null=True)
    creation_date = models.DateTimeField('Creation Date')

    def __unicode__(self):
        info = "User: " + self.user.uuid + \
            "key: " + self.key + \
            "creation_date" + str(self.creation_date)
        return info

    class Meta:
        verbose_name = "Token"
        app_label = "backend"


class LambdaInstance(models.Model):
    """
    Stores every lambda instance created for the LoD service.
    id: Auto generated id for the database.
    uuid: A unique id assigned to every Lambda Instance. This key will be used by the API
          to reference a specific Lambda Instance.
    name: The name for the specific lambda instance.
    owner: The owner of the specific lambda instance. Instance of the User model.
    status: The status of the lambda instance.
    failure_message: Message that denotes the reason of failure of the lambda instance.
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
                            default=uuid.uuid4,
                            help_text="Unique key assigned to every instance.")

    owner = models.ForeignKey(User, limit_choices_to={'is_authenticated': True},
                              related_name="lambda_instances",
                              on_delete=models.CASCADE)

    failure_message = models.TextField(default="",
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

    def __unicode__(self):
        info = "Instance id: " + str(self.id) + "\n" + \
               "Instance info: " + str(self.instance_info)
        return info

    class Meta:
        verbose_name = "Lambda Instance"
        app_label = 'backend'


class LambdaApplication(models.Model):
    """
    Table representing a lambda application running/to-run on a lambda cluster.
    id: Auto generated id for the database.
    uuid: A unique id assigned to every Lambda Application. This key will be used by the API
          to reference a specific Lambda Application.
    name: The name for the specific lambda application.
    description: A description for the specific lambda application.
    owner: The owner of the specific lambda application. Is an application of the User model.
    status: The status of the lambda application.
    failure_message: Message that denotes the reason of failure of the lambda application.
    """
    id = models.AutoField("Lambda Application ID", primary_key=True, null=False,
                          help_text="Auto-increment instance id.")
    uuid = models.UUIDField("uuid", unique=True, default=uuid.uuid4, help_text="Application uuid.")
    name = models.CharField(max_length=100, default="")
    description = models.TextField(blank="True", help_text='The description of the lambda '
                                                           'application running on an instance')
    owner = models.ForeignKey(User, default=None, on_delete=models.SET_NULL, null=True)

    UPLOADED = "0"
    UPLOADING = "1"
    FAILED = "2"
    status_choices = (
        (UPLOADED, 'UPLOADED'),
        (UPLOADING, 'UPLOADING'),
        (FAILED, 'FAILED'),
    )
    status = models.CharField(max_length=10, choices=status_choices, default="1",
                              help_text="The status of this application.")
    failure_message = models.TextField(default="",
                                       help_text="Error message regarding this application.")

    times_started = models.PositiveIntegerField(
        default=0, help_text="The count of times that this application has been started.")

    def __unicode__(self):
        unicode_str = "Application id: " + str(self.id) + "\n" + \
                      "Description: " + str(self.description)
        return unicode_str

# May be used
# class LambdaInstanceApplicationConnection(models.Model):
#     """
#     Connection table for lambda instance and project.
#     :model: models.LambdaInstance
#     :model: models.Project
#     """
#     application = models.ForeignKey(LambdaApplication, null=False, blank=False, unique=False,
#                                 on_delete=models.CASCADE)
#     lambda_instance = models.ForeignKey(LambdaInstance, null=False, blank=False, unique=False,
#                                         on_delete=models.CASCADE)
#
#     def __unicode__(self):
#         info = "Application: " + self.project + "\n" + \
#                "LambdaInstance: " + self.lambda_instance
#         return info
#
#     class Meta:
#         verbose_name = "LambdaInstanceProjectConnection"
#         app_label = 'backend'
