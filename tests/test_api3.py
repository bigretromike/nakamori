# -*- coding: utf-8 -*-
""" Tests against ShokoServer APIv3 """

from __future__ import absolute_import

from http import HTTPStatus

import pytest
import json
from api.shoko.v3.api3 import (replace_apikey_while_runtime, login_user, delete_user_apikey, change_user_password)
from api.shoko.v3.api3models import AuthUser


@pytest.fixture()
def fake_auth_info():
    with open("tests/resources/auth.json") as f:
        return json.load(f)


def test_login_user(mocker, fake_auth_info):
    """
    this test mock (fake) call with reading json from file and passing is as response from call,
    while also calling real endpoint and compare both objects
    """
    fake_resp = mocker.Mock()
    fake_resp.json = mocker.Mock(return_value=fake_auth_info)
    fake_resp.status_code = HTTPStatus.OK

    mocker.patch("api.shoko.v3.api3.login_user", return_value=fake_resp)

    auth_info = login_user(user='default', password='', device='pytest')
    replace_apikey_while_runtime(apikey=auth_info.apikey)
    # let's overwrite apikey because each time we 'POST' we get new ApiKey so we can't fake it vs real server
    fake_auth_info['apikey'] = auth_info.apikey
    assert auth_info == AuthUser.from_dict(fake_auth_info)


def test_delete_user_apikey(mocker):
    fake_resp = mocker.Mock()
    fake_resp.json = mocker.Mock(return_value="")
    fake_resp.status_code = HTTPStatus.OK

    mocker.patch("api.shoko.v3.api3.delete_user_apikey", return_value=fake_resp)

    delete_info = delete_user_apikey(apikey='c5df7065-0000-0000-0000-a821ca52d593')
    assert delete_info == b''


def test_change_user_password(mocker):
    fake_resp = mocker.Mock()
    fake_resp.json = mocker.Mock(return_value="")
    fake_resp.status_code = HTTPStatus.OK
    mocker.patch("api.shoko.v3.api3.change_user_password", return_value=fake_resp)
    # we change password, then change it back, while doing this we need to replace new apikey
    change_info = change_user_password(password='123')
    assert change_info == b''

    auth_info = login_user(user='default', password='123', device='pytest')
    replace_apikey_while_runtime(apikey=auth_info.apikey)

    change_info = change_user_password(password='')
    assert change_info == b''
