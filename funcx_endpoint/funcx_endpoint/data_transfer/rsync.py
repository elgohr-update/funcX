import subprocess
import logging
import concurrent.futures
from functools import partial
from funcx_endpoint.data_transfer.data_transfer_client import DataTransferClient
import uuid
import os

logger = logging.getLogger("interchange")

class RsyncTransferClient(DataTransferClient):
    def __init__(self, local_path=".", dst_ep=None,username=os.getlogin(),**kwargs):
        # all connected endpoints should be authenticated by ssh manually
        self.local_path = local_path # local path to store the data
        self.dst_ep = dst_ep      # the ip address of the host of funcx endpoint
        self.username = username  # username of the remote host
        self.transfer_tasks = {}  # task_id: future object, task id is a random uuid

    def generate_rsync_command(self, src_username, src_ip, src_path, basename, recursive=False):
        r_parm = "-avz" if not recursive else "-avzr"
        rsync_command = f"rsync {r_parm} {src_username}@{src_ip}:{src_path} {self.local_path}"
        return rsync_command

    # transfer a file by rsync, return a future object
    def transfer(self, src_username, src_ip, src_path, basename, recursive=False):
        cmd = self.generate_rsync_command(src_username, src_ip, src_path, basename, recursive)
        with concurrent.futures.ProcessPoolExecutor() as executor:
            logger.info(f"[Rsync] transfer command: {cmd}")
            future = executor.submit(subprocess.run, cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            task_id = str(uuid.uuid4())
            task = {'task_id': task_id, 'status': 'ACTIVE', 'future': future, 'stdout': None, 'stderr': None}
            self.transfer_tasks[task_id] = task
            future.add_done_callback(partial(self._transfer_done, task=task_id))
            return future  

    def _transfer_done(self, future, task):
        try:
            transfer_result = future.result()
            if transfer_result.returncode == 0:
                self.transfer_tasks[task]['status'] = 'SUCCEEDED'
                logger.info("[Rsync] Transfer succeed {task}")
            else:
                self.transfer_tasks[task]['status'] = 'FAILED' 
            self.transfer_tasks[task]['stdout'] = transfer_result.stdout
            self.transfer_tasks[task]['stderr'] = transfer_result.stderr          
        except Exception as e:
            self.transfer_tasks[task]['status'] = 'FAILED'
            self.transfer_tasks[task]['stdout'] = transfer_result.stdout
            self.transfer_tasks[task]['stderr'] = transfer_result.stderr  
            logger.info("Rsync transfer failed: ", e)
        return

    def status(self, task):
        """
        Keep consistent with the return value of GlobusTransferClient.status()
        status: ACTIVE, SUCCEEDED, FAILED
        INACTIVE status is not supported, only for globustransfer
        """
        return task['status']

    def get_event(self, task):
        return task['stderr']

    def cancel(self, task):
        del self.transfer_tasks[task['task_id']]
        logger.info(f"[Rsync] canceled the task : {task['task_id']}")
