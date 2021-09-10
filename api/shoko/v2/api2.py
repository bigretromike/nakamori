# -*- coding: utf-8 -*-

# BASED OF :8111/swagger/index.html?urls.primaryName=2.0

try:
    from api.common import APIClient, APIType
except:
    from ...common import APIClient, APIType
from api2models import *
import json

# read test config from file that is not sync with gh
with open("config.json") as file:
    config = json.load(file)
    address = config['address']
    port = config['port']
    version = config['version']
    apikey = config['apikey']
    timeout = config['timeout']

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
        output.append(Serie.Decoder(serie))
    return output

def episode_watch(id: int):
    """Mark episode watched"""
    query = {
        'id': id
    }
    return api_client.call(url='/api/ep/watch', call_type=APIType.GET, query=query)

def episode_unwatch(id: int):
    """Mark episode not watched"""
    query = {
        'id': id
    }
    return api_client.call(url='/api/ep/unwatch', call_type=APIType.GET, query=query)

def episode_vote(id: int, score: int):
    """Vote episode score"""
    query = {
        'id': id,
        'score': score
    }
    return api_client.call(url='/api/ep/vote', call_type=APIType.GET, query=query)

def episode_scrobble(id: int, progress: int, status: int, ismovie: bool):
    # TODO test it
    """Scrobble/rewind Trakt episode
    
    // status 1-start, 2-pause, 3-stop

    // progres 0-100
    
    // type 1-movie, 2-episode"""
    query = {
        'id': id,
        'progress': progress,
        'status': status,
        'ismovie': ismovie
    }
    return api_client.call(url='/api/ep/scrobble', call_type=APIType.GET, query=query)

def episode_last_watched(query: str, pic: int, level: int, limit: int, offset: int):
    # i guess query is date in yyyy-MM-dd format
    """Get list of last watched `Episodes`"""
    query = {
        'query': query,
        'pic': pic,
        'level': level,
        'limit': limit,
        'offset': offset
    }
    response = api_client.call(url='/api/ep/last_watched', call_type=APIType.GET, query=query)
    _json = json.loads(response)
    output: list[Episode] = []
    for ep in _json:
        output.append(Episode.Decoder(ep))
    return output

def series_get(opts: QueryOptions = QueryOptions):
    """Get list of `Series`"""
    response = api_client.call(url='/api/serie', call_type=APIType.GET, query=opts.__dict__)
    _json = json.loads(response)
    output: list[Serie] = []
    for serie in _json:
        output.append(Serie.Decoder(serie))
    return output

def series_count() -> Counter:
    """Get count of `Series`"""
    response = api_client.call(url='/api/serie/count', call_type=APIType.GET)
    _json = json.loads(response)
    return Counter.Decoder(_json)

def series_today(opts: QueryOptions = QueryOptions) -> Group:
    """Get list of "today" `Series`
    
    // 1. get series airing

    // 2. get eps for those series

    // 3. calculate which series have most of the files released today"""
    response = api_client.call(url='/api/serie/today', call_type=APIType.GET, query=opts.__dict__)
    _json = json.loads(response)
    return Group.Decoder(_json)

def series_bookmark(opts: QueryOptions = QueryOptions) -> Group:
    """Return bookmarked series"""
    response = api_client.call(url='/api/serie/bookmark', call_type=APIType.GET, query=opts.__dict__)
    _json = json.loads(response)
    return Group.Decoder(_json)

def series_bookmark_add(id: int):
    """Add serie (by anidb `id`) to bookmark"""
    query = {
        'id': id
    }
    return api_client.call(url='/api/serie/bookmark/add', call_type=APIType.GET, query=query)

def series_bookmark_remove(id: int):
    """Remove serie (by anidb `id`) from bookmark"""
    query = {
        'id': id
    }
    return api_client.call(url='/api/serie/bookmark/remove', call_type=APIType.GET, query=query)

def series_calendar_refresh():
    """Refresh calendar"""
    return api_client.call(url='/api/serie/calendar/refresh', call_type=APIType.GET)

def series_soon(opts: QueryOptions = QueryOptions) -> Group:
    """Return group of series airing soon"""
    response = api_client.call(url='/api/serie/soon', call_type=APIType.GET, query=opts.__dict__)
    _json = json.loads(response)
    return Group.Decoder(_json)

def series_calendar(opts: QueryOptions = QueryOptions) -> Group:
    """Return group of series airing soon"""
    response = api_client.call(url='/api/serie/calendar', call_type=APIType.GET, query=opts.__dict__)
    _json = json.loads(response)
    return Group.Decoder(_json)

def series_get_by_folder(opts: QueryOptions = QueryOptions):
    """Return list of series by folder"""
    response = api_client.call(url='/api/serie/byfolder', call_type=APIType.GET, query=opts.__dict__)
    _json = json.loads(response)
    output: list[Serie] = []
    for serie in _json:
        output.append(Serie.Decoder(serie))
    return output

def series_get_info_by_folder(id: int) -> FolderInfo:
    """Return series info by folder `id`"""
    query = {
        'id': id
    }
    response = api_client.call(url='/api/serie/infobyfolder', call_type=APIType.GET, query=query)
    _json = json.loads(response)
    return FolderInfo.Decoder(_json)

def series_get_recent(opts: QueryOptions = QueryOptions):
    """Return list of recent series"""
    response = api_client.call(url='/api/serie/recent', call_type=APIType.GET, query=opts.__dict__)
    _json = json.loads(response)
    output: list[Serie] = []
    for serie in _json:
        output.append(Serie.Decoder(serie))
    return output

def serie_watch(id: int):
    """Mark serie as watched"""
    query = {
        'id': id
    }
    return api_client.call(url='/api/serie/watch', call_type=APIType.GET, query=query)

def serie_unwatch(id: int):
    """Mark serie as unwatch"""
    query = {
        'id': id
    }
    return api_client.call(url='/api/serie/unwatch', call_type=APIType.GET, query=query)

def serie_vote(id: int, score: int):
    """Vote on serie"""
    query = {
        'id': id,
        'score': score
    }
    return api_client.call(url='/api/serie/vote', call_type=APIType.GET, query=query)

def series_search(opts: QueryOptions = QueryOptions()):
    """Return list of series"""
    response = api_client.call(url='/api/serie/search', call_type=APIType.GET, query=opts.__dict__)
    _json = json.loads(response)
    output: list[Serie] = []
    for serie in _json:
        output.append(Serie.Decoder(serie))
    return output

def series_search_tag(opts: QueryOptions = QueryOptions()):
    """Return list of series"""
    response = api_client.call(url='/api/serie/tag', call_type=APIType.GET, query=opts.__dict__)
    _json = json.loads(response)
    output: list[Serie] = []
    for serie in _json:
        output.append(Serie.Decoder(serie))
    return output

def series_from_ep(opts: QueryOptions = QueryOptions()) -> Serie:
    """Used to get the series related to the episode id.

    `id` of `QueryParams` must be specified
    
    Return list of series"""
    response = api_client.call(url='/api/serie/fromep', call_type=APIType.GET, query=opts.__dict__)
    _json = json.loads(response)
    return Serie.Decoder(_json)

def series_groups(opts: QueryOptions = QueryOptions()):
    """Get all related AnimeGroups for a series ID

    `id` of `QueryParams` must be specified
    
    Return list of series"""
    response = api_client.call(url='/api/serie/groups', call_type=APIType.GET, query=opts.__dict__)
    _json = json.loads(response)
    output: list[Group] = []
    for group in _json:
        output.append(Group.Decoder(group))
    return output

def series_from_anidb(opts: QueryOptions = QueryOptions()) -> Serie:
    """Used to get the series related to the episode id.
    
    `id` of `QueryParams` must be specified
    
    Return list of series"""
    response = api_client.call(url='/api/serie/fromaid', call_type=APIType.GET, query=opts.__dict__)
    _json = json.loads(response)
    return Serie.Decoder(_json)

#
# Core
#
def config_port_set(port: int):
    # not sure if it's working anymore
    """Set JMMServer Port"""
    query = {
        'port': port
    }
    return api_client.call(url='/api/config/port/set', call_type=APIType.POST, query=query)

def config_port_get() -> dict:
    """Get JMMServer Port
    
    Returns dict like response['port']"""
    response = api_client.call(url='/api/config/port/get', call_type=APIType.GET)
    return json.loads(response)

apikey = login_user(AuthUser(user="default", password=""))
api_client.apikey = apikey['apikey']
print(api_client.apikey)

print((config_port_get())['port'])