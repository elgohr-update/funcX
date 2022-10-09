import pytest

from urllib.parse import urlparse
from funcx.sdk.file import RsyncFile, RsyncDirectory, RemoteDirectory
from funcx.sdk.file import RsyncInstanceList, GlobusFile, GlobusInstanceList

def test_rsyncfile():
    rsync_ip = "10.10.10.10"
    rsync_username = "user"
    file_path = "/user/test.txt"
    rsyncfile = RsyncFile(rsync_ip, rsync_username, file_path)
    assert rsyncfile.rsync_ip == rsync_ip 
    assert rsyncfile.rsync_username == rsync_username
    assert rsyncfile.file_path == "/user/test.txt" 

def test_rsyncdir():
    rsync_ip = "10.10.10.10"
    rsync_username = "user"
    file_path = "/user/test.txt"
    rsyncdir = RsyncDirectory(rsync_ip, rsync_username, file_path)
    rsyncfile = RsyncFile(rsync_ip, rsync_username, file_path)
    assert isinstance(rsyncdir, RemoteDirectory) == True 
    rsyncInsList = RsyncInstanceList(instance_list=[rsyncfile, rsyncdir])
    data_url = "rsync://user:10.10.10.10/user/test.txt:False|rsync://user:10.10.10.10/user/test.txt:True|"

    for url in data_url.split("|")[:-1]:
            recursive = True if url.split(":")[2] == "True" else False
            begin = url.rfind(":")
            single_url = url[:begin]
            parsed_url = urlparse(single_url)
            assert parsed_url.path == "/user/test.txt"

    assert rsyncInsList.generate_url() ==  data_url 

def test_globusInsList():
    globus_ep = "e419f04d-215b-41eb-9e5c-22bfba011cc8"
    file_path = "/user/test.txt"
    globusfile = GlobusFile(globus_ep, file_path)
    data_url = "globus://e419f04d-215b-41eb-9e5c-22bfba011cc8/user/test.txt:False|"

    for url in data_url.split("|")[:-1]:
            recursive = True if url.split(":")[2] == "True" else False
            begin = url.rfind(":")
            single_url = url[:begin]
            parsed_url = urlparse(single_url)
            assert parsed_url.path == "/user/test.txt"
    globus_InslList = GlobusInstanceList(instance_list=[globusfile])
    assert globus_InslList.generate_url() == data_url