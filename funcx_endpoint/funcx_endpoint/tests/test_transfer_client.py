import pytest
import sys
import os

from funcx_endpoint.data_transfer.globus import GlobusTransferClient
from funcx_endpoint.data_transfer.rsync import RsyncTransferClient


def test_globus_urlparse():
    url = "globus://e419f04d-215b-41eb-9e5c-22bfba011cc8/user/test.txt:False|globus://e419f04d-215b-41eb-9e5c-22bfba011cc8/user/test.txt:True|"
    res_list = GlobusTransferClient.parse_url(url)  
    assert len(res_list) == 2

def test_rsync_urlparse():
    host_ip = "10.10.10.10"
    user_name = "user"
    url = f"rsync://{user_name}:{host_ip}/user/test.txt:False|rsync://{user_name}:{host_ip}/user/test:True|"
    res_list = RsyncTransferClient.parse_url(url)
    assert len(res_list) == 2
    assert res_list[0]["scheme"] == "rsync"
    assert res_list[0]["src_path"] == "/user/test.txt"
    assert res_list[1]["src_path"] == "/user/test"
    assert res_list[0]["rsync_username"] == user_name
    assert res_list[0]["rsync_ip"] == host_ip


def test_rsync_transfer():
    host_ip = "10.10.10.10"
    user_name = "user"
    # the local path must end with "/"
    rsync_client = RsyncTransferClient(local_path="/user/", dst_ep=host_ip, username=user_name)

    url = f"rsync://{user_name}:{host_ip}/user/test.txt:False|rsync://{user_name}:{host_ip}/user/test:True|"
    res_list = rsync_client.parse_url(url)
    info_list = []
    for i in range(len(res_list)):
        tmp_res = rsync_client.check_same(res_list[i])
        if i==0 : assert tmp_res == True
        elif i==1 : assert tmp_res == False
        