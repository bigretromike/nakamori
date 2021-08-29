# -*- coding: utf-8 -*-

# BASED OF :8111/swagger/index.html?urls.primaryName=2.0

import gzip
import json
from urllib.parse import urlencode
from enum import Enum
from io import BytesIO
from urllib.request import Request, urlopen
from api2models import *


class Api(Enum):
    GET = 1
    POST = 2
    DELETE = 3
    PATCH = 4
    PUT = 5


def _responde_helper(response):
    if response.code == 200:
        print('ok')
    elif response.code == 400:
        print('bad request')
    elif response.code == 401:
        print('unauthorized')
    elif response.code == 500:
        print('shoko is buggy')
    else:
        print('not supported error')


# timeout waiting for response (in seconds)
timeout = 120
# api related
api_version = 2
api_key = ''
api_address = "http://192.168.1.2"
api_port = "8111"


def _api_call_(url, call_type=Api.GET, query={}, data={}, auth=True):
    if query:
        query = urlencode(query)
        url = f"{api_address}:{api_port}{url}?{query}&api-version={api_version}"
    else:
        url = f"{api_address}:{api_port}{url}?api-version={api_version}"
    print(f"{url}")

    headers = {
        'Accept': '*/*',
        'Content-Type': 'application/json',
        'api-version': f'{api_version}'
    }

    if auth:
        headers['apikey'] = api_key

    if '127.0.0.1' not in url and 'localhost' not in url:
        headers['Accept-Encoding'] = 'gzip'
    if '/Stream/' in url:
        headers['api-version'] = '1.0'

# Api Calls
    if call_type == Api.GET:
        print(f"Api.GET === {url} -- -H {headers} -D {data}")
        req = Request(url, data=data, headers=headers, method="GET")

    elif call_type == Api.POST:
        print(f"Api.POST === {url} -- -H {headers} -D {data}")
        data = json.dumps(data).encode("utf-8")
        req = Request(url, data=data, headers=headers, method="POST")

    elif call_type == Api.DELETE:
        print(f"Api.DELETE === {url} -- -H {headers} -D {data}")
        data = json.dumps(data).encode("utf-8")
        req = Request(url, data=data, headers=headers, method="DELETE")

    elif call_type == Api.PATCH:
        print(f"Api.PATCH === {url} -- -H {headers} -D {data}")
        data = json.dumps(data).encode("utf-8")
        req = Request(url, data=data, headers=headers, method="PATCH")

    elif call_type == Api.PUT:
        print(f"Api.PUT == {url} -- -H {headers} -D {data}")
        data = json.dumps(data).encode("utf-8")
        req = Request(url, data=data, headers=headers, method="PUT")

    else:
        print(f"Unknown === {url}")


    response = urlopen(req, timeout=int(timeout))

    if response.info().get('Content-Encoding') == 'gzip':
        try:
            buf = BytesIO(response.read())
            f = gzip.GzipFile(fileobj=buf)
            data = f.read()
        except Exception as e:
            print(f"Failed to decompress === {e}")
    else:
        data = response.read()
    response.close()

    return data


#
# Auth
#
def _auth_api_(command='', call_type=Api.GET, query={}, data={}, auth=False):
    if command == '':
        url = '/api/auth'
    else:
        url = f'/api/auth/{command}'
    
    return _api_call_(url=url, call_type=call_type, query=query, data=data, auth=auth)
def login_user(user='', password='', device=''):
    """Authenticate user with given username and password\n
    Returns `AuthUser` object"""
    data = {
        "user": user,
        "pass": password,
        "device": device
    }
    response = _auth_api_(call_type=Api.POST, data = data)
    return json.loads(response, object_hook=AuthUser.Decoder)
def delete_user_apikey(apikey):
    """
    Delete user apikey
    """
    data = {'apikey': apikey}
    return _auth_api_(call_type=Api.DELETE, query=data)
def change_user_password(password):
    """
    Change user password
    """
    data = f"{password}"
    return _auth_api_(command="ChangePassword", call_type=Api.POST, data=data, auth=True)



#
# Common
#
def _common_api_(command='', call_type=Api.GET, query={}):
    url = f'/api/{command}'
    return _api_call_(url=url, call_type=call_type, query=query, data={}, auth=True)
def cloud_list():
    # 501: Not Implemented
    return _common_api_(command='cloud/list', call_type=Api.GET)
def cloud_count():
    # 501: Not Implemented
    return _common_api_(command='cloud/count', call_type=Api.GET)
def cloud_add():
    # 501: Not Implemented
    return _common_api_(command='cloud/add', call_type=Api.POST)
def cloud_delete():
    # 501: Not Implemented
    return _common_api_(command='cloud/delete', call_type=Api.POST)
def cloud_import():
    # 501: Not Implemented
    return _common_api_(command='cloud/import', call_type=Api.POST)
def filter(opts: QueryOptions = QueryOptions()):
    return _common_api_(command='filter', call_type=Api.GET, query=opts.__dict__)
def group(opts: QueryOptions = QueryOptions()):
    return _common_api_(command='group', call_type=Api.GET, query=opts.__dict__)
def group_watch(id: int):
    data = {
        'id': id
    }
    return _common_api_(command='group/watch', call_type=Api.GET, query=data)
def group_search(opts: QueryOptions = QueryOptions()):
    return _common_api_(command='group/search', call_type=Api.GET, query=opts.__dict__)
def cast_by_series(id: int):
    data = {
        'id': id
    }
    return _common_api_(command='cast/byseries', call_type=Api.GET, query=data)
def cast_search(opts: QueryOptions = QueryOptions()):
    return _common_api_(command='cast/search', call_type=Api.GET, query=opts.__dict__)

def ping():
    return _common_api_('ping', call_type=Api.GET)

api_key = login_user('default', '', 'api-v2-device').apikey
print(api_key)


# response = filter()
# print(response)

# response = group_watch(1)
# print(response)


response = cast_by_series(15)
print(json.loads(response))

response = cast_search(QueryOptions(query="Eguchi Takuya"))
print(json.loads(response))