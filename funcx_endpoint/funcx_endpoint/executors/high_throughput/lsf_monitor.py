import subprocess
import os


class LSFMonitor:

    def __init__(self):
        self.hosts_num = 10

    @staticmethod
    def execute_cmd(cmd):
        current_env = os.environ.copy()
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=current_env,
            shell=True)
        (stdout, stderr) = proc.communicate()
        retcode = proc.returncode
        return retcode, stdout.decode("utf-8"), stderr.decode("utf-8")

    def get_hosts_info(self, cmd="lshosts -w"):
        retcode, cmd_out, cmd_err = self.execute_cmd(cmd)
        for line in cmd_out.split('\n'):
            print(line)


if __name__ == "__main__":
    lsf = LSFMonitor()
    print(lsf.get_hosts_info())
