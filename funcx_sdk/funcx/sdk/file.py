import os


class GlobusFile:
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


class GlobusDirectory:
    """
    The GlobusDirectory class

    This represents a directory which is transferred by Globus
    """

    def __init__(self, endpoint, directory_path, directory_size=0):
        self.endpoint = endpoint
        self.directory_path = directory_path
        self.directory_name = os.path.basename(directory_path)
        self.directory_size = directory_size

    # if there is not a directory, then create it.
    @classmethod
    def remote_generate(cls, directory_name):
        if directory_name.startswith('/'):
            directory_name = directory_name[1:]
        globus_ep_id = os.getenv('GLOBUS_EP_ID')
        local_path = os.getenv('LOCAL_PATH')
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
class GlobusInstanceList:
    def __init__(self, instance_list, pre_trans=False):
        self.instance_list = instance_list
        self.pre_trans = pre_trans

    def generate_url(self):
        if len(self.instance_list) <= 0:
            return ""
        url = ""
        for file in self.instance_list:
            if isinstance(file, GlobusDirectory):
                recursive = True
                url += f"globus://{file.endpoint}/{file.directory_path}:{recursive}|"
            elif isinstance(file, GlobusFile):
                recursive = False
                url += f"globus://{file.endpoint}/{file.file_path}:{recursive}|"
        return url
