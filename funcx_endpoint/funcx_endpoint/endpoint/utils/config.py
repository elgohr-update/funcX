from parsl.utils import RepresentationMixin

from funcx_endpoint.executors import HighThroughputExecutor

_DEFAULT_EXECUTORS = [HighThroughputExecutor()]


class Config(RepresentationMixin):
    """Specification of FuncX configuration options.

    Parameters
    ----------

    executors : list of Executors
        A list of executors which serve as the backend for function execution.
        As of 0.2.2, this list should contain only one executor.
        Default: [HighThroughtputExecutor()]

    funcx_service_address: str
        URL address string of the funcX service to which the Endpoint should connect.
        Default: 'https://api2.funcx.org/v2'

    heartbeat_period: int (seconds)
        The interval at which heartbeat messages are sent from the endpoint to the
        funcx-web-service
        Default: 30s

    heartbeat_threshold: int (seconds)
        Seconds since the last hearbeat message from the funcx-web-service after which
        the connection is assumed to be disconnected.
        Default: 120s

    stdout : str
        Path where the endpoint's stdout should be written
        Default: ./interchange.stdout

    stderr : str
        Path where the endpoint's stderr should be written
        Default: ./interchange.stderr

    detach_endpoint : Bool
        Should the endpoint deamon be run as a detached process? This is good for
        a real edge node, but an anti-pattern for kubernetes pods
        Default: True

    log_dir : str
        Optional path string to the top-level directory where logs should be written to.
        Default: None

    globus_ep_id : str
        Globus endpoint ID. Default: None

    globus_polling_interval : float
        The interval (in seconds) to poll data transfer status. Default: 10, minimum 1

    local_data_path : str
        The local path to store the data. Default: None
    """

    def __init__(
        self,
        # Execution backed
        executors: list = _DEFAULT_EXECUTORS,
        # Connection info
        funcx_service_address="https://api2.funcx.org/v2",
        # Tuning info
        heartbeat_period=30,
        heartbeat_threshold=120,
        detach_endpoint=True,
        # Logging info
        log_dir=None,
        stdout="./endpoint.log",
        stderr="./endpoint.log",
        # Globus transfer info
        globus_ep_id=None,
        rsync_ip=None,
        rsync_username=None,
        check_rsync_auth=False,
        rsync_password_file=None,
        globus_polling_interval=10,
        local_data_path=None,
    ):

        # Execution backends
        self.executors = executors  # List of executors

        # Connection info
        self.funcx_service_address = funcx_service_address

        # Tuning info
        self.heartbeat_period = heartbeat_period
        self.heartbeat_threshold = heartbeat_threshold
        self.detach_endpoint = detach_endpoint

        # Logging info
        self.log_dir = log_dir
        self.stdout = stdout
        self.stderr = stderr

        # Globus transfer info
        self.globus_ep_id = globus_ep_id
        self.globus_polling_interval = globus_polling_interval
        if local_data_path is not None and not local_data_path.endswith("/"):
            local_data_path = local_data_path+"/"
        self.local_data_path = local_data_path

        # Since interchange is lanuched as a subprocess, we need to pass a string-format
        # parameter to the interchange to build a instance of DataTransferClient
        # Rsync info
        self.rsync_ip = rsync_ip
        self.rsync_username = rsync_username
        self.check_rsync_auth = check_rsync_auth
        if rsync_password_file is not None:
            import os
            rsync_password_file = os.path.abspath(rsync_password_file)
        self.rsync_password_file = rsync_password_file
