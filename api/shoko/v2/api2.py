# -*- coding: utf-8 -*-

# BASED OF :8111/swagger/index.html?urls.primaryName=2.0

from api.common import *
from api2models import *


address = "http://192.168.1.2"
port = "8111"
version = 2
# api related
apikey = ''
# timeout waiting for response (in seconds)
timeout = 120


api_client = APIClient(api_address=address, api_port=port, api_version=version, api_key=apikey, timeout=timeout)


#
# Auth
#
def login_user(user='', password='', device=''):
    """Authenticate user with given username and password\n
    Returns `AuthUser` object"""
    data = {
        "user": user,
        "pass": password,
        "device": device
    }
    response = api_client.call(url='/api/auth', call_type=APIType.POST, data=data, auth=False)
    return json.loads(response, object_hook=AuthUser.Decoder)


def delete_user_apikey(apikey):
    """
    Delete user apikey
    """
    query = {'apikey': apikey}
    return api_client.call(url='/api/auth', call_type=APIType.DELETE, query=query, auth=False)

def change_user_password(password):
    """
    Change user password
    """
    data = f"{password}"
    return api_client.call(url='/api/auth/ChangePassword', call_type=APIType.POST, data=data)



#
# Common
#
# TODO check under Shoko.Server hood to get return types and some comment on endpoints

# def _common_api_(command='', call_type=APIType.GET, query={}, data={}):
#     url = f'/api/{command}'
#     return api_client.call(url=url, call_type=call_type, query=query, data=data, auth=True)

def cloud_list():
    # 501: Not Implemented
    return api_client.call(url='/api/cloud/list', call_type=APIType.GET)
def cloud_count():
    # 501: Not Implemented
    return api_client.call(url='/api/cloud/count', call_type=APIType.GET)
def cloud_add():
    # 501: Not Implemented
    return api_client.call(url='/api/cloud/add', call_type=APIType.POST)
def cloud_delete():
    # 501: Not Implemented
    return api_client.call(url='/api/cloud/delete', call_type=APIType.POST)
def cloud_import():
    # 501: Not Implemented
    return api_client.call(url='/api/cloud/import', call_type=APIType.POST)
def filter(opts: QueryOptions = QueryOptions()):
    return api_client.call(url='/api/filter', call_type=APIType.GET, query=opts.__dict__)
def group(opts: QueryOptions = QueryOptions()):
    return api_client.call(url='/api/group', call_type=APIType.GET, query=opts.__dict__)
def group_watch(id: int):
    query = {
        'id': id
    }
    return api_client.call(url='/api/group/watch', call_type=APIType.GET, query=query)
def group_search(opts: QueryOptions = QueryOptions()):
    return api_client.call(url='/api/group/search', call_type=APIType.GET, query=opts.__dict__)
def cast_by_series(id: int):
    query = {
        'id': id
    }
    return api_client.call(url='/api/cast/byseries', call_type=APIType.GET, query=query)
def cast_search(opts: QueryOptions = QueryOptions()):
    response = api_client.call(url='/api/cast/search', call_type=APIType.GET, query=opts.__dict__)
    _json = json.loads(response)
    return Filter.Decoder(_json)
def links_serie(id: int):
    query = {
        'id': id
    }
    return api_client.call(url='/api/links/serie', call_type=APIType.GET, query=query)
def folder_list():
    response = api_client.call(url='/api/folder/list', call_type=APIType.GET)
    _json = json.loads(response)
    output: list[ImportFolder] = []
    for folder in _json:
        output.append(ImportFolder.Decoder(folder))
    return output
def folder_count() -> Counter:
    response = api_client.call(url='/api/folder/count', call_type=APIType.GET)
    _json = json.loads(response)
    return Counter.Decoder(_json)
def folder_add(folder: ImportFolder) -> ImportFolder:
    response = api_client.call(url='/api/folder/add', call_type=APIType.POST, data=folder.__dict__)
    _json = json.loads(response)
    return ImportFolder.Decoder(_json)
def folder_edit(folder: ImportFolder) -> ImportFolder:
    response = api_client.call(url='/api/folder/edit', call_type=APIType.POST, data=folder.__dict__)
    _json = json.loads(response)
    return ImportFolder.Decoder(_json)
def folder_delete(id: int):
    query = {
        'folderId': id
    }
    return api_client.call(url='/api/folder/delete', call_type=APIType.POST, query=query)
def folder_import():
    return api_client.call(url='/api/folder/import', call_type=APIType.GET)
def folder_scan():
    return api_client.call(url='/api/folder/scan', call_type=APIType.GET)
def remove_missing_files():
    return api_client.call(url='/api/remove_missing_files', call_type=APIType.GET)
def stats_update():
    return api_client.call(url='/api/stats_update', call_type=APIType.GET)
def mediainfo_update():
    # typo in API endpoint?
    # should be media? meta?
    # assumed to be mediainfo
    return api_client.call(url='/api/medainfo_update', call_type=APIType.GET)
def hash_sync():
    return api_client.call(url='/api/hash/sync', call_type=APIType.GET)
def foler_rescan(id: int):
    """Accoring to Shoko.Server source code:
    "Rescan ImportFolder (with given `id`) to recognize new episodes"
    """
    query = {
        'id': id
    }
    return api_client.call(url='/api/rescan', call_type=APIType.GET, query=query)
def rescan_unlinked():
    """Accoring to Shoko.Server source code:
    "files which have been hashed, but don't have an associated episode"
    """
    return api_client.call(url='/api/rescanunlinked', call_type=APIType.GET)
def rescan_manual_links():
    """Accoring to Shoko.Server source code:
    "files which have been hashed, but don't have an associated episode"
    """
    return api_client.call(url='/api/rescanmanuallinks', call_type=APIType.GET)
def rehash(id: int):
    """Accoring to Shoko.Server source code:
    "Rehash given files in given VideoLocal"
    """
    query = {
        'id': id
    }
    return api_client.call(url='/api/rehash', call_type=APIType.GET, query=query)
def rehash_unlinked():
    """Accoring to Shoko.Server source code:
    "files which have been hashed, but don't have an associated episode"
    """
    return api_client.call(url='/api/rehashunlinked', call_type=APIType.GET)
def rehash_manual_links():
    """Accoring to Shoko.Server source code:
    "files which have been hashed, but don't have an associated episode"
    """
    return api_client.call(url='/api/rehashmanuallinks', call_type=APIType.GET)
def myid_get():
    """Accoring to Shoko.Server source code:
    "Returns current user ID for use in legacy calls"
    """
    return api_client.call(url='/api/myid/get', call_type=APIType.GET)

def ping():
    return api_client.call(url='/api/ping', call_type=APIType.GET)


api_client.apikey = login_user('default', '', 'api-v2-device').apikey
print(api_client.apikey)

