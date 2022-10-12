import subprocess
import logging
import concurrent.futures
from functools import partial
from urllib.parse import urlparse
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

    def generate_rsync_command(self, rsync_username, rsync_ip, src_path, basename, recursive=False):
        r_parm = "-avz" if not recursive else "-avzr"
        rsync_command = f"rsync {r_parm} {rsync_username}@{rsync_ip}:{src_path} {self.local_path}"
        return rsync_command

    # transfer a file by rsync, return a future object
    def transfer(self, transfer_task_info):
        # resolve the transfer_task_info generted by the parse_url

        rsync_ip = transfer_task_info['rsync_ip']
        rsync_username = transfer_task_info['rsync_username']
        src_path = transfer_task_info['src_path']
        basename = transfer_task_info['basename']
        recursive = transfer_task_info['recursive']

        cmd = self.generate_rsync_command(rsync_username, rsync_ip, src_path, basename, recursive)
        with concurrent.futures.ProcessPoolExecutor() as executor:
            logger.info(f"[Rsync] transfer command: {cmd}")
            future = executor.submit(subprocess.run, cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            task_id = str(uuid.uuid4())
            task = {'task_id': task_id, 'status': 'ACTIVE', 'future': future, 'stdout': None, 'stderr': None}
            self.transfer_tasks[task_id] = task
            future.add_done_callback(partial(self._transfer_done, task=task_id))
             # aggregate the task info
            task["src_ep"] = f"{rsync_username}:{rsync_ip}"
            task["src_path"] = src_path
            task["dst_path"] = f"{self.local_path}/{basename}"
            task["dst_ep"] = f"{self.dst_ep}:{self.username}"
            logger.info(f"[Rsync] transfer task: {task}")
            return task  

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

    def check_same(self, transfer_task_info):
        rsync_ip = transfer_task_info['rsync_ip']
        rsync_username = transfer_task_info['rsync_username']
        src_path = transfer_task_info['src_path']
        recursive = transfer_task_info['recursive']
        src_dir = src_path
        basename = os.path.basename(src_path)
        # get the directory of source file
        # if the object is not directory, reduce the file name
        # only fetch the dir path
        if not recursive and len(basename) > 0:
            src_dir = src_dir[:-len(basename)]
        if rsync_ip == self.dst_ep and rsync_username == self.username and src_dir== self.local_path:
            return True
        else:
            return False

    @staticmethod
    def parse_url(combined_url):
        """Parse a URL into a list containing dicts of {rsync_ip, rsync_username, src_path, base_name, recursive}
        URL format: {url1}|{url2}|{url3}|
        For a single url: rsync://{rsync_ip}:{rsync_username}/{path}:{recursive}
        """
        pending_transfers_task = []
        for url in combined_url.split("|")[:-1]:
            last_colon = url.rfind(":") 
            recursive = True if url[last_colon+1:] == "True" else False
            #Keep the string before the colon
            rsync_url = url[:last_colon]
            try:
                parsed_url = urlparse(rsync_url)
                rsync_username = parsed_url.hostname
                rsync_ip = parsed_url.netloc[len(rsync_username)+1:]  # remove the username from the netloc, the rest is the ip address
                src_path = parsed_url.path
                basename = os.path.basename(src_path)
                scheme = parsed_url.scheme
                single_transfer_info = {
                    "rsync_ip" : rsync_ip,
                    "rsync_username": rsync_username,
                    "src_path": src_path,
                    "basename": basename,
                    "recursive": recursive,
                    "scheme": scheme,
                }
                pending_transfers_task.append(single_transfer_info)
            # raise a execption if the url is not in the correct format
            # the interchange will catch the exception and record on 
            except Exception as e:
                logger.exception(
                    "Failed to parse url {} due to error: {}".format(url, e)
                )
                raise Exception(
                    "Failed to parse url {} due to error: {}".format(url, e)
                )
        return pending_transfers_task

    def status(self, task):
        """
        Keep consistent with the return value of GlobusTransferClient.status()
        status: ACTIVE, SUCCEEDED, FAILED
        INACTIVE status is not supported, only for globustransfer
        """
        # return a string
        return task['status']

    def get_event(self, task):
        return task['stderr']

    def cancel(self, task):
        del self.transfer_tasks[task['task_id']]
        logger.info(f"[Rsync] canceled the task : {task['task_id']}")
