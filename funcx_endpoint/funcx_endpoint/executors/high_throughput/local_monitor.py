import logging
import threading
import time
from funcx_endpoint.executors.high_throughput.system_info_util import SystemInfoUtil
from queue import Queue
logger = logging.getLogger(__name__)

class LocalMonitor:

    def __init__(self, monitor_interval=1,):
        self._kill_event = threading.Event()
        self._monitor_thread = threading.Thread(target=self.start,
                                                args=(self._kill_event,),
                                                name="Local-Monitor-Thread")
        self.monitor_interval = monitor_interval
        self.threading_lock = threading.Lock()
        self.info_list = []
        self.max_size = 10


    """
    Starting stage:
        1.gather the basic information of the endpoint. e.g. CPU cores, Memory size, Disk Size
    """

    def start(self, kill_event):
        while not kill_event.is_set():
            time.sleep(self.monitor_interval)
            info = self.get_system_info()
            with self.threading_lock:
                while len(self.info_list) >= self.max_size > 0:
                    self.info_list.pop(0)
                self.info_list.append(info)
        return

    @staticmethod
    def get_system_info():
        cpu_info = SystemInfoUtil.get_current_cpu_info(interval=0.1)
        mem_info = SystemInfoUtil.get_current_mem_info()
        system_info = {**cpu_info, **mem_info}
        return system_info

    def get_avg_info(self):
        with self.threading_lock:
            res = {}
            for d in self.info_list:
                for k, v in d.items():
                    if k in res.keys():
                        res[k] += v
                    else:
                        res[k] = v
            for k in res.keys():
                res[k] = res[k] / len(self.info_list)
        return res

    # TODO information can be stored at the funcx-webservice
    def submit_to_webservice(self):
        pass
