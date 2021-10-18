# -*- coding: utf-8 -*-

# BASED OF :8111/swagger/index.html?urls.primaryName=2.0

from api.common import APIClient, APIType
from api.shoko.v2.api2models import *
import json
import os

# read test config from file that is not sync with gh
if os.path.exists("config.json"):
    with open("config.json") as file:
        config = json.load(file)
        address = config['address']
        port = config['port']
        version = config['version']
        apikey = config['apikey']
        timeout = config['timeout']


class Client:
    def __init__(self, address: str = '127.0.0.1', port: int = 8111, version: int = 2, apikey: str = '', timeout: int = 120):
        self.address = address
        self.port = port
        self.version = version
        self.apikey = apikey
        self.timeout = timeout
        self.api_client = APIClient(api_proto='http', api_address=self.address, api_port=self.port, api_version=self.version, api_key=self.apikey, timeout=self.timeout)
    
    #
    # Auth
    #
    def login_user(self, auth: AuthUser) -> str:
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
        return self.api_client.call(url='/api/auth', call_type=APIType.POST, data=data, auth=False)
    
    def delete_user_apikey(self, apikey: str):
        """
        Delete an APIKey from the database.
        
        Parameters
        ---
            apikey : str
                The API key to delete
        """
        query = {'apikey': apikey}
        return self.api_client.call(url='/api/auth', call_type=APIType.DELETE, query=query, auth=False)
    
    def change_user_password(self, password: str):
        """
        Change user password
    
        Parameters
        ---
            password : str
                new password
        """
        data = f"{password}"
        return self.api_client.call(url='/api/auth/ChangePassword', call_type=APIType.POST, data=data)
    
    #
    # Common
    #
    def cloud_list(self):
        # 501: Not Implemented
        return self.api_client.call(url='/api/cloud/list', call_type=APIType.GET)
    
    def cloud_count(self):
        # 501: Not Implemented
        return self.api_client.call(url='/api/cloud/count', call_type=APIType.GET)
    
    def cloud_add(self):
        # 501: Not Implemented
        return self.api_client.call(url='/api/cloud/add', call_type=APIType.POST)
    
    def cloud_delete(self):
        # 501: Not Implemented
        return self.api_client.call(url='/api/cloud/delete', call_type=APIType.POST)
    
    def cloud_import(self):
        # 501: Not Implemented
        return self.api_client.call(url='/api/cloud/import', call_type=APIType.POST)
    
    def filter(self, opts: QueryOptions = QueryOptions()) -> Filter:
        response = self.api_client.call(url='/api/filter', call_type=APIType.GET, query=opts.__dict__)
        return Filter.Decoder(response)

    def filters(self, opts: QueryOptions = QueryOptions()) -> Filters:
        response = self.api_client.call(url='/api/filter', call_type=APIType.GET, query=opts.__dict__)
        return Filters.Decoder(response)
    
    def group(self, opts: QueryOptions = QueryOptions()):
        response = self.api_client.call(url='/api/group', call_type=APIType.GET, query=opts.__dict__)
        output: list[Group] = []
        for group in response:
            output.append(Group.Decoder(group))
        return output
    
    def group_watch(self, id: int):
        query = {
            'id': id
        }
        return self.api_client.call(url='/api/group/watch', call_type=APIType.GET, query=query)
    
    def group_search(self, opts: QueryOptions = QueryOptions()):
        response = self.api_client.call(url='/api/group/search', call_type=APIType.GET, query=opts.__dict__)
        # _json = json.loads(response)
        output: list[Group] = []
        for group in response:
            output.append(Group.Decoder(group))
        return output
    
    def cast_by_series(self, id: int):
        query = {
            'id': id
        }
        response = self.api_client.call(url='/api/cast/byseries', call_type=APIType.GET, query=query)
        # _json = json.loads(response)
        output: list[Role] = []
        for role in response:
            output.append(Role.Decoder(role))
        return output
    
    def cast_search(self, opts: QueryOptions = QueryOptions()):
        response = self.api_client.call(url='/api/cast/search', call_type=APIType.GET, query=opts.__dict__)
        # _json = json.loads(response)
        return Filter.Decoder(response)
    
    def links_serie(self, id: int):
        query = {
            'id': id
        }
        return self.api_client.call(url='/api/links/serie', call_type=APIType.GET, query=query)
    
    def folder_list(self):
        """
        List all saved Import Folders
        """
        response = self.api_client.call(url='/api/folder/list', call_type=APIType.GET)
        # _json = json.loads(response)
        output: list[ImportFolder] = []
        for folder in response:
            output.append(ImportFolder.Decoder(folder))
        return output
    
    def folder_count(self) -> Counter:
        """
        Get import folders count
        """
        response = self.api_client.call(url='/api/folder/count', call_type=APIType.GET)
        # _json = json.loads(response)
        return Counter.Decoder(response)
    
    def folder_add(self, folder: ImportFolder) -> ImportFolder:
        """
        Add Folder to Import Folders Repository
        """
        response = self.api_client.call(url='/api/folder/add', call_type=APIType.POST, data=folder.__dict__)
        # _json = json.loads(response)
        return ImportFolder.Decoder(response)
    
    def folder_edit(self, folder: ImportFolder) -> ImportFolder:
        """
        Edit folder giving fulll ImportFolder object with ID
        """
        response = self.api_client.call(url='/api/folder/edit', call_type=APIType.POST, data=folder.__dict__)
        # _json = json.loads(response)
        return ImportFolder.Decoder(response)
    
    def folder_delete(self, id: int):
        """
        Delete Import Folder out of Import Folder Repository
        """
        query = {
            'folderId': id
        }
        return self.api_client.call(url='/api/folder/delete', call_type=APIType.POST, query=query)
    
    def folder_import(self):
        """
        Run Import action on all Import Folders inside Import Folders Repository
        """
        return self.api_client.call(url='/api/folder/import', call_type=APIType.GET)
    
    def folder_scan(self):
        """
        Scan All Drop Folders
        """
        return self.api_client.call(url='/api/folder/scan', call_type=APIType.GET)
    
    def remove_missing_files(self):
        """
        Scans your import folders and remove files from your database that are no longer in your collection.
        """
        return self.api_client.call(url='/api/remove_missing_files', call_type=APIType.GET)
    
    def stats_update(self):
        """
        Updates all series stats such as watched state and missing files.
        """
        return self.api_client.call(url='/api/stats_update', call_type=APIType.GET)
    
    def mediainfo_update(self):
        """
        Updates all technical details about the files in your collection via running MediaInfo on them.
        """
        # typo in API endpoint?
        # should be media? meta?
        # assumed to be mediainfo
        return self.api_client.call(url='/api/medainfo_update', call_type=APIType.GET)
    
    def hash_sync(self):
        """
        Sync Hashes - download/upload hashes from/to webcache
        """
        return self.api_client.call(url='/api/hash/sync', call_type=APIType.GET)
    
    def foler_rescan(self, id: int):
        """Accoring to Shoko.Server source code:
        "Rescan ImportFolder (with given `id`) to recognize new episodes"
        """
        query = {
            'id': id
        }
        return self.api_client.call(url='/api/rescan', call_type=APIType.GET, query=query)
    
    def rescan_unlinked(self):
        """Accoring to Shoko.Server source code:
        "files which have been hashed, but don't have an associated episode"
        """
        return self.api_client.call(url='/api/rescanunlinked', call_type=APIType.GET)
    
    def rescan_manual_links(self):
        """Accoring to Shoko.Server source code:
        "files which have been hashed, but don't have an associated episode"
        """
        return self.api_client.call(url='/api/rescanmanuallinks', call_type=APIType.GET)
    
    def rehash(self, id: int):
        """Accoring to Shoko.Server source code:
        "Rehash given files in given VideoLocal"
        """
        query = {
            'id': id
        }
        return self.api_client.call(url='/api/rehash', call_type=APIType.GET, query=query)
    
    def rehash_unlinked(self):
        """Accoring to Shoko.Server source code:
        "files which have been hashed, but don't have an associated episode"
        """
        return self.api_client.call(url='/api/rehashunlinked', call_type=APIType.GET)
    
    def rehash_manual_links(self):
        """Accoring to Shoko.Server source code:
        "files which have been hashed, but don't have an associated episode"
        """
        return self.api_client.call(url='/api/rehashmanuallinks', call_type=APIType.GET)
    
    def myid_get(self) -> dict:
        """Accoring to Shoko.Server source code:
        "Returns current user ID for use in legacy calls"
        """
        return json.loads(self.api_client.call(url='/api/myid/get', call_type=APIType.GET))
    
    def news_get(self, max: int):
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
        response = self.api_client.call(url='/api/news/get', call_type=APIType.GET, query=query)
        # _json = json.loads(response)
        output: list[WebNews] = []
        for new in response:
            output.append(WebNews.Decoder(new))
        return output
    
    def search(self, opts: QueryOptions = QueryOptions()):
        response = self.api_client.call(url='/api/search', call_type=APIType.GET, query=opts.__dict__)
        # _json = json.loads(response)
        return Filter.Decoder(response)
    
    def serie_startswith(self, opts: QueryOptions = QueryOptions()):
        response = self.api_client.call(url='/api/serie/startswith', call_type=APIType.GET, query=opts.__dict__)
        # _json = json.loads(response)
        return Filter.Decoder(response)
    
    def ping(self) -> dict:
        """
        Check if connection and auth is valid without ask for real data
        """
        return json.loads(self.api_client.call(url='/api/ping', call_type=APIType.GET))
    
    def queue_get(self):
        """Get current information about Queues (hash, general, images)
    
        Returns dictionary:
    
        {
            hasher : `QueueInfo`
            general : `QueueInfo`
            images : `QueueInfo`
        }"""
        response = self.api_client.call(url='/api/queue/get', call_type=APIType.GET)
        # _json: dict = json.loads(response)
        output: dict[str, QueueInfo] = {}
        for row in response.keys(self):
             queueinfo = QueueInfo.Decoder(response.get(row))
             output[row] = queueinfo
        return output
    
    def queue_pause(self):
        """Pause all (hasher, general, images) running Queues"""
        return self.api_client.call(url='/api/queue/pause', call_type=APIType.GET)
    
    def queue_start(self):
        """Start all (hasher, general, images) queues that are pasued"""
        return self.api_client.call(url='/api/queue/start', call_type=APIType.GET)
    
    def queue_hasher_get(self) -> QueueInfo:
        """Return information about Hasher queue"""
        response = self.api_client.call(url='/api/queue/hasher/get', call_type=APIType.GET)
        # _json = json.loads(response)
        return QueueInfo.Decoder(response)
    
    def queue_hasher_pause(self):
        """Pause hasher queue"""
        return self.api_client.call(url='/api/queue/hasher/pause', call_type=APIType.GET)
    
    def queue_hasher_start(self):
        """Start Queue from Pause state"""
        return self.api_client.call(url='/api/queue/hasher/start', call_type=APIType.GET)
    
    def queue_hasher_clear(self):
        """Clear Queue and Restart it"""
        return self.api_client.call(url='/api/queue/hasher/clear', call_type=APIType.GET)
    
    def queue_general_get(self) -> QueueInfo:
        """Return information about general queue"""
        response = self.api_client.call(url='/api/queue/general/get', call_type=APIType.GET)
        # _json = json.loads(response)
        return QueueInfo.Decoder(response)
    
    def queue_general_pause(self):
        """Pause general queue"""
        return self.api_client.call(url='/api/queue/general/pause', call_type=APIType.GET)
    
    def queue_general_start(self):
        """Start Queue from Pause state"""
        return self.api_client.call(url='/api/queue/general/start', call_type=APIType.GET)
    
    def queue_general_clear(self):
        """Clear Queue and Restart it"""
        return self.api_client.call(url='/api/queue/general/clear', call_type=APIType.GET)
    
    def queue_images_get(self) -> QueueInfo:
        """Return information about images queue"""
        response = self.api_client.call(url='/api/queue/images/get', call_type=APIType.GET)
        # _json = json.loads(response)
        return QueueInfo.Decoder(response)
    
    def queue_images_pause(self):
        """Pause images queue"""
        return self.api_client.call(url='/api/queue/images/pause', call_type=APIType.GET)
    
    def queue_images_start(self):
        """Start Queue from Pause state"""
        return self.api_client.call(url='/api/queue/images/start', call_type=APIType.GET)
    
    def queue_images_clear(self):
        """Clear Queue and Restart it"""
        return self.api_client.call(url='/api/queue/images/clear', call_type=APIType.GET)
    
    def file(self, id: int = 0, limit: int = 0, level: int = 0):
        """Returns list of `RawFile` object by given `id`"""
        # if I supply ID, then why it must response with list?
        query = {
            'id': id,
            'limit': limit,
            'level': level
        }
        response = self.api_client.call(url='/api/file', call_type=APIType.GET, query=query)
        # _json = json.loads(response)
        output: list[RawFile] = []
        for file in response:
            output.append(RawFile.Decoder(file))
        return output
    
    def file_needs_av_dumped(self, level: int):
        """Gets files whose data does not match AniDB
        
        Return list of `RawFile`"""
        query = {
            'level': level
        }
        response = self.api_client.call(url='/api/file/needsavdumped', call_type=APIType.GET, query=query)
        # _json = json.loads(response)
        output: list[RawFile] = []
        for file in response:
            output.append(RawFile.Decoder(file))
        return output
    
    def av_dump_mismatched_files(self):
        """Gets files whose data does not match AniDB and dump it"""
        return self.api_client.call(url='/api/avdumpmismatchedfiles', call_type=APIType.GET)
    
    def file_deprecated(self, level: int):
        """
        Gets files that are deprecated on AniDB
        """
        query = {
            'level': level
        }
        response = self.api_client.call(url='/api/file/deprecated', call_type=APIType.GET, query=query)
        # _json = json.loads(response)
        output: list[RawFile] = []
        for file in response:
            output.append(RawFile.Decoder(file))
        return output
    
    def file_multiple(self, opts: QueryOptions = QueryOptions()):
        response = self.api_client.call(url='/api/file/multiple', call_type=APIType.GET, query=opts.__dict__)
        # _json = json.loads(response)
        output: list[Serie] = []
        for file in response:
            output.append(Serie.Decoder(file))
        return output
        # return self.api_client.call(url='/api/file/multiple', call_type=APIType.GET, query=opts.__dict__)
    
    def file_count(self) -> Counter:
        response = self.api_client.call(url='/api/file/count', call_type=APIType.GET)
        # _json = json.loads(response)
        return Counter.Decoder(response)
    
    def file_recent(self, limit: int = 0, level: int = 0):
        """Get recent files"""
        query = {
            'limit': limit,
            'level': level
        }
        response = self.api_client.call(url='/api/file/recent', call_type=APIType.GET, query=query)
        # _json = json.loads(response)
        output: list[RecentFile] = []
        for file in response:
            output.append(RecentFile.Decoder(file))
        return output
    
    def file_unsort(self, offset: int = 0, level: int = 0, limit: int = 0):
        """Get unsort files"""
        query = {
            'offset': offset,
            'limit': limit,
            'level': level
        }
        response = self.api_client.call(url='/api/file/unsort', call_type=APIType.GET, query=query)
        # _json = json.loads(response)
        output: list[RawFile] = []
        for file in response:
            output.append(RawFile.Decoder(file))
        return output
    
    def file_offset(self, opts: QueryOptions):
        """Set file offset
    
        `Id` and `offset` are required"""
        return self.api_client.call(url='/api/offset', call_type=APIType.POST, query=opts.__dict__)
    
    def file_watch(self, id: int):
        """Mark file with `id` as watched"""
        query = {
            'id': id
        }
        return self.api_client.call(url='/api/watch', call_type=APIType.GET, query=query)
    
    def episodes_get(self, opts: QueryOptions = QueryOptions()):
        """Get episodes"""
        response = self.api_client.call(url='/api/ep', call_type=APIType.GET, query=opts.__dict__)
        # _json = json.loads(response)
        output: list[Episode] = []
        for episode in response:
            output.append(Episode.Decoder(episode))
        return output
    
    def episode_get_by_filename(self, filename: str, pic: int = 1):
        """Get episode by filename"""
        query = {
            'filename': filename,
            'pic': pic
        }
        response = self.api_client.call(url='/api/ep/getbyfilename', call_type=APIType.GET, query=query)
        # _json = json.loads(response)
        return Episode.Decoder(response)
    
    def episodes_get_by_hash(self, hash: str, pic: int = 1):
        """Get episodes by hash"""
        query = {
            'hash': hash,
            'pic': pic
        }
        response = self.api_client.call(url='/api/ep/getbyhash', call_type=APIType.GET, query=query)
        # _json = json.loads(response)
        output: list[Episode] = []
        for episode in response:
            output.append(Episode.Decoder(episode))
        return output
    
    def episodes_get_recent(self, opts: QueryOptions = QueryOptions()):
        """Get recent episodes
        """
        response = self.api_client.call(url='/api/ep/recent', call_type=APIType.GET, query=opts.__dict__)
        # _json = json.loads(response)
        output: list[Episode] = []
        for episode in response:
            output.append(Episode.Decoder(episode))
        return output
    
    def episodes_serie_get_missing(self, all: bool, pic: int, tagfilter: int):
        """Get episodes with no files"""
        query = {
            'all': all,
            'pic': pic,
            'tagfilter': tagfilter
        }
        response = self.api_client.call(url='/api/ep/missing', call_type=APIType.GET, query=query)
        # _json = json.loads(response)
        output: list[Serie] = []
        for serie in response:
            output.append(Serie.Decoder(serie))
        return output
    
    def episode_watch(self, id: int):
        """Mark episode watched"""
        query = {
            'id': id
        }
        return self.api_client.call(url='/api/ep/watch', call_type=APIType.GET, query=query)
    
    def episode_unwatch(self, id: int):
        """Mark episode not watched"""
        query = {
            'id': id
        }
        return self.api_client.call(url='/api/ep/unwatch', call_type=APIType.GET, query=query)
    
    def episode_vote(self, id: int, score: int):
        """Vote episode score"""
        query = {
            'id': id,
            'score': score
        }
        return self.api_client.call(url='/api/ep/vote', call_type=APIType.GET, query=query)
    
    def episode_scrobble(self, id: int, progress: int, status: int, ismovie: bool):
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
        return self.api_client.call(url='/api/ep/scrobble', call_type=APIType.GET, query=query)
    
    def episode_last_watched(self, query: str, pic: int, level: int, limit: int, offset: int):
        # i guess query is date in yyyy-MM-dd format
        """Get list of last watched `Episodes`"""
        query = {
            'query': query,
            'pic': pic,
            'level': level,
            'limit': limit,
            'offset': offset
        }
        response = self.api_client.call(url='/api/ep/last_watched', call_type=APIType.GET, query=query)
        # _json = json.loads(response)
        output: list[Episode] = []
        for ep in response:
            output.append(Episode.Decoder(ep))
        return output
    
    def series_get(self, opts: QueryOptions = QueryOptions):
        """Get list of `Series`"""
        response = self.api_client.call(url='/api/serie', call_type=APIType.GET, query=opts.__dict__)
        # _json = json.loads(response)
        output: list[Serie] = []
        for serie in response:
            output.append(Serie.Decoder(serie))
        return output

    def series_get_by_id(self, opts: QueryOptions = QueryOptions):
        """Get list of `Series`"""
        response = self.api_client.call(url='/api/serie', call_type=APIType.GET, query=opts.__dict__)
        output: Serie = Serie.Decoder(response)
        return output
    
    def series_count(self) -> Counter:
        """Get count of `Series`"""
        response = self.api_client.call(url='/api/serie/count', call_type=APIType.GET)
        # _json = json.loads(response)
        return Counter.Decoder(response)
    
    def series_today(self, opts: QueryOptions = QueryOptions) -> Group:
        """Get list of "today" `Series`
        
        // 1. get series airing
    
        // 2. get eps for those series
    
        // 3. calculate which series have most of the files released today"""
        response = self.api_client.call(url='/api/serie/today', call_type=APIType.GET, query=opts.__dict__)
        # _json = json.loads(response)
        return Group.Decoder(response)
    
    def series_bookmark(self, opts: QueryOptions = QueryOptions) -> Group:
        """Return bookmarked series"""
        response = self.api_client.call(url='/api/serie/bookmark', call_type=APIType.GET, query=opts.__dict__)
        # _json = json.loads(response)
        return Group.Decoder(response)
    
    def series_bookmark_add(self, id: int):
        """Add serie (by anidb `id`) to bookmark"""
        query = {
            'id': id
        }
        return self.api_client.call(url='/api/serie/bookmark/add', call_type=APIType.GET, query=query)
    
    def series_bookmark_remove(self, id: int):
        """Remove serie (by anidb `id`) from bookmark"""
        query = {
            'id': id
        }
        return self.api_client.call(url='/api/serie/bookmark/remove', call_type=APIType.GET, query=query)
    
    def series_calendar_refresh(self):
        """Refresh calendar"""
        return self.api_client.call(url='/api/serie/calendar/refresh', call_type=APIType.GET)
    
    def series_soon(self, opts: QueryOptions = QueryOptions) -> Group:
        """Return group of series airing soon"""
        response = self.api_client.call(url='/api/serie/soon', call_type=APIType.GET, query=opts.__dict__)
        # _json = json.loads(response)
        return Group.Decoder(response)
    
    def series_calendar(self, opts: QueryOptions = QueryOptions) -> Group:
        """Return group of series airing soon"""
        response = self.api_client.call(url='/api/serie/calendar', call_type=APIType.GET, query=opts.__dict__)
        # _json = json.loads(response)
        return Group.Decoder(response)
    
    def series_get_by_folder(self, opts: QueryOptions = QueryOptions):
        """Return list of series by folder"""
        response = self.api_client.call(url='/api/serie/byfolder', call_type=APIType.GET, query=opts.__dict__)
        # _json = json.loads(response)
        output: list[Serie] = []
        for serie in response:
            output.append(Serie.Decoder(serie))
        return output
    
    def series_get_info_by_folder(self, id: int) -> FolderInfo:
        """Return series info by folder `id`"""
        query = {
            'id': id
        }
        response = self.api_client.call(url='/api/serie/infobyfolder', call_type=APIType.GET, query=query)
        # _json = json.loads(response)
        return FolderInfo.Decoder(response)
    
    def series_get_recent(self, opts: QueryOptions = QueryOptions):
        """Return list of recent series"""
        response = self.api_client.call(url='/api/serie/recent', call_type=APIType.GET, query=opts.__dict__)
        # _json = json.loads(response)
        output: list[Serie] = []
        for serie in response:
            output.append(Serie.Decoder(serie))
        return output
    
    def serie_watch(self, id: int):
        """Mark serie as watched"""
        query = {
            'id': id
        }
        return self.api_client.call(url='/api/serie/watch', call_type=APIType.GET, query=query)
    
    def serie_unwatch(self, id: int):
        """Mark serie as unwatch"""
        query = {
            'id': id
        }
        return self.api_client.call(url='/api/serie/unwatch', call_type=APIType.GET, query=query)
    
    def serie_vote(self, id: int, score: int):
        """Vote on serie"""
        query = {
            'id': id,
            'score': score
        }
        return self.api_client.call(url='/api/serie/vote', call_type=APIType.GET, query=query)
    
    def series_search(self, opts: QueryOptions = QueryOptions()):
        """Return list of series"""
        response = self.api_client.call(url='/api/serie/search', call_type=APIType.GET, query=opts.__dict__)
        # _json = json.loads(response)
        output: list[Serie] = []
        for serie in response:
            output.append(Serie.Decoder(serie))
        return output
    
    def series_search_tag(self, opts: QueryOptions = QueryOptions()):
        """Return list of series"""
        response = self.api_client.call(url='/api/serie/tag', call_type=APIType.GET, query=opts.__dict__)
        # _json = json.loads(response)
        output: list[Serie] = []
        for serie in response:
            output.append(Serie.Decoder(serie))
        return output
    
    def series_from_ep(self, opts: QueryOptions = QueryOptions()) -> Serie:
        """Used to get the series related to the episode id.
    
        `id` of `QueryParams` must be specified
        
        Return list of series"""
        response = self.api_client.call(url='/api/serie/fromep', call_type=APIType.GET, query=opts.__dict__)
        # _json = json.loads(response)
        return Serie.Decoder(response)
    
    def series_groups(self, opts: QueryOptions = QueryOptions()):
        """Get all related AnimeGroups for a series ID
    
        `id` of `QueryParams` must be specified
        
        Return list of series"""
        response = self.api_client.call(url='/api/serie/groups', call_type=APIType.GET, query=opts.__dict__)
        # _json = json.loads(response)
        output: list[Group] = []
        for group in response:
            output.append(Group.Decoder(group))
        return output
    
    def series_from_anidb(self, opts: QueryOptions = QueryOptions()) -> Serie:
        """Used to get the series related to the episode id.
        
        `id` of `QueryParams` must be specified
        
        Return list of series"""
        response = self.api_client.call(url='/api/serie/fromaid', call_type=APIType.GET, query=opts.__dict__)
        # _json = json.loads(response)
        return Serie.Decoder(response)
    
    #
    # Core
    #
    def config_port_set(self, port: int):
        # not sure if it's working anymore, 500: Internal Server Error
        """Set JMMServer Port"""
        query = {
            'port': port
        }
        return self.api_client.call(url='/api/config/port/set', call_type=APIType.POST, query=query)
    
    def config_port_get(self) -> dict:
        """Get JMMServer Port
        
        Returns dict like response['port']"""
        return self.api_client.call(url='/api/config/port/get', call_type=APIType.GET)
    
    def config_image_path_set(self, image_path: ImagePath):
        # 500: Internal Server Error
        """Set Imagepath as default or custom"""
        return self.api_client.call(url='/api/config/imagepath/set', call_type=APIType.POST, data=image_path.__dict__)
    
    def config_image_path_get(self) -> ImagePath:
        """Return ImagePath object"""
        response = self.api_client.call(url='/api/config/imagepath/get', call_type=APIType.GET)
        # _json = json.loads(response)
        return ImagePath.Decoder(response)
    
    def config_export(self) -> ServerSettingsExport:
        """Return body of current working settings.json - this could act as backup"""
        response = self.api_client.call(url='/api/config/export', call_type=APIType.GET)
        # _json = json.loads(response)
        return ServerSettingsExport.Decoder(response)
    
    def config_import(self, settings: ServerSettingsImport):
        """Import config file that was sent to in API body - this act as import from backup"""
        return self.api_client.call(url='/api/config/import', call_type=APIType.POST, data=settings.__dict__)
    
    def config_get(self):
        return "Use APIv3's implementation"
    
    def config_set(self):
        return "Use APIv3's JsonPatch implementation"
    
    def config_set_multiple(self):
        return "Use APIv3's JsonPatch implementation"
    
    def anidb_set(self, creds: Credentials):
        # 500: Internal Server Error
        """Set AniDB account with login, password and client port"""
        return self.api_client.call(url='/api/anidb/set', call_type=APIType.POST, data=creds.__dict__)
    
    def anidb_test_creds(self):
        # 500: Internal Server Error
        """Test AniDB Creditentials"""
        return self.api_client.call(url='/api/anidb/test', call_type=APIType.GET)
    
    def anidb_get(self) -> Credentials:
        """Return login/password/port of used AniDB"""
        response = self.api_client.call(url='/api/anidb/get', call_type=APIType.GET)
        # print(response)
        # _json = json.loads(response)
        return Credentials.Decoder(response)
    
    def anidb_votes_sync(self):
        # 500: Internal Server Error
        """Sync votes bettween Local and AniDB and only upload to MAL"""
        return self.api_client.call(url='/api/anidb/votes/sync', call_type=APIType.GET)
    
    def anidb_list_sync(self):
        # 500: Internal Server Error
        """Sync AniDB List"""
        return self.api_client.call(url='/api/anidb/list/sync', call_type=APIType.GET)
    
    def anidb_update(self):
        # 500: Internal Server Error
        """Update all series infromation from AniDB"""
        return self.api_client.call(url='/api/anidb/update', call_type=APIType.GET)
    
    def anidb_update_missing_cache(self):
        # 500: Internal Server Error
        """Update aniDB missing cache"""
        return self.api_client.call(url='/api/anidb/updatemissingcache', call_type=APIType.GET)
    
    def trakt_get_code(self) -> dict:
        """Get Trakt code and url
        
        Returns `dict` with `usercode` and `url`"""
        return self.api_client.call(url='/api/trakt/code', call_type=APIType.GET)
    
    def trakt_get(self) -> Credentials:
        """Return trakt authtoken"""
        response = self.api_client.call(url='/api/trakt/get', call_type=APIType.GET)
        return Credentials.Decoder(response)
    
    def trakt_sync(self):
        """Sync Trakt Collection"""
        return self.api_client.call(url='/api/trakt/sync', call_type=APIType.GET)
    
    def trakt_scan(self):
        # 500: Internal Server Error
        """Scan Trakt"""
        return self.api_client.call(url='/api/trakt/scan', call_type=APIType.GET)
    
    def trakt_set(self):
        """Not Implemented"""
        pass
    
    def trakt_create(self):
        """Not Implemented"""
        pass
    
    def tvdb_update(self):
        # 500: Internal Server Error
        """Scan TvDB"""
        return self.api_client.call(url='/api/tvdb/update', call_type=APIType.GET)
    
    def tvdb_regenrate_links(self):
        # 500: Internal Server Error
        """Regenerate All Episode Links"""
        return self.api_client.call(url='/api/tvdb/regenlinks', call_type=APIType.GET)
    
    def tvdb_check_links(self):
        """Check links"""
        return self.api_client.call(url='/api/tvdb/checklinks', call_type=APIType.GET)
    
    def moviedb_update(self):
        # 500: Internal Server Error
        """Scan MovieDB"""
        return self.api_client.call(url='/api/moviedb/update', call_type=APIType.GET)
    
    def user_list(self) -> dict:
        """Get all users
        
        Returns `dict<int, str>`
    
        `int` = id, `string` = username"""
        return self.api_client.call(url='/api/user/list', call_type=APIType.GET)
    
    def user_create(self, user: JMMUser):
        # 500: Internal Server Error
        """Create user from Contract_JMMUser"""
        return self.api_client.call(url='/api/user/create', call_type=APIType.POST, data=user.__dict__)
    
    def user_change_password(self, user: JMMUser):
        # 500: Internal Server Error
        """change current user password"""
        return self.api_client.call(url='/api/user/password', call_type=APIType.POST, data=user.__dict__)
    
    def user_change_password_by_uid(self, uid: int, user: JMMUser):
        # 500: Internal Server Error
        """change current user password by uid"""
        return self.api_client.call(url=f'/api/user/password/{uid}', call_type=APIType.POST, data=user.__dict__)
    
    def user_delete(self, user: JMMUser):
        # 500: Internal Server Error
        """Delete user from his ID"""
        return self.api_client.call(url='/api/user/delete', call_type=APIType.POST, data=user.__dict__)
    
    def os_folder_base(self) -> OSFolder:
        """Return OSFolder object that is a folder from which jmmserver is running"""
        response = self.api_client.call(url='/api/os/folder/base', call_type=APIType.GET)
        return OSFolder.Decoder(response)
    
    def os_folder_get(self, folder: OSFolder) -> OSFolder:
        """Return OSFolder object of directory that was given via folder
    
        Create OSFolder with at least `full_path` to receive OSFolder, trade that's fair enough :)"""
        response = self.api_client.call(url='/os/folder', call_type=APIType.POST, data=folder.__dict__)
        return OSFolder.Decoder(response)
    
    def os_drives(self) -> OSFolder:
        """Return OSFolder with subdirs as every driver on local system"""
        response = self.api_client.call(url='/api/os/drives', call_type=APIType.GET)
        return OSFolder.Decoder(response)
    
    def log_run(self):
        # 500: Internal Server Error
        """Run LogRotator with current settings"""
        return self.api_client.call(url='/api/log/get', call_type=APIType.GET)
    
    def log_set_rotate(self, logs: Logs):
        # 500: Internal Server Error
        """Set settings for LogRotator"""
        return self.api_client.call(url='/api/log/rotate', call_type=APIType.POST, data=logs.__dict__)
    
    def log_get_rotate(self) -> Logs:
        """Get settings for LogRotator"""
        response = self.api_client.call(url='/api/log/rotate', call_type=APIType.GET)
        return Logs.Decoder(response)
    
    def log_get(self, lines: int = 10, position: int = 0) -> dict:
        """
        Return int position - current position
    
        Return string[] lines - lines from current log file
        Parameters
        ---
           - `lines` - max lines to return
           - `position` - position to seek
        """
        return self.api_client.call(url=f'/api/log/get/{lines}/{position}', call_type=APIType.GET)
    
    def images_update(self):
        # 500: Internal Server Error
        """Update images"""
        return self.api_client.call(url='/api/images/update', call_type=APIType.GET)
    
    #
    # DashboardModules
    #
    def modules(self) -> dict:
        """Return Dictionary<str, obj> with nesesery items for Dashboard inside Webui"""
        return self.api_client.call(url='/api/modules', call_type=APIType.GET)
    
    #
    # Dev
    #
    def dev_media_by_id(self, id: int) -> Media:
        """Get media by id"""
        response = self.api_client.call(url=f'/api/dev/Media/{id}', call_type=APIType.GET)
        return Media.Decoder(response)
    
    #
    # Image
    #
    def image_validate_all(self):
        # 500: Internal Server Error
        """Validate all images"""
        return self.api_client.call(url=f'/api/v2/image/validateall', call_type=APIType.GET)
    
    def image_get_image_by_id_and_type(self, id: int, type: int):
        """Return image with given id, type
        
        Note: It prints out actual file content, not any python object"""
        return self.api_client.call(url=f'/api/v2/image/{type}/{id}', call_type=APIType.GET)
    
    def image_get_image_thumb_by_id_and_type(self, id: int, type: int, ratio: str = '0'):
        """Return thumb with given id, type
        
        Note: It prints out actual file content, not any python object"""
        return self.api_client.call(url=f'/api/v2/image/thumb/{type}/{id}/{ratio}', call_type=APIType.GET)
    
    def image_get_support_image_by_name(self, image_name: str):
        # 500: Internal Server Error
        """Return SupportImage (build-in server)
        """
        return self.api_client.call(url=f'/api/v2/image/support/{image_name}', call_type=APIType.GET)
    
    def image_get_support_image_by_name(self, image_name: str, ratio: str):
        # 500: Internal Server Error
        """Return SupportImage (build-in server)
        """
        return self.api_client.call(url=f'/api/v2/image/support/{image_name}/{ratio}', call_type=APIType.GET)
    
    def image_random_by_type(self, type: int):
        """Return random image with given type and not from restricted content"""
        return self.api_client.call(url=f'/api/v2/image/{type}/random', call_type=APIType.GET)
    
    #
    # Init
    #
    def init_version_get(self):
        """Return current version of ShokoServer and several modules
        
        This will work after init"""
        response = self.api_client.call(url='/api/init/version', call_type=APIType.GET)
        output: List[ComponentVersion] = []
        for component in response:
            output.append(ComponentVersion.Decoder(component))
        return output
    
    def init_status_get(self) -> ServerStatus:
        """Gets various information about the startup status of the server"""
        response = self.api_client.call(url='/api/init/status', call_type=APIType.GET)
        return ServerStatus.Decoder(response)
    
    def init_is_in_use(self) -> bool:
        """Gets whether anything is actively using the API"""
        return self.api_client.call(url='/api/init/inuse', call_type=APIType.GET)
    
    def init_default_user_get(self) -> Credentials:
        # 403: Forbidden
        """Gets the Default user's credentials. Will only return on first run"""
        response = self.api_client.call(url='/api/init/defaultuser', call_type=APIType.GET)
        return Credentials.Decoder(response)
    
    def init_default_user_set(self, creds: Credentials):
        # 403: Forbidden
        """Sets the default user's credentials"""
        return self.api_client.call(url='/api/init/defaultuser', call_type=APIType.POST, data=creds.__dict__)
    
    def init_start_server(self):
        # 500: Internal Server Error
        """Starts the server, or does nothing"""
        return self.api_client.call(url='/api/init/startserver', call_type=APIType.GET)
    
    def init_anidb_set(self, creds: Credentials):
        """Set AniDB account credentials with a Credentials object"""
        return self.api_client.call(url='/api/init/anidb', call_type=APIType.POST, data=creds.__dict__)
    
    def init_anidb_get(self) -> Credentials:
        # 403: Forbidden
        """Return existing login and ports for AniDB"""
        response = self.api_client.call(url='/api/init/anidb', call_type=APIType.GET)
        return Credentials.Decoder(response)
    
    def init_anidb_test(self):
        # 403: Forbidden
        """Test AniDB Creditentials"""
        return self.api_client.call(url='/api/init/anidb/test', call_type=APIType.GET)
    
    def init_database_get(self) -> DatabaseSettings:
        # 403: Forbidden
        """Get Database Settings"""
        response = self.api_client.call(url='/api/init/database', call_type=APIType.GET)
        return DatabaseSettings.Decoder(response)
    
    def init_database_set(self, settings: DatabaseSettings):
        # 403: Forbidden
        """Set Database Settings"""
        return self.api_client.call(url='/api/init/database', call_type=APIType.POST, data=settings.__dict__)
    
    def init_database_test(self):
        # 403: Forbidden
        """Test Database Connection with Current Settings"""
        return self.api_client.call(url='/api/init/database/test', call_type=APIType.GET)
    
    def init_database_sql_server_instance_get(self) -> List[str]:
        # 403: Forbidden
        """Get SQL Server Instances Running on this Machine"""
        return self.api_client.call(url='/api/init/database/sqlserverinstance', call_type=APIType.GET)
    
    def init_config_export(self) -> ServerSettingsExport:
        """Return body of current working settings.json - this could act as backup"""
        response = self.api_client.call(url='/api/init/config', call_type=APIType.GET)
        # _json = json.loads(response)
        return ServerSettingsExport.Decoder(response)
    
    #
    # PlexWebhook
    #
    def plex_json(self, json: object):
        # Not tested
        """Send json"""
        return self.api_client.call(url='/plex.json', call_type=APIType.POST, data=json)
    
    def plex(self, payload: object):
        # Not tested
        """Send payload"""
        return self.api_client.call(url='/plex', call_type=APIType.POST, data=payload)
    
    def plex_login_url_get(self) -> str:
        """Get login url"""
        response = self.api_client.call(url='/plex/loginurl', call_type=APIType.GET)
        return response.decode("utf-8")
    
    def plex_is_pin_authenticated(self) -> bool:
        """Determine if authenticated with pin"""
        return self.api_client.call(url='/plex/pin/authenticated', call_type=APIType.GET)
    
    def plex_token_invalidate(self) -> bool:
        """Invalidates plex token, if error not ocurred, returns True"""
        return self.api_client.call(url='/plex/token/invalidate', call_type=APIType.GET)
    
    def plex_sync(self):
        # 500: Internal Server Error
        """Sync"""
        return self.api_client.call(url='/plex/sync', call_type=APIType.GET)
    
    def plex_sync_all(self):
        # 500: Internal Server Error
        """Sync all"""
        return self.api_client.call(url='/plex/sync/all', call_type=APIType.GET)
    
    def plex_sync_by_id(self, id: int):
        # 500: Internal Server Error
        """Sync by id"""
        return self.api_client.call(url=f'/plex/sync/{id}', call_type=APIType.GET)
    
    #
    # Version
    #
    def version_get(self):
        """Return current version of ShokoServer and several modules"""
        response = self.api_client.call(url='/api/version', call_type=APIType.GET)
        output: List[ComponentVersion] = []
        for component in response:
            output.append(ComponentVersion.Decoder(component))
        return output
    
    #
    # Webui
    #
    def webui_settings_get(self) -> WebUI_Settings:
        """Read json file that is converted into string from .config file of jmmserver"""
        response = self.api_client.call(url='/api/webui/config', call_type=APIType.GET)
        return WebUI_Settings.Decoder(response)
    
    def webui_settings_set(self, settings: WebUI_Settings = WebUI_Settings()):
        # 500: Internal Server Error
        """Save webui settings as json converted into string inside .config file of jmmserver"""
        return self.api_client.call(url='/api/webui/config', call_type=APIType.POST, data=settings.__dict__)
        
    def webui_latest_stable(self) -> ComponentVersion:
        """Check for newest stable version and return object 
    
        {
    
            version: string, 
    
            url: string
    
        }"""
        response = self.api_client.call(url='/api/webui/latest/stable', call_type=APIType.GET)
        return ComponentVersion.Decoder(response)
    
    def webui_latest_unstable(self) -> ComponentVersion:
        """Check for newest unstable version and return object
        
        {
    
            version: string, 
    
            url: string
    
        }"""
        response = self.api_client.call(url='/api/webui/latest/unstable', call_type=APIType.GET)
        return ComponentVersion.Decoder(response)
