import pytest

from urllib.parse import urlparse
from funcx.sdk.file import RsyncFile, RsyncDirectory, RemoteDirectory
from funcx.sdk.file import GlobusFile


def test_rsyncfile():
    rsync_ip = "10.10.10.10"
    rsync_username = "user"
    file_path = "/user/test.txt"
    rsyncfile = RsyncFile(rsync_ip, rsync_username, file_path)
    assert rsyncfile.rsync_ip == rsync_ip 
    assert rsyncfile.rsync_username == rsync_username
    assert rsyncfile.file_path == "/user/test.txt" 
    assert rsyncfile.generate_url() == "rsync://user:10.10.10.10/user/test.txt:False|"

def test_rsyncdir():
    rsync_ip = "10.10.10.10"
    rsync_username = "user"
    file_path = "/user/test.txt"
    rsyncdir = RsyncDirectory(rsync_ip, rsync_username, file_path)
    rsyncfile = RsyncFile(rsync_ip, rsync_username, file_path)
    assert isinstance(rsyncdir, RemoteDirectory) == True 
    tmp_url = rsyncfile.generate_url()
    tmp_url += rsyncdir.generate_url()

    data_url = "rsync://user:10.10.10.10/user/test.txt:False|rsync://user:10.10.10.10/user/test.txt:True|"
    assert data_url == tmp_url

    for url in data_url.split("|")[:-1]:
            recursive = True if url.split(":")[2] == "True" else False
            begin = url.rfind(":")
            single_url = url[:begin]
            parsed_url = urlparse(single_url)
            assert parsed_url.path == "/user/test.txt"

