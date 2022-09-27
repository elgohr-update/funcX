import os
import pathlib
import csv

class ExecutionRecorder:

    def __init__(self):
        self._FUNCX_HOME = os.path.join(pathlib.Path.home(), ".funcx")
        self._FUNCX_EXECUTION_RECORD = os.path.join(self._FUNCX_HOME, "execution_record")
        self.max_files = 10 ** 6
        self._init_execution_record_dir()

    def _init_execution_record_dir(self):
        """Initialize the execution record directory"""
        
        if not os.path.exists(self._FUNCX_EXECUTION_RECORD):
            os.makedirs(name=self._FUNCX_EXECUTION_RECORD, exist_ok=True, mode=0o777)


    def _is_empty_record(self, dir_path):
        """Check if the record directory is empty"""
        return not os.listdir(dir_path)

    def _get_record_file(self):
        """Get the file which will be written a record """

        # If there is no record file, create a new one
        if self._is_empty_record(self._FUNCX_EXECUTION_RECORD):
            number = 0
            file_path = os.path.join(self._FUNCX_EXECUTION_RECORD, "%08d" % number)
            with open(file_path, mode="w") as f:
                pass
            return file_path
        
        # If there are record files, get the last one
        file_list = os.listdir(self._FUNCX_EXECUTION_RECORD)
        file_list.sort(reverse=True)
        return os.path.join(self._FUNCX_EXECUTION_RECORD, file_list[0])
            
        
    
    def write_record(self,task_id, result):
        """Write the execution record to the execution record directory"""

        record_file = self._get_record_file()
        
        # information be append to a record file, so the file should be opened in append mode
        with open(record_file, "a") as f:
            result_copy = result.copy()
            result_copy["task_id"] = task_id
            f = csv.DictWriter(f, result_copy.keys())
            f.writerow(result_copy)