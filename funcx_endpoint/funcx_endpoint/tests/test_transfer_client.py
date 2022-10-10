import pytest
import sys
import os

from funcx_endpoint.data_transfer.globus import GlobusTransferClient


def test_globus():
    #client = GlobusTransferClient()
    url = "globus://e419f04d-215b-41eb-9e5c-22bfba011cc8/user/test.txt:False|globus://e419f04d-215b-41eb-9e5c-22bfba011cc8/user/test.txt:True|"
    res_list = GlobusTransferClient.parse_url(url)
    assert len(res_list) == 2
