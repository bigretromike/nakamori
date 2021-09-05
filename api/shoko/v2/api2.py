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
def login_user(auth: AuthUser) -> str:
    """
    Get an authentication token for the user.

    Parameters
    ---
        auth : AuthUser
            The authentication details for the user.
    """
    data = {
        "user": auth.user,
        "pass": auth.password,
        "device": auth.device
    }
    response = api_client.call(url='/api/auth', call_type=APIType.POST, data=data, auth=False)
    return json.loads(response)

def delete_user_apikey(apikey: str):
    """
    Delete an APIKey from the database.
    
    Parameters
    ---
        apikey : str
            The API key to delete
    """
    query = {'apikey': apikey}
    return api_client.call(url='/api/auth', call_type=APIType.DELETE, query=query, auth=False)

def change_user_password(password: str):
    """
    Change user password

    Parameters
    ---
        password : str
            new password
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
    response = api_client.call(url='/api/filter', call_type=APIType.GET, query=opts.__dict__)
    _json = json.loads(response)
    return Filter.Decoder(_json)

def group(opts: QueryOptions = QueryOptions()):
    response = api_client.call(url='/api/group', call_type=APIType.GET, query=opts.__dict__)
    _json = json.loads(response)
    output: list[Group] = []
    for group in _json:
        output.append(Group.Decoder(group))
    return output

def group_watch(id: int):
    query = {
        'id': id
    }
    return api_client.call(url='/api/group/watch', call_type=APIType.GET, query=query)

def group_search(opts: QueryOptions = QueryOptions()):
    response = api_client.call(url='/api/group/search', call_type=APIType.GET, query=opts.__dict__)
    _json = json.loads(response)
    output: list[Group] = []
    for group in _json:
        output.append(Group.Decoder(group))
    return output

def cast_by_series(id: int):
    query = {
        'id': id
    }
    response = api_client.call(url='/api/cast/byseries', call_type=APIType.GET, query=query)
    _json = json.loads(response)
    output: list[Role] = []
    for role in _json:
        output.append(Role.Decoder(role))
    return output

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
    """
    List all saved Import Folders
    """
    response = api_client.call(url='/api/folder/list', call_type=APIType.GET)
    _json = json.loads(response)
    output: list[ImportFolder] = []
    for folder in _json:
        output.append(ImportFolder.Decoder(folder))
    return output

def folder_count() -> Counter:
    """
    Get import folders count
    """
    response = api_client.call(url='/api/folder/count', call_type=APIType.GET)
    _json = json.loads(response)
    return Counter.Decoder(_json)

def folder_add(folder: ImportFolder) -> ImportFolder:
    """
    Add Folder to Import Folders Repository
    """
    response = api_client.call(url='/api/folder/add', call_type=APIType.POST, data=folder.__dict__)
    _json = json.loads(response)
    return ImportFolder.Decoder(_json)

def folder_edit(folder: ImportFolder) -> ImportFolder:
    """
    Edit folder giving fulll ImportFolder object with ID
    """
    response = api_client.call(url='/api/folder/edit', call_type=APIType.POST, data=folder.__dict__)
    _json = json.loads(response)
    return ImportFolder.Decoder(_json)

def folder_delete(id: int):
    """
    Delete Import Folder out of Import Folder Repository
    """
    query = {
        'folderId': id
    }
    return api_client.call(url='/api/folder/delete', call_type=APIType.POST, query=query)

def folder_import():
    """
    Run Import action on all Import Folders inside Import Folders Repository
    """
    return api_client.call(url='/api/folder/import', call_type=APIType.GET)

def folder_scan():
    """
    Scan All Drop Folders
    """
    return api_client.call(url='/api/folder/scan', call_type=APIType.GET)

def remove_missing_files():
    """
    Scans your import folders and remove files from your database that are no longer in your collection.
    """
    return api_client.call(url='/api/remove_missing_files', call_type=APIType.GET)

def stats_update():
    """
    Updates all series stats such as watched state and missing files.
    """
    return api_client.call(url='/api/stats_update', call_type=APIType.GET)

def mediainfo_update():
    """
    Updates all technical details about the files in your collection via running MediaInfo on them.
    """
    # typo in API endpoint?
    # should be media? meta?
    # assumed to be mediainfo
    return api_client.call(url='/api/medainfo_update', call_type=APIType.GET)

def hash_sync():
    """
    Sync Hashes - download/upload hashes from/to webcache
    """
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

def myid_get() -> dict:
    """Accoring to Shoko.Server source code:
    "Returns current user ID for use in legacy calls"
    """
    return json.loads(api_client.call(url='/api/myid/get', call_type=APIType.GET))

def news_get(max: int):
    """
    Return newest posts

    Parameters:
    ---
        `max` : int
            Limit number of news by declaring `max` value
    """
    query = {
        'max': max
    }
    response = api_client.call(url='/api/news/get', call_type=APIType.GET, query=query)
    _json = json.loads(response)
    output: list[WebNews] = []
    for new in _json:
        output.append(WebNews.Decoder(new))
    return output

def search(opts: QueryOptions = QueryOptions()):
    response = api_client.call(url='/api/search', call_type=APIType.GET, query=opts.__dict__)
    _json = json.loads(response)
    return Filter.Decoder(_json)

def serie_startswith(opts: QueryOptions = QueryOptions()):
    response = api_client.call(url='/api/serie/startswith', call_type=APIType.GET, query=opts.__dict__)
    _json = json.loads(response)
    return Filter.Decoder(_json)

def ping() -> dict:
    """
    Check if connection and auth is valid without ask for real data
    """
    return json.loads(api_client.call(url='/api/ping', call_type=APIType.GET))

def queue_get():
    """Get current information about Queues (hash, general, images)

    Returns dictionary:

    {
        hasher : `QueueInfo`
        general : `QueueInfo`
        images : `QueueInfo`
    }"""
    response = api_client.call(url='/api/queue/get', call_type=APIType.GET)
    _json: dict = json.loads(response)
    output: dict[str, QueueInfo] = {}
    for row in _json.keys():
         queueinfo = QueueInfo.Decoder(_json.get(row))
         output[row] = queueinfo
    return output

def queue_pause():
    """Pause all (hasher, general, images) running Queues"""
    return api_client.call(url='/api/queue/pause', call_type=APIType.GET)

def queue_start():
    """Start all (hasher, general, images) queues that are pasued"""
    return api_client.call(url='/api/queue/start', call_type=APIType.GET)

def queue_hasher_get() -> QueueInfo:
    """Return information about Hasher queue"""
    response = api_client.call(url='/api/queue/hasher/get', call_type=APIType.GET)
    _json = json.loads(response)
    return QueueInfo.Decoder(_json)

def queue_hasher_pause():
    """Pause hasher queue"""
    return api_client.call(url='/api/queue/hasher/pause', call_type=APIType.GET)

def queue_hasher_start():
    """Start Queue from Pause state"""
    return api_client.call(url='/api/queue/hasher/start', call_type=APIType.GET)

def queue_hasher_clear():
    """Clear Queue and Restart it"""
    return api_client.call(url='/api/queue/hasher/clear', call_type=APIType.GET)

def queue_general_get() -> QueueInfo:
    """Return information about general queue"""
    response = api_client.call(url='/api/queue/general/get', call_type=APIType.GET)
    _json = json.loads(response)
    return QueueInfo.Decoder(_json)

def queue_general_pause():
    """Pause general queue"""
    return api_client.call(url='/api/queue/general/pause', call_type=APIType.GET)

def queue_general_start():
    """Start Queue from Pause state"""
    return api_client.call(url='/api/queue/general/start', call_type=APIType.GET)

def queue_general_clear():
    """Clear Queue and Restart it"""
    return api_client.call(url='/api/queue/general/clear', call_type=APIType.GET)

def queue_images_get() -> QueueInfo:
    """Return information about images queue"""
    response = api_client.call(url='/api/queue/images/get', call_type=APIType.GET)
    _json = json.loads(response)
    return QueueInfo.Decoder(_json)

def queue_images_pause():
    """Pause images queue"""
    return api_client.call(url='/api/queue/images/pause', call_type=APIType.GET)

def queue_images_start():
    """Start Queue from Pause state"""
    return api_client.call(url='/api/queue/images/start', call_type=APIType.GET)

def queue_images_clear():
    """Clear Queue and Restart it"""
    return api_client.call(url='/api/queue/images/clear', call_type=APIType.GET)

def file(id: int = 0, limit: int = 0, level: int = 0):
    """Returns list of `RawFile` object by given `id`"""
    # if I supply ID, then why it must response with list?
    query = {
        'id': id,
        'limit': limit,
        'level': level
    }
    response = api_client.call(url='/api/file', call_type=APIType.GET, query=query)
    _json = json.loads(response)
    output: list[RawFile] = []
    for file in _json:
        output.append(RawFile.Decoder(file))
    return output

def file_needs_av_dumped(level: int):
    """Gets files whose data does not match AniDB
    
    Return list of `RawFile`"""
    query = {
        'level': level
    }
    response = api_client.call(url='/api/file/needsavdumped', call_type=APIType.GET, query=query)
    _json = json.loads(response)
    output: list[RawFile] = []
    for file in _json:
        output.append(RawFile.Decoder(file))
    return output

def av_dump_mismatched_files():
    """Gets files whose data does not match AniDB and dump it"""
    return api_client.call(url='/api/avdumpmismatchedfiles', call_type=APIType.GET)

def file_deprecated(level: int):
    """
    Gets files that are deprecated on AniDB
    """
    query = {
        'level': level
    }
    response = api_client.call(url='/api/file/deprecated', call_type=APIType.GET, query=query)
    _json = json.loads(response)
    output: list[RawFile] = []
    for file in _json:
        output.append(RawFile.Decoder(file))
    return output

def file_multiple(opts: QueryOptions = QueryOptions()):
    response = api_client.call(url='/api/file/multiple', call_type=APIType.GET, query=opts.__dict__)
    _json = json.loads(response)
    output: list[Serie] = []
    for file in _json:
        output.append(Serie.Decoder(file))
    return output
    # return api_client.call(url='/api/file/multiple', call_type=APIType.GET, query=opts.__dict__)

def file_count() -> Counter:
    response = api_client.call(url='/api/file/count', call_type=APIType.GET)
    _json = json.loads(response)
    return Counter.Decoder(_json)

def file_recent(limit: int = 0, level: int = 0):
    """Get recent files"""
    query = {
        'limit': limit,
        'level': level
    }
    response = api_client.call(url='/api/file/recent', call_type=APIType.GET, query=query)
    _json = json.loads(response)
    output: list[RecentFile] = []
    for file in _json:
        output.append(RecentFile.Decoder(file))
    return output

def file_unsort(offset: int = 0, level: int = 0, limit: int = 0):
    """Get unsort files"""
    query = {
        'offset': offset,
        'limit': limit,
        'level': level
    }
    response = api_client.call(url='/api/file/unsort', call_type=APIType.GET, query=query)
    _json = json.loads(response)
    output: list[RawFile] = []
    for file in _json:
        output.append(RawFile.Decoder(file))
    return output

def file_offset(opts: QueryOptions):
    """Set file offset

    `Id` and `offset` are required"""
    return api_client.call(url='/api/offset', call_type=APIType.POST, query=opts.__dict__)

def file_watch(id: int):
    """Mark file with `id` as watched"""
    query = {
        'id': id
    }
    return api_client.call(url='/api/watch', call_type=APIType.GET, query=query)

def episodes_get(opts: QueryOptions = QueryOptions()):
    """Get episodes"""
    response = api_client.call(url='/api/ep', call_type=APIType.GET, query=opts.__dict__)
    _json = json.loads(response)
    output: list[Episode] = []
    for episode in _json:
        output.append(Episode.Decoder(episode))
    return output

def episode_get_by_filename(filename: str, pic: int = 1):
    """Get episode by filename"""
    query = {
        'filename': filename,
        'pic': pic
    }
    response = api_client.call(url='/api/ep/getbyfilename', call_type=APIType.GET, query=query)
    _json = json.loads(response)
    return Episode.Decoder(_json)

def episodes_get_by_hash(hash: str, pic: int = 1):
    """Get episodes by hash"""
    query = {
        'hash': hash,
        'pic': pic
    }
    response = api_client.call(url='/api/ep/getbyhash', call_type=APIType.GET, query=query)
    _json = json.loads(response)
    output: list[Episode] = []
    for episode in _json:
        output.append(Episode.Decoder(episode))
    return output

def episodes_get_recent(opts: QueryOptions = QueryOptions()):
    """Get recent episodes
    """
    response = api_client.call(url='/api/ep/recent', call_type=APIType.GET, query=opts.__dict__)
    _json = json.loads(response)
    output: list[Episode] = []
    for episode in _json:
        output.append(Episode.Decoder(episode))
    return output

# TODO nie podoba mi sie output i parsowanie Serie i Episode, do sprawdzenia
def episodes_serie_get_missing(all: bool, pic: int, tagfilter: int):
    """Get episodes with no files"""
    query = {
        'all': all,
        'pic': pic,
        'tagfilter': tagfilter
    }
    response = api_client.call(url='/api/ep/missing', call_type=APIType.GET, query=query)
    _json = json.loads(response)
    output: list[Serie] = []
    for serie in _json:
        # print(serie['aid'])
        output.append(Serie.Decoder(serie))
    return output

apikey = login_user(AuthUser(user="default", password=""))
api_client.apikey = apikey['apikey']
print(api_client.apikey)

# rehash()

# print(episode_get_by_filename(filename="91 Days - s01e01.mkv"))
# print(episodes_get_by_hash(hash="ECE790DE96606EBAFB57A4342EA000BF"))
# print(episodes_get_recent(QueryOptions(query="Days")))
# print(episodes_serie_get_missing(True, 1, 0))
series = episodes_serie_get_missing(False, 1, 0)
print(series.__len__())
serie = series[0]
print(f"===={serie.name}===")
print(serie.aid)
# print(serie.eps)
# for ep in serie.eps:
    # print(ep.id)
    # print(ep.name)