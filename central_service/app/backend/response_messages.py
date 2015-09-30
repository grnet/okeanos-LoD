class ResponseMessages:
    """
    Class that holds all the API response messages.
    """

    def __init__(self):
        pass

    short_descriptions = {
        'lambda_instances_create': "Your request to create a "
                                   "new lambda instance has been accepted.",
        'lambda_instances_list': "Lambda instances.",
        'lambda_instances_details': "Lambda instance details.",
        'lambda_instances_action': "Your request has been accepted.",
        'lambda_instances_delete': "Your request to destroy the specified lambda instance has been"
                                   " accepted.",
        'lambda_instances_count': "Lambda instances count.",
        'lambda_instances_update': "Lambda instances status update accepted.",

        'lambda_applications_create': "Your request to create the specified application"
                                      " has been accepted.",
        'lambda_applications_list': "Lambda Applications.",
        'lambda_applications_details': "Lambda Application details.",
        'lambda_applications_delete': "Your request to delete the specified application"
                                      " has been accepted.",
        'lambda_applications_count': 'Lambda applications count.',
        'lambda_applications_update': "Lambda application status update accepted.",

        'lambda_users_count': 'Lambda Users count on ~okeanos infrastructure.'
    }

    lambda_instance_status_details = {
        'STARTED': "Lambda instance has been started.",
        'STOPPED': "Lambda instance has been stopped.",
        'PENDING': "Lambda instance installation is pending.",
        'STARTING': "Lambda instance is starting.",
        'STOPPING': "Lambda instance is stopping.",
        'DESTROYING': "Lambda instance is being destroyed.",
        'DESTROYED': "Lambda instance has been destroyed.",
        'SCALING_UP': "Lambda instance is being scaled up.",
        'SCALING_DOWN': "Lambda instance is being scaled down.",
        'FAILED': "Lambda instance has failed.",
        'CLUSTER_CREATED': "~okeanos cluster has been successfully built.",
        'CLUSTER_FAILED': "~okeanos cluster build has failed.",
        'INIT_DONE': "~okeanos cluster has been successfully initialized.",
        'INIT_FAILED': "~okeanos cluster initialization has failed.",
        'COMMONS_INSTALLED': "Common libraries have been successfully installed.",
        'COMMONS_FAILED': "Common libraries installation has failed.",
        'HADOOP_INSTALLED': "Apache Hadoop has been successfully installed and configured.",
        'HADOOP_FAILED': "Apache Hadoop installation and configuration have failed.",
        'KAFKA_INSTALLED': "Apache Kafka has been successfully installed and configured.",
        'KAFKA_FAILED': "Apache Kafka installation and configuration have failed.",
        'FLINK_INSTALLED': "Apache Flink has been successfully installed and configured.",
        'FLINK_FAILED': "Apache Flink installation and configuration have failed."
    }

    application_status_details = {
        'UPLOADED': "Application has been successfully uploaded.",
        'UPLOADING': "Application is being uploaded.",
        'FAILED': "Application upload has failed."
    }
