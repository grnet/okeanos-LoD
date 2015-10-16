class ResponseMessages:
    """
    Class that holds all the API response messages.
    """

    def __init__(self):
        pass

    short_descriptions = {
        'lambda_instance_create': "Your request to create a new lambda instance has been accepted",
        'lambda_instances_list': "Lambda instances",
        'lambda_instance_details': "Lambda instance details",
        'lambda_instance_action': "Your request has been accepted",
        'lambda_instance_destroy': "Your request to destroy the specified lambda instance has been"
                                   " accepted",

        'applications_list': "Applications",
        'application_details': "Application details",
        'application_upload': "Your request to upload the specified application has been accepted",
        'application_delete': "Your request to delete the specified application has been accepted",
        'application_deploy': "Your request to deploy the specified application has been accepted",
        'application_withdraw': "Your request to withdraw the specified application has been"
                                " accepted",
        'application_start': "Your request to start the specified application has been accepted",
        'application_stop': "Your request to stop the specified application has been accepted",
        'user_public_keys': "Public keys uploaded to ~okeanos",
        'user_okeanos_projects': "~okeanos projects",
        'vm_parameter_values': "Allowed values of parameters for creating a Lambda Instance",
    }

    lambda_instance_status_details = {
        'STARTED': "Lambda instance has been started",
        'STOPPED': "Lambda instance has been stopped",
        'PENDING': "Lambda instance installation is pending",
        'STARTING': "Lambda instance is starting",
        'STOPPING': "Lambda instance is stopping",
        'DESTROYING': "Lambda instance is being destroyed",
        'DESTROYED': "Lambda instance has been destroyed",
        'SCALING_UP': "Lambda instance is being scaled up",
        'SCALING_DOWN': "Lambda instance is being scaled down",
        'FAILED': "Lambda instance has failed",
        'CLUSTER_CREATED': "~okeanos cluster has been successfully built",
        'CLUSTER_FAILED': "~okeanos cluster build has failed",
        'INIT_DONE': "~okeanos cluster has been successfully initialized",
        'INIT_FAILED': "~okeanos cluster initialization has failed",
        'COMMONS_INSTALLED': "Common libraries have been successfully installed",
        'COMMONS_FAILED': "Common libraries installation has failed",
        'HADOOP_INSTALLED': "Apache Hadoop has been successfully installed and configured",
        'HADOOP_FAILED': "Apache Hadoop installation and configuration have failed",
        'KAFKA_INSTALLED': "Apache Kafka has been successfully installed and configured",
        'KAFKA_FAILED': "Apache Kafka installation and configuration have failed",
        'FLINK_INSTALLED': "Apache Flink has been successfully installed and configured",
        'FLINK_FAILED': "Apache Flink installation and configuration have failed"
    }

    application_status_details = {
        'UPLOADED': "Application has been successfully uploaded",
        'UPLOADING': "Application is being uploaded",
        'FAILED': "Application upload has failed"
    }
