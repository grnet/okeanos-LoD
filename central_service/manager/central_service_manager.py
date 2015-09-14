import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CentralServiceManager:
    """
    Class deploying dynamically the central service VM.
    It uses the kamaki API to create/destroy the actual vm, running on
    the ~okeanos infrastructure.
    """

    def central_service_create():
        """
        Creates the central service vm and installs the relevant s/w.
        :return:
        """
        raise NotImplementedError

    def central_service_destroy():
        """
        Deletes the central service vm.
        :return:
        """
        raise NotImplementedError

    def central_service_start():
        """
        Starts the central service vm if it's not running.
        :return:
        """
        raise NotImplementedError

    def central_service_stop():
        """
        Stops the central service vm if it's running.
        :return:
        """
        raise NotImplementedError
