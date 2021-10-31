# -*- coding: utf-8 -*-

# BASED OF :8111/swagger/index.html?urls.primaryName=3.0
# Asahara

from __future__ import absolute_import
from api.common import APIClient, APIType
from api.shoko.v3.api3models import *
import json
import os
from typing import List

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
    def __init__(self, address: str = '127.0.0.1', port: int = 8111, version: int = 3, apikey: str = '', timeout: int = 120):
        self.address = address
        self.port = port
        self.version = version
        self.apikey = apikey
        self.timeout = timeout
        self.api_client = APIClient(api_proto='http', api_address=self.address, api_port=self.port, api_version=self.version, api_key=self.apikey, timeout=self.timeout)

    # region action api

        self.action_api_url = '/api/v{}/Action/{}'
        self.auth_api_url = '/api/auth'
        self.dashboard_api_url = '/api/v{}/Dashboard/{}'
        self.episode_api_url = '/api/v{}/Episode/{}'
        self.file_api_url = '/api/v{}/File/{}'
        self.filter_api_url = '/api/v{}/Filter/{}'
        self.tree_api_url = '/api/v{}/{}'
        self.folder_api_url = '/api/v{}/Folder{}'
        self.group_api_url = '/api/v{}/Group{}'
        self.image_api_url = '/api/v{}/Image/{}'
        self.import_folder_api_url = '/api/v{}/ImportFolder{}'
        self.init_api_url = '/api/v{}/Init/{}'
        self.integrity_check_api_url = '/api/v{}/IntegrityCheck{}'
        self.plex_api_url = '/plex{}'
        self.reverse_tree_api_url = '/api/v{}/{}'
        self.series_api_url = '/api/v{}/Series{}'
        self.settings_api_url = '/api/v{}/Settings{}'
        self.user_api_url = '/api/v{}/User{}'

    def replace_apikey_while_runtime(self, apikey: str = ''):
        self.api_client.replace_apikey(apikey=apikey)

    def _action_api_(self, command: str = '', call_type: APIType = APIType.GET):
        url = self.action_api_url.format(self.api_client.version, command)
        return self.api_client.call(url=url, call_type=call_type)

    def run_import(self):
        return self._action_api_('RunImport')

    def sync_hashes(self):
        return self._action_api_('SyncHashes')

    def sync_votes(self):
        return self._action_api_('SyncVotes')

    def sync_trakt(self):
        return self._action_api_('SyncTrakt')

    def remove_missing_files(self):
        return self._action_api_('RemoveMissingFiles/{removeFromMyList}')

    def update_all_tvdbinfo(self):
        return self._action_api_('UpdateAllTvDBInfo')

    def update_all_images(self):
        return self._action_api_('UpdateAllImages')

    def update_all_moviedb_info(self):
        return self._action_api_('UpdateAllMovieDBInfo')

    def update_all_trakt_info(self):
        return self._action_api_('UpdateAllTraktInfo')

    def validate_all_images(self):
        return self._action_api_('ValidateAllImages')

    def avdump_mismatched_files(self):
        return self._action_api_('AVDumpMismatchedFiles')

    def download_missing_anidb_anime_data(self):
        return self._action_api_('DownloadMissingAniDBAnimeData')

    def regenerate_all_tvdb_episodes_matching(self):
        return self._action_api_('RegenerateAllTvDBEpisodeMatchings')

    def sync_mylist(self):
        return self._action_api_('SyncMyList')

    def update_all_anidb_info(self):
        return self._action_api_('UpdateAllAniDBInfo')

    def update_all_mediainfo(self):
        return self._action_api_('UpdateAllMediaInfo')

    def update_series_stats(self):
        return self._action_api_('UpdateSeriesStats')

    # endregion

    # region auth

    def _auth_api_(self, command: str = '', call_type: APIType = APIType.GET, data: dict = None, auth: bool = True):
        url = self.auth_api_url if command == '' else self.auth_api_url + '/' + command
        return self.api_client.call(url=url, call_type=call_type, data=data, auth=auth)

    def login_user(self, user: str = '', password: str = '', device: str = ''):

        data = {"user": user,
                "pass": password,
                "device": device
                }
        response = self._auth_api_(call_type=APIType.POST, data=data, auth=False)
        return AuthUser.from_dict(response)
        # return json.loads(response, object_hook=AuthUser.decoder)

    def delete_user_apikey(self, apikey: str = ''):
        data = {'apikey': apikey}
        return self._auth_api_(call_type=APIType.DELETE, data=data, auth=True)

    def change_user_password(self, password: str = ''):
        # string only, no json, no brackets
        data = password
        return self._auth_api_(command='ChangePassword', call_type=APIType.POST, data=data)

    # endregion

    # region dashboard

    def _dashboard_api_(self, command: str = '', call_type: APIType = APIType.GET, data: dict = None):
        url = self.dashboard_api_url.format(self.api_client.version, command)
        return self.api_client.call(url=url, call_type=call_type, data=data)

    def get_stats(self):
        from api3models import Stats
        response =  self._dashboard_api_(command='Stats')
        return json.loads(response, object_hook=Stats.decoder)

    def get_top_tags(self):
        from api3models import Tags
        response = self._dashboard_api_(command='TopTags')
        return json.loads(response, object_hook=Tags.decoder)

    def get_top_tags_by_page(self, page: int):
        from api3models import Tags
        response = self._dashboard_api_(command=f'TopTags/{page}')
        return json.loads(response, object_hook=Tags.decoder)

    def queue_summary(self):
        return  self._dashboard_api_(command='QueueSummary')

    def series_summary(self):
        from api3models import Summary
        response =  self._dashboard_api_(command='SeriesSummary')
        return json.loads(response, object_hook=Summary.decoder)

    # endregion

    # region episode

    def _episode_api_(self, command: str = '', call_type: APIType = APIType.GET, data: dict = None):
        url = self.episode_api_url.format(self.api_client.version, command)
        return self.api_client.call(url=url, call_type=call_type, data=data)

    def episode_by_id(self, id: int):
        from api3models import Episode
        response = self._episode_api_(command=f'{id}')
        return json.loads(response, object_hook=Episode.decoder)

    def episode_by_id_anidb_info(self, id: int):
        from api3models import EpisodeAniDB
        response = self._episode_api_(command=f'{id}/AniDB')
        return json.loads(response, object_hook=EpisodeAniDB.decoder)

    def episode_by_id_tvdb_info(self, id: int):
        from api3models import Episode
        response = self._episode_api_(command=f'{id}/TvDB')
        return json.loads(response, object_hook=Episode.decoder)

    def episode_by_id_watched_state(self, id: int, watched: bool = True):
        return self._episode_api_(command=f'{id}/watched/{watched}', call_type=APIType.POST)

    # endregion

    # region file

    def _file_api_(self, command: str = '', call_type: APIType = APIType.GET, data: dict = None):
        url = self.file_api_url.format(self.api_client.version, command)
        return self.api_client.call(url=url, call_type=call_type, data=data)

    def file_by_id(self, id: int):
        from api3models import File
        response = self._file_api_(command=f'{id}')
        return json.loads(response, object_hook=File.decoder)

    def remove_file_by_id(self, id: int, removefolder: bool):
        return self._file_api_(command=f'{id}?removeFolder={removefolder}', call_type=APIType.DELETE)

    def file_by_id_anidb_info(self, id: int):
        from api3models import FileAniDB
        response = self._file_api_(command=f'{id}/AniDB')
        return json.loads(response, object_hook=FileAniDB.decoder)

    def file_by_id_MediaInfo(self, id: int):
        from api3models import FileMediaInfo
        response = self._file_api_(command=f'{id}/MediaInfo')
        return json.loads(response, object_hook=FileMediaInfo.decoder)

    def file_api_watched_state(self, id: int, watched: bool = True):
        return self._file_api_(command=f'{id}/watched/{watched}', call_type=APIType.POST)

    def file_by_id_scrobble(self, id: int, watched: bool = True, resumeposition: int = 0):
        return self._file_api_(command=f'{id}/Scrobble?watched={watched}&resumePosition={resumeposition}', call_type=APIType.PATCH)

    def file_by_id_avdump(self, id: int, fulloutput: str, ed2k: str):
        data = {'FullOutput': fulloutput, "Ed2k": ed2k}
        return self._file_api_(command=f'{id}/avdump', call_type=APIType.POST, data=data)

    def file_ends_with_path(self, path: str):
        from api3models import File
        response = self._file_api_(command='PathEndsWith/{}'.format(str(path)))
        return json.loads(response, object_hook=File.decoder)

    def file_path_regex(self, path: str):
        from api3models import File
        response = self._file_api_(command='PathRegex/{}'.format(str(path)))
        return json.loads(response, object_hook=File.decoder)

    def recent_file(self, limit: int):
        from api3models import File
        response = self._file_api_(command='Recent/{}'.format(int(limit)))
        return json.loads(response, object_hook=File.decoder)

    def unrecognized_file(self):
        from api3models import File
        response = self._file_api_(command='Unrecognized')
        return json.loads(response, object_hook=File.decoder)

    # endregion

    # region filter

    def _filter_api_(self, command: str = '', call_type: APIType = APIType.GET, data: dict = None):
        url = self.filter_api_url.format(self.api_client.version, command)
        return self.api_client.call(url=url, call_type=call_type, data=data)

    def filter_by_id(self, id: int):
        from api3models import Filter
        response = self._filter_api_(command='{}'.format(int(id)))
        return json.loads(response, object_hook=Filter.decoder)

    def remove_filter_by_id(self, id: int):
        from api3models import Filter
        response = self._filter_api_(command='{}'.format(int(id)), call_type=APIType.DELETE)
        return json.loads(response, object_hook=Filter.decoder)

    def filter_by_id_filter(self, id: int):
        from api3models import Filter
        # duplicate of filter_by_id ?
        response = self._filter_api_(command='{}/Filter'.format(int(id)))
        return json.loads(response, object_hook=Filter.decoder)

    def filter_by_id_conditions(self, id: int):
        from api3models import Conditions
        response = self._filter_api_(command='{}/Conditions'.format(id))
        return json.loads(response, object_hook=Conditions.decoder)

    def filter_by_id_sorting(self, id: int):
        from api3models import Filter
        response = self._filter_api_(command='{}/Sorting'.format(id))
        return json.loads(response, object_hook=Filter.decoder)

    def filter_preview(self):
        from api3models import Filter
        response = self._filter_api_(command='Preview', call_type=APIType.POST)
        return json.loads(response, object_hook=Filter.decoder)

    def filter(self):
        # duplicate filter_preview?
        from api3models import Filter
        response = self._filter_api_(command='', call_type=APIType.POST)
        return json.loads(response, object_hook=Filter.decoder)

    # endregion

    # region tree

    def _tree_api_(self, command: str = '', call_type: APIType = APIType.GET, data: dict = None):
        url = self.tree_api_url.format(self.api_client.version, command)
        return self.api_client.call(url=url, call_type=call_type, data=data)

    def tree_filter(self, includeempty : bool = False, includeinvisible : bool = False)-> List[Filter]:
        from api.shoko.v3.api3models import Filter
        response = self._tree_api_(command=f'Filter?includeEmpty={includeempty}&includeInvisible={includeinvisible}')
        filter_list = []
        for f in response:
            filter_list.append(json.loads(json.dumps(f), object_hook=Filter.decoder))
        return filter_list

    def tree_group_in_filter_by_id(self, id: int):
        from api3models import Group
        response = self._tree_api_(command=f'Filter/{id}/Group')
        return json.loads(response, object_hook=Group.decoder)

    def tree_group_by_id_in_filter_by_id(self, fid: int, gid: int):
        from api3models import Series
        response = self._tree_api_(command=f'Filter/{fid}/Group/{gid}/Series')
        return json.loads(response, object_hook=Series.decoder)

    def tree_episode_in_series_by_id(self, id: int, includemissing: bool = False):
        from api3models import Episode
        response = self._tree_api_(command=f'Series/{id}/Episode?includeMissing={includemissing}')
        return json.loads(response, object_hook=Episode.decoder)

    # endregion

    # region folder

    def _folder_api(self, command: str = '', call_type: APIType = APIType.GET, data: dict = None):
        url = self.folder_api_url.format(self.api_client.version, command)
        return  self.api_client.call(url=url, call_type=call_type, data=data)

    def folder_drives(self):
        from api3models import FolderDrives
        response = self._folder_api(command='/drives')
        return json.loads(response, object_hook=FolderDrives.decoder)

    def folder(self, path: str):
        from api3models import Folder
        response = self._folder_api(command='?path={}'.format(str(path)))
        return json.loads(response, object_hook=Folder.decoder)

    # endregion

    # region group

    def _group_api(self, command: str = '', call_type: APIType = APIType.GET, data: dict = None):
        url = self.group_api_url.format(self.api_client.version, command)
        return self.api_client.call(url=url, call_type=call_type, data=data)

    def group(self):
        from api3models import Group
        response = self._group_api()
        return json.loads(response, object_hook=Group.decoder)

    def group_add(self, data: dict):
        return self._group_api(call_type=APIType.POST, data=data)

    def group_by_id(self, id: int):
        from api3models import Group
        response = self._group_api(command=f'/{id}')
        return json.loads(response, object_hook=Group.decoder)

    def group_by_id_recalculate(self, id: int):
        return self._group_api(command='/{id)}/Recalculate', call_type  = APIType.POST)

    def delete_group_by_id(self, id: int, deleteseries: bool = False, deletefiles: bool = False):
        return self._group_api(command=f'/{id}?deleteSeries={deleteseries}&deleteFiles={deletefiles}')

    def recreate_all_groups(self):
        return self._group_api(command='/RecreateAllGroups')

    # endregion

    # region image

    def _image_api(self, command: str = '', call_type: APIType = APIType.GET, data: dict = None):
        url = self.image_api_url.format(self.api_client.version, command)
        return self.api_client.call(url=url, call_type=call_type, data=data)

    def image(self, source: str, type: str, value: str):
        response = self._image_api(command=f'{source}/{type}/{value}')
        # return binary image
        return response

    # endregion

    # region import folder

    def _import_folder_api(self, command: str = '', call_type: APIType = APIType.GET, data: dict = None):
        url = self.import_folder_api_url.format(self.api_client.version, command)
        return self.api_client.call(url=url, call_type=call_type, data=data)

    def import_folder(self):
        from api3models import ImportFolder
        response = self._import_folder_api()
        return json.loads(response, object_hook=ImportFolder.decoder)

    def import_folder_add(self, data: dict):
        return self._import_folder_api(data=data, call_type=APIType.POST)

    def import_folder_update(self, data: dict):
        return self._import_folder_api(data=data, call_type=APIType.PUT)

    def import_folder_by_id(self, id: int):
        from api3models import ImportFolder
        # TODO PATCH
        response = self._import_folder_api(command=f'/{id}', call_type=APIType.PATCH)
        return json.loads(response, object_hook=ImportFolder.decoder)

    def delete_import_folder_by_id(self, id: int, removerecords: bool = True, updatemylist: bool = True):
        return self._import_folder_api(command=f'/{id}?removeRecords={removerecords}&updateMyList={updatemylist}', call_type=APIType.DELETE)

    def scan_import_folder_by_id(self, id:int):
        return self._import_folder_api(command=f'/{id}/Scan')

    # endregion

    # region init

    def _init_api(self, command: str = '', call_type: APIType = APIType.GET, data: dict = None):
        url = self.init_api_url.format(self.api_client.version, command)
        return self.api_client.call(url=url, call_type=call_type, data=data)

    def version(self):
        from api3models import Version
        response = self._init_api(command='Version')
        return json.loads(response, object_hook=Version.decoder)

    def status(self):
        from api3models import Status
        response = self._init_api(command='status')
        return json.loads(response, object_hook=Status.decoder)

    def inuse(self):
        from api3models import InUse
        response = self._init_api(command='inuse')
        return json.loads(response, object_hook=InUse.decoder)

    def default_user(self):
        from api3models import DefaultUser
        response = self._init_api(command='defaultuser')
        return json.loads(response, object_hook=DefaultUser.decoder)

    def create_default_user(self, username: str, password: str):
        data = {'Username': username, 'Password': password}
        response = self._init_api(command='defaultuser', data=data, call_type=APIType.POST)
        return response

    def start_server(self):
        return self._init_api(command='startserver')

    def database_test(self):
        return self._init_api(command='database/test')

    def database_instance(self):
        return self._init_api(command='database/sqlserverinstance')

    # endregion

    # region integrity check

    def _integrity_check_api(self, command: str = '', call_type: APIType = APIType.GET, data: dict = None):
        url = self.integrity_check_api_url.format(self.api_client.version, command)
        return self.api_client.call(url=url, call_type=call_type, data=data)

    def integrity_check(self, data: dict):
        return self._init_api(call_type=APIType.POST, data=data)

    def integrity_check_by_id(self, id: int):
        return self._init_api(command=f'{id}/Start')

    # endregion

    # region plex webhook

    def _plex_api(self, command: str = '', call_type: APIType = APIType.GET, data: dict = None):
        url = self.plex_api_url.format(self.api_client.version, command)
        return self.api_client.call(url=url, call_type=call_type, data=data)

    def plex_magic_that_only_plex_need(self, data: dict):
        return self._plex_api(command='.json', call_type=APIType.POST, data=data)

    def plex_magic_that_only_plex_need2(self, data: dict):
        return self._plex_api(call_type=APIType.POST, data=data)

    def plex_login_url(self):
        return self._plex_api(command='/loginurl')

    def plex_pin_authenticated(self):
        return self._plex_api(command='/pin/authenticated')

    def plex_token_invalidate(self):
        return self._plex_api(command='/token/invalidate')

    def plex_sync(self):
        return self._plex_api(command='/sync')

    def plex_sync_all(self):
        return self._plex_api(command='/sync/all')

    def plex_sync_by_id(self, id: int):
        return self._plex_api(command=f'/sync/{id}')

    # endregion

    # region renamer

    # TODO renamer

    # endregion

    # region reverse tree

    def _reverse_tree_api(self, command: str = '', call_type: APIType = APIType.GET, data: dict = None):
        url = self.reverse_tree_api_url.format(self.api_client.version, command)
        return self.api_client.call(url=url, call_type=call_type, data=data)

    def group_from_series_by_id(self, id: int):
        from api3models import Group
        response = self._reverse_tree_api(command=f'Series/{id}/Group')
        return json.loads(response, object_hook=Group.decoder)

    def series_from_episode_by_id(self, id: int):
        from api3models import Series
        response = self._reverse_tree_api(command=f'Episode/{id}/Series')
        return json.loads(response, object_hook=Series.decoder)

    def episode_from_file_by_id(self, id: int):
        from api3models import Episode
        response = self._reverse_tree_api(command=f'File/{id}/Episode')
        return json.loads(response, object_hook=Episode.decoder)

    # endregion

    # region series

    def _series_api(self, command: str = '', call_type: APIType = APIType.GET, data: dict = None):
        url = self.series_api_url.format(self.api_client.version, command)
        return self.api_client.call(url=url, call_type=call_type, data=data)

    def series(self):
        from api3models import Series
        response = self._series_api()
        return json.loads(response, object_hook=Series.decoder)

    def series_by_id(self, id: int):
        from api3models import Series
        response = self._series_api(command=f'/{id}')
        return json.loads(response, object_hook=Series.decoder)

    def series_path_ending_with(self, path: str):
        from api3models import Series
        response = self._series_api(command=f'/PathEndsWith/{path}')
        return json.loads(response, object_hook=Series.decoder)

    def series_by_id_anidb_info(self, id: int):
        from api3models import Series
        response = self._series_api(command=f'/{id}/AniDB')
        return json.loads(response, object_hook=Series.decoder)

    def series_by_id_tvdb_info(self, id: int):
        from api3models import Series
        response = self._series_api(command=f'/{id}/TvDB')
        return json.loads(response, object_hook=Series.decoder)

    def images_from_series_by_id(self, id: int, includedisabled: bool = True):
        from api3models import Images
        response = self._series_api(command=f'/{id}/Images/{includedisabled}')
        return json.loads(response, object_hook=Images.decoder)

    def tag_from_series_by_id_and_filter(self, id: int, filter: int):
        from api3models import Tags
        response = self._series_api(command=f'/{id}/Tags/{filter}')
        return json.loads(response, object_hook=Tags.decoder)

    def cast_from_series_by_id(self, id: int):
        from api3models import FullCast
        response = self._series_api(command=f'/{id}/Cast')
        return json.loads(response, object_hook=FullCast.decoder)

    def move_series_to_group(self, sid: int, gid: int):
        from api3models import Series
        response = self._series_api(command=f'/{sid}/Move/{gid}', call_type=APIType.PATCH)
        return json.loads(response, object_hook=Series.decoder)

    def delete_series_by_id(self, id: int):
        from api3models import Series
        response = self._series_api(command=f'/{id}', call_type=APIType.DELETE)
        return json.loads(response, object_hook=Series.decoder)

    def search_series(self, query: str):
        from api3models import Series
        response = self._series_api(command=f'/Search/{query}')
        return json.loads(response, object_hook=Series.decoder)

    def series_starts_with(self, query: str):
        from api3models import Series
        response = self._series_api(command=f'/StartsWith/{query}')
        return json.loads(response, object_hook=Series.decoder)

    # endregion

    # region settings

    def _settings_api(self, command: str = '', call_type: APIType = APIType.GET, data: dict = None):
        url = self.settings_api_url.format(self.api_client.version, command)
        return self.api_client.call(url=url, call_type=call_type, data=data)

    def settings_get(self):
        from api3models import Settings
        response = self._settings_api()
        return json.loads(response, object_hook=Settings.decoder)

    def settings_set(self, data: dict = None):
        from api3models import Settings
        response = self._settings_api(call_type=APIType.PATCH, data=data)
        return json.loads(response, object_hook=Settings.decoder)

    def settings_anidb_test(self, username: str, password: str):
        data = {'Username': username, 'Password': password}
        return self._settings_api(call_type=APIType.POST, data=data)

    # endregion

    # region user

    def _user_api(self, command: str = '', call_type: APIType = APIType.GET, data: dict = None):
        url = self.user_api_url.format(self.api_client.version, command)
        return self.api_client.call(url=url, call_type=call_type, data=data)

    def user_get(self):
        from api3models import User
        response = self._user_api()
        return json.loads(response, object_hook=User.decoder)

    def user_add(self, data: dict = None):
        from api3models import User
        response = self._user_api(call_type=APIType.POST, data=data)
        return json.loads(response, object_hook=User.decoder)

    def user_update(self, data: dict = None):
        from api3models import User
        response = self._user_api(call_type=APIType.PUT, data=data)
        return json.loads(response, object_hook=User.decoder)

    def user_patch(self, id: int, data: dict = None):
        from api3models import User
        # TODO MAP THIS
        data = [{"path": "string", "op": "string", "from": "string"}]
        response = self._user_api(command=f'/{id}', call_type=APIType.PATCH, data=data)
        return json.loads(response, object_hook=User.decoder)

    def user_delete(self, id: int):
        return self._user_api(command='/{}'.format(id), call_type=APIType.DELETE)

    # endregion


    #
    # # flow
    # # 0.check if online/busy
    # # 1.login (login='default' password='')
    # api_key = login_user('default', '', 'from-inside-ide').apikey
    # x = api_key
    # print(x)
    # # 2.save apikey ( apikey is user+device ) / or store it in api_key for debugging
    # # 3. list all available filters
    # x = tree_filter()
    # print(x)
    # # 4. list all availables groups in filter of id:8  /8 - newly added series
    # x = tree_group_in_filter_by_id(8)
    # print(x)
    # # 5. list all availables series in group of id: 3981 (mine is this)
    # x = tree_group_by_id_in_filter_by_id(8, 3981)
    # print(x)
    # # 6. list all episodes for give series :
    # x = tree_episode_in_series_by_id(22, True)
    # print(x)
    #
    # # region TEST
    # # region SERIES
    # x = series()
    # print(x)
    #
    # x = series_by_id(22)
    # print(x)
    #
    # x = series_path_ending_with('naruto')
    # print(x)
    #
    # x = series_by_id_anidb_info(22)
    # print(x)
    #
    # # TODO got empty, sure ?
    # x = series_by_id_tvdb_info(22)
    # print(x)
    #
    # x = images_from_series_by_id(22, includeDisabled=True)
    # print(x)
    #
    # x = tag_from_series_by_id_and_filter(22, 8)
    # print(x)
    #
    # x = cast_from_series_by_id(22)
    # print(x)
    #
    # # TODO not doing this right now
    # # x = move_series_to_group(sid: int. gid)
    #
    # # TODO not doing this right now
    # # x = delete_series_by_id(id)
    #
    # x = search_series('naruto')
    # print(x)
    #
    # x = series_starts_with('ano')
    # print(x)
    #
    # # endregion
    #
    # # region REVERSE_TREE
    #
    #
    # x = group_from_series_by_id(20)
    # print(x)
    #
    # x = series_from_episode_by_id(20)
    # print(x)
    #
    # x = episode_from_file_by_id(20)
    # print(x)
    #
    # # endregion
    #
    # # region IMAGE
    #
    # x = image('AniDB', 'Poster', 1)
    # print(x)
    #
    # # endregion
    #
    # # region GROUP
    #
    # # get ALL GROUPS TIME HEAVY !!!!!!
    # #x = group()
    # #print(x)
    #
    # # TODO not doing this now
    # #x = group_add(data)
    # #print(x)
    #
    # x = group_by_id(1)
    # print(x)
    #
    # # time consuming even for one id
    # # x = group_by_id_recalculate(1)
    # # b''
    # # print(x)
    #
    # # TODO not doing this now
    # #x = delete_group_by_id(self, id: int. deleteSeries=False, deleteFiles=False)
    # #print(x)
    #
    # # TODO not doing this now
    # #x = recreate_all_groups()
    # #print(x)
    # # endregion
    #
    # # region EPISODE
    # x = episode_by_id(1)
    # print(x)
    #
    # x = episode_by_id_anidb_info(1)
    # print(x)
    #
    # # TODO nothing i get nothing ? is this broken or i'm missing something ?
    # x = episode_by_id_tvdb_info(1)
    # print(x)
    #
    # # OK
    # # x = episode_by_id_watched_state(1, watched=True)
    # # b''
    # # print(x)
    #
    # # endregion
    #
    # # region FILTER
    # x = filter_by_id(6)
    # print(x)
    #
    # # TODO not doing this now
    # # x = remove_filter_by_id(id)
    # # print(x)
    #
    # # TODO HTTP Error 400: Bad Request broken or im missing something
    # # x = filter_by_id_filter(1)
    # # print(x)
    #
    # x = filter_by_id_conditions(6)
    # print(x)
    #
    # # TODO [] am i'm missing something ?
    # x = filter_by_id_sorting(6)
    # print(x)
    #
    # # TODO HTTP Error 400: Bad Request im missing data to post ? looks like Filter object, Testing Filter before add ?
    # # x = filter_preview()
    # # print(x)
    #
    # # TODO HTTP Error 400: Bad Request im missing data to post ? looks like Filter object, Adding Filter ?
    # # x = filter()
    # # print(x)
    #
    # # endregion
    #
    # # region File
    #
    # #  400: Bad Request  === missing row - someone had bad day
    # #  TAKE SOME TIME, WORKING
    # # x = file_by_id(3)
    # # print(x)
    #
    # # TODO not doing this
    # #x = remove_file_by_id(1, removeFolder=False)
    # #print(x)
    #
    # # HTTP Error 400: Bad Request ?? == missing row
    # x = file_by_id_anidb_info(3)
    # print(x)
    #
    # # TODO is it broken ? or its me ?
    # # x = file_by_id_MediaInfo(3)
    # # b''
    # # print(x)
    #
    # # working results in b'' but trigger
    # #x = file_api_watched_state(3, watched=True)
    # # b''
    # # print(x)
    #
    # # TODO not important right now
    # # x = file_by_id_scrobble(self, id: int. watched=True, resumePosition=0)
    # # print(x)
    #
    # # TODO not doing this right now
    # #x = file_by_id_avdump(self, id: int. FullOutput, Ed2k)
    # #print(x)
    #
    # # TODO APIv3 broken, throw 500
    # # x = file_ends_with_path('a')
    # # print(x)
    #
    # # OK, BUT SLOWDOWN DEBUG
    # # x = file_path_regex('naruto')
    # # print(x)
    #
    # # ok, but slowdown
    # # x = recent_file(10)
    # # print(x)
    #
    # # ok, but slowdown
    # # x = unrecognized_file()
    # # print(x)
    #
    # # endregion
    #
    # # region Folder
    #
    # x = folder_drives()
    # print(x)
    #
    # x = folder('c:')
    # print(x)
    #
    # # endregion
    #
    # # region ImportFolder
    #
    # x = import_folder()
    # print(x)
    #
    # # TODO not right now
    # # x = import_folder_add(data)
    # # print(x)
    #
    # # TODO not right now
    # # x = import_folder_update(data)
    # # print(x)
    #
    # # TODO this one need patch and body
    # # x = import_folder_by_id(4)
    # # print(x)
    #
    # # TODO not right now
    # # x = delete_import_folder_by_id(2, removeRecords=True, updateMyList=True)
    # # print(x)
    #
    # # b'' ok
    # # x = scan_import_folder_by_id(4)
    # # print(x)
    #
    # # endregion
    #
    # # region Init
    #
    # x = version()
    # print(x)
    #
    # x = status()
    # print(x)
    #
    # x = inuse()
    # print(x)
    #
    # # TODO HTTP Error 403: Forbidden (only in firstrun ?)
    # # x = default_user()
    # # print(x)
    #
    # # TODO not needed now
    # # x = create_default_user(username, password)
    # # print(x)
    #
    # # TODO HTTP Error 400: Bad Request
    # # TODO NOT NEEDED NOW
    # # x = start_server()
    # # print(x)
    #
    # # TODO HTTP Error 403: Forbidden (only in firstrun ?)
    # # x = database_test()
    # # print(x)
    #
    # # TODO HTTP Error 403: Forbidden (only in firstrun ?)
    # # x = database_instance()
    # # print(x)
    #
    # # endregion
    #
    # # region Auth
    #
    # x = login_user(user='default', password='', device='something')
    # print(x.apikey)
    #
    # # TODO HTTP Error 400: Bad Request
    # # x = delete_user_apikey(apikey=x.apikey)
    # # print(x)
    #
    # # TODO HTTP Error 500: Internal Server Error
    # # x = change_user_password('password')
    # # print(x)
    #
    # # endregion
    #
    # # region Action
    #
    # # ok
    # # x = run_import()
    # # print(x)
    #
    # # TODO HTTP Error 400: Bad Request
    # # x = sync_hashes()
    # # print(x)
    #
    # # NO LOG ? IS THIS EVEN WORKING ?
    # # x = sync_votes()
    # # print(x)
    #
    # # TODO HTTP Error 400: Bad Request
    # # x = sync_trakt()
    # # print(x)
    #
    # # x = remove_missing_files()
    # # print(x)
    #
    # # x = update_all_tvdbinfo()
    # # print(x)
    #
    # # ok - log but with big delay
    # # x = update_all_images()
    # # print(x)
    #
    # # ok - log -ok
    # # x = update_all_moviedb_info()
    # # print(x)
    #
    # # HTTP Error 400: Bad Request (track issue??)
    # # x = update_all_trakt_info()
    # # print(x)
    #
    # # region TEST LATER
    # # TODO check this on small database because it could be ban releated and time consumig
    # # x = validate_all_images()
    # # print(x)
    #
    # # x = avdump_mismatched_files()
    # # print(x)
    #
    # # x = download_missing_anidb_anime_data()
    # # print(x)
    #
    # # x = regenerate_all_tvdb_episodes_matching()
    # # print(x)
    #
    # # x = sync_mylist()
    # # print(x)
    #
    # # x = update_all_anidb_info()
    # # print(x)
    #
    # # x = update_all_mediainfo()
    # # print(x)
    #
    # # x = update_series_stats()
    # # print(x)
    # # endregion
    # # endregion
    #
    # # region IntegrityCheck
    #
    # # TODO not right now
    # # data = {'ScanID': 0, 'CreationTIme': "2021-08-29T08:32:44.284Z", "ImportFolders": "string", "Status": 0}
    # # x = integrity_check(data)
    # # print(x)
    #
    # # TODO 404, because you need to add SCAN ?queue? and ten start it
    # # x = integrity_check_by_id(0)
    # # print(x)
    #
    # # endregion
    #
    # # region Users
    #
    #
    # x = user_get()
    # print(x)
    #
    # # TODO MAYBE LATER
    # # x = user_add(data='')
    # # print(x)
    #
    # # TODO MAYBE LATER
    # # x = user_update(data='')
    # # print(x)
    #
    # # TODO MAYBE LATER
    # # x = user_patch(self, id: int. data='')
    # # print(x)
    #
    # # TODO NOT DOING THIS RIGHT NOW
    # # x = user_delete(id)
    # # print(x)
    #
    # # endregion
    #
    # # region Settings
    #
    # x = settings_get()
    # print(x)
    #
    # # TODO we not doing this right now
    # #x = settings_set(data):
    # #print(x)
    #
    # # TODO HTTP Error 405: Method Not Allowed
    # # bruteForce Anidb and get ban
    # # x = settings_anidb_test('username', 'password')
    # # print(x)
    #
    # # endregion
    #
    # # region Dashboard
    #
    # x = get_stats()
    # print(x)
    #
    # x = get_top_tags()
    # print(x)
    #
    # x = get_top_tags_by_page(1)
    # print(x)
    #
    # x = queue_summary()
    # print(x)
    #
    # x = series_summary()
    # print(x)
    #
    # # endregion
    #
    # # region PLEX
    #
    # # TODO no way to test, why would we need it ?:-) is this a time-machine property ? someone doing exclusive shit ?
    # # endregion
    #
    # # endregion
