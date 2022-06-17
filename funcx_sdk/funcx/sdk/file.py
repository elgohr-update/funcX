import os


class GlobusFile:
    """The Globus File Class.

    This represents the globus filpath to a file.
    """

    def __init__(self, endpoint, path, recursive=False):
        """Initialize the client

        Parameters
        ----------
        endpoint: str
        The endpoint id where the data is located. Required

        path: str
        The path where the data is located on the endpoint. Required

        recursive: boolean
        A boolean indicating whether the data is a directory or a file.
        Default is False (a file).

        """
        self.endpoint = endpoint
        if recursive is False:
            obs_path = os.path.abspath(path)
            self.path = obs_path
        else:
            obs_path = os.path.abspath(path)
            self.path = obs_path
        self.recursive = recursive

    @classmethod
    def remote_generate(cls, relative_path, recursive=False):
        if relative_path.startswith('/'):
            relative_path = relative_path[1:]
        globus_ep_id = os.getenv('GLOBUS_EP_ID')
        local_path = os.getenv('LOCAL_PATH')
        obs_path = f"{local_path}/{relative_path}"
        return cls(endpoint=globus_ep_id, path=obs_path, recursive=recursive)

    def get_remote_file_path(self):
        local_path = os.getenv('LOCAL_PATH')
        if local_path is not None and local_path.endswith('/'):
            local_path = local_path[:-1]
        return f"{local_path}/{os.path.basename(self.path)}"

    def get_remote_file_path_in_dir(self, relative_path):
        if relative_path.startswith('/'):
            relative_path = relative_path[1:]
        local_path = os.getenv('LOCAL_PATH')
        if local_path is not None and local_path.endswith('/'):
            local_path = local_path[:-1]
        return f"{local_path}/{os.path.basename(self.path)}/{relative_path}"

    def get_file_path(self):
        return self.path

    def generate_url(self):
        return f"globus://{self.endpoint}/{self.path}"

    def get_recursive(self):
        return self.recursive


class GlobusFileList:
    def __init__(self, file_list, pre_trans=False):
        self.file_list = file_list
        self.pre_trans = pre_trans

    def generate_url(self):
        if len(self.file_list) <= 0:
            return ""
        url = ""
        for file in self.file_list:
            url += f"globus://{file.endpoint}/{file.path}:{file.recursive}|"
        return url