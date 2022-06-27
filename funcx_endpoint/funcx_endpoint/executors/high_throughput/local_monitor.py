import logging
import threading
import time
from funcx_endpoint.executors.high_throughput.system_info_util import SystemInfoUtil
logger = logging.getLogger(__name__)


class CPUInformation:

    def __init__(self, cores, user_system):
        self.cores = cores
        self.user_system = user_system


class LocalMonitor:

    def __init__(self, monitor_interval=1):
        self._monitor_thread = threading.Thread(target=self.start,
                                                args=(),
                                                name="Local-Monitor-Thread")
        self.monitor_interval = monitor_interval

    """
    Starting stage:
        1.gather the basic information of the endpoint. e.g. CPU cores, Memory size, Disk Size
    """

    def start(self):
        while True:
            time.sleep(self.monitor_interval)



        return

    @staticmethod
    def get_system_info():
        cpu_info = SystemInfoUtil.get_current_cpu_info()
        mem_info = SystemInfoUtil.get_current_mem_info()
        system_info = {**cpu_info, **mem_info}
        pass

    # TODO information can be stored at the funcx-webservice
    def submit_to_webservice(self):
        pass
