import subprocess

class RsyncTransferClient:
    def __init__(self, local_path=".", dst_ep=None,username="~",**kwargs):
        # all connected endpoints should be authenticated by ssh manually
        self.local_path = local_path
        self.dst_ep = dst_ep
        self.username = username

    def generate_rsync_command(self, src_username, src_ip, src_path, basename, recursive=False):
        r_parm = "-avz" if not recursive else "-avzr"
        rsync_command = f"rsync {r_parm} {src_username}@{src_ip}:{src_path} {self.local_path}"
        return rsync_command

    # transfer a file by rsync
    def transfer(self, src_username, src_ip, src_path, basename, recursive=False):
        cmd = self.generate_rsync_command(src_username, src_ip, src_path, basename, recursive)
        print(f"Rysnc command: {cmd}")
        try:
            ret = subprocess.run(cmd, shell=True, check=True)
            print(f"Rsync return code: {ret.returncode}")
        except subprocess.CalledProcessError as e:
            print(f"Rsync failed: {e}")
            raise Exception(f"Rsync failed: {e}")
        return (cmd, src_username, src_ip, src_path, self.dst_ep, self.local_path)


if __name__ == "__main__":
    host_loc = "/home/eric/research/EVA_dir/rsync"
    host_user = "eric"
    host_ip = "10.16.57.154"

    src_user = "eric"
    src_file = "/Users/eric/research/MAC_dir"
    src_ip =  "10.26.116.231"

    rsync_client = RsyncTransferClient(local_path=host_loc, dst_ep=host_ip, username=host_user)
    print(rsync_client.transfer(src_user, src_ip, src_file, "MAC_dir"))
