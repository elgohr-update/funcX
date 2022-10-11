import os
import abc
from abc import abstractclassmethod, ABCMeta


class RemoteFile(metaclass=ABCMeta):

    @abstractclassmethod
    def remote_generate(cls,file_name):
        pass

    @abstractclassmethod
    def local_generate(cls,abs_file_path, local_endpoint):
        pass

    @abstractclassmethod
    def get_remote_file_path(self):
        pass

    @abstractclassmethod
    def set_file_size(self, size):
        pass

    @abstractclassmethod
    def get_file_size(self):
        pass

class RemoteDirectory(metaclass=ABCMeta):

    @abstractclassmethod
    def remote_generate(cls,file_name):
        pass

    @abstractclassmethod
    def local_generate(cls,abs_file_path, local_endpoint):
        pass

    @abstractclassmethod
    def get_remote_directory(self):
        pass

    @abstractclassmethod
    def get_remote_file_in_dir(self):
        pass

    @abstractclassmethod
    def set_directory_size(self, size):
        pass

class RemoteInstanceList(metaclass=ABCMeta):
    @abstractclassmethod
    def generate_url(self):
        pass

class RsyncFile(RemoteFile):
    """
    RsyncFile is a class that represents a file that transferred by rsync.
    Different from GlobusFile, (rsync_ip, rsync_username) can be used to
    determine the remote endpoint.
    For GlobusFIle, the remote endpoint is determined by the endpoint_id.
    """

    def __init__(self,rsync_ip,rsync_username,file_path, file_size=0):
        self.rsync_ip = rsync_ip
        self.rsync_username = rsync_username
        # os.path.abspath if file_path only contains a name 
        # return /{os.current_path}/{file_name}
        # if file_path contains a directory, return file_path directly.
        # for example, if file_path is /home/user/test.txt, return /home/user/test.txt
        # if file_path is test.txt, return /{os.current_path}/test.txt
        self.file_path = os.path.abspath(file_path)
        self.file_size = file_size

    @classmethod
    def remote_generate(cls, file_name):
        if file_name.startswith('/'):
            file_name = file_name[1:]
        local_path = os.getenv('LOCAL_PATH')
        abs_path = os.path.join(local_path, file_name)
        return cls(rsync_ip=os.getenv('RSYNC_IP'), 
                   rsync_username=os.getenv('RSYNC_USERNAME'), 
                   file_path=abs_path)

    @classmethod
    def local_generate(cls, abs_file_path, local_ip, local_username):
        if not os.path.exists(abs_file_path):
            raise Exception("[RsyncFile] File not exists.")

        return cls(rsync_ip=local_ip, rsync_username = local_username, 
        file_path=abs_file_path, file_size=os.path.getsize(abs_file_path))

    def get_remote_file_path(self):
        local_path = os.getenv('LOCAL_PATH')
        if local_path is not None and local_path.endswith('/'):
            local_path = local_path[:-1]
        return os.path.join(local_path, self.file_path)

    def set_file_size(self, size):
        self.file_size = size

    def get_file_size(self):
        return self.file_size

class RsyncDirectory(RemoteDirectory):

    def __init__(self, rsync_ip, rsync_username, directory_path, directory_size=0):
        self.rsync_ip = rsync_ip
        self.rsync_username = rsync_username
        self.directory_path = os.path.abspath(directory_path)
        self.directory_name = os.path.basename(directory_path)
        self.directory_size = directory_size

    @classmethod
    def remote_generate(cls, directory_name):
        # In case that unnecessary prefix "/"
        if directory_name.startswith('/'):
            directory_name = directory_name[1:]
        local_path = os.getenv('LOCAL_PATH')
        abs_path = os.path.join(local_path,directory_name)
        # if there is not a directory, then create it.
        if not os.path.exists(abs_path):
            os.makedirs(abs_path)
        return cls(rsync_ip=os.getenv('RSYNC_IP'), rsync_username=os.getenv('RSYNC_USERNAME'), 
        directory_path=abs_path)

    @classmethod
    def local_generate(cls, local_ip, local_username, abs_directory_path):
        if not os.path.exists(abs_directory_path):
            raise Exception("[RsyncDirectory] Directory path not exists.")
        if not os.path.isdir(abs_directory_path):
            raise Exception("[RsyncDirectory] Input path is not a directory.")
        size = 0
        for root, dirs, files in os.walk(abs_directory_path):
            size += sum([os.path.getsize(os.path.join(root, name)) for name in files])

        return cls(rsync_ip=os.getenv('RSYNC_IP'), rsync_username=os.getenv('RSYNC_USERNAME'), 
        directory_path=abs_directory_path, directory_size=size)

    def get_remote_directory(self):
        local_path = os.getenv('LOCAL_PATH')
        if local_path is not None and local_path.endswith('/'):
            local_path = local_path[:-1]
        return os.path.join(local_path, self.directory_name)

    def get_remote_file_in_dir(self, file_name):
        # Only return the file name, please generate a File instance if necessary
        remote_dir = self.get_remote_directory()
        if file_name.startswith('/'):
            file_name = file_name[1:]
        return os.path.join(remote_dir, file_name)

    def set_directory_size(self, size):
        self.directory_size = size

class RsyncInstanceList(RemoteInstanceList):
    def __init__(self, instance_list, pre_trans=False):
        self.instance_list = instance_list
        # pre_trans means that it has been transfered by parsl client
        self.pre_trans = pre_trans

    def generate_url(self):
        if len(self.instance_list) <= 0:
            return ""
        url = ""
        for file in self.instance_list:
            if isinstance(file, RsyncDirectory):
                recursive = True
                """
                There is no dash between endpoint and directory path.
                Because the unix path will involes a '/' at the beginning.
                """
                url += f"rsync://{file.rsync_username}:{file.rsync_ip}{file.directory_path}:{recursive}|"
            elif isinstance(file, RsyncFile):
                recursive = False
                url += f"rsync://{file.rsync_username}:{file.rsync_ip}{file.file_path}:{recursive}|"
        return url

class GlobusFile(RemoteFile):
    """The Globus File Class.

    This represents the globus filpath to a file.
    """

    def __init__(self, endpoint, file_path, file_size=0):
        """Initialize the client

        Parameters
        ----------
        endpoint: str
        The endpoint id where the data is located. Required

        path: str
        The path where the data is located on the endpoint. Required
        """
        self.endpoint = endpoint
        obs_path = os.path.abspath(file_path)
        self.file_path = obs_path
        self.file_size = file_size

    @classmethod
    def remote_generate(cls, file_name):
        if file_name.startswith('/'):
            file_name = file_name[1:]
        globus_ep_id = os.getenv('GLOBUS_EP_ID')
        local_path = os.getenv('LOCAL_PATH')
        abs_path = os.path.join(local_path, file_name)
        return cls(endpoint=globus_ep_id, file_path=abs_path)

    @classmethod
    def local_generate(cls, abs_file_path, local_endpoint):
        if not os.path.exists(abs_file_path):
            raise Exception("[GlobusFile] File not exists.")

        return cls(endpoint=local_endpoint, file_path=abs_file_path, file_size=os.path.getsize(abs_file_path))

    def get_remote_file_path(self):
        local_path = os.getenv('LOCAL_PATH')
        if local_path is not None and local_path.endswith('/'):
            local_path = local_path[:-1]
        return os.path.join(local_path, self.file_path)

    def set_file_size(self, size):
        self.file_size = size

    def get_file_size(self):
        return self.file_size

class GlobusDirectory(RemoteDirectory):
    """
    The GlobusDirectory class

    This represents a directory which is transferred by Globus
    """

    def __init__(self, endpoint, directory_path, directory_size=0):
        self.endpoint = endpoint
        self.directory_path = os.path.abspath(directory_path)
        self.directory_name = os.path.basename(directory_path)
        self.directory_size = directory_size

    @classmethod
    def remote_generate(cls, directory_name):
        if directory_name.startswith('/'):
            directory_name = directory_name[1:]
        globus_ep_id = os.getenv('GLOBUS_EP_ID')
        local_path = os.getenv('LOCAL_PATH')
        # if there is not a directory, then create it.
        abs_path = os.path.join(local_path,directory_name)
        if not os.path.exists(abs_path):
            os.makedirs(abs_path)
        return cls(endpoint=globus_ep_id, directory_path=abs_path)

    @classmethod
    def local_generate(cls, local_endpoint, abs_directory_path):
        if not os.path.exists(abs_directory_path):
            raise Exception("[GlobusDirectory] Directory path not exists.")
        if not os.path.isdir(abs_directory_path):
            raise Exception("[GlobusDirectory] Input path is not a directory.")
        size = 0
        for root, dirs, files in os.walk(abs_directory_path):
            size += sum([os.path.getsize(os.path.join(root, name)) for name in files])

        return cls(endpoint=local_endpoint, directory_path=abs_directory_path, directory_size=size)

    def get_remote_directory(self):
        local_path = os.getenv('LOCAL_PATH')
        if local_path is not None and local_path.endswith('/'):
            local_path = local_path[:-1]
        return os.path.join(local_path, self.directory_name)

    def get_remote_file_in_dir(self, file_name):
        remote_dir = self.get_remote_directory()
        if file_name.startswith('/'):
            file_name = file_name[1:]
        return os.path.join(remote_dir, file_name)

    def set_directory_size(self, size):
        self.directory_size = size

# GlobusInstanceList is only invoked for internal program (funcX-executor)
class GlobusInstanceList(RemoteInstanceList):
    def __init__(self, instance_list, pre_trans=False):
        self.instance_list = instance_list
        # pre_trans means that it has been transfered by parsl client
        self.pre_trans = pre_trans

    def generate_url(self):
        if len(self.instance_list) <= 0:
            return ""
        url = ""
        for file in self.instance_list:
            if isinstance(file, GlobusDirectory):
                recursive = True
                """
                There is no dash between endpoint and directory path.
                Because the unix path will involes a '/' at the beginning.
                """
                url += f"globus://{file.endpoint}{file.directory_path}:{recursive}|"
            elif isinstance(file, GlobusFile):
                recursive = False
                url += f"globus://{file.endpoint}{file.file_path}:{recursive}|"
        return url


