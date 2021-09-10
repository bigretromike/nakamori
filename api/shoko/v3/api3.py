# -*- coding: utf-8 -*-

# BASED OF :8111/swagger/index.html?urls.primaryName=3.0
# Asahara

from __future__ import absolute_import
from api.common import APIClient, APIType
from api.shoko.v3.api3models import *
import json

# read test config from file that is not sync with gh
config = json.load(open("config.json"))
address = config['address']
port = config['port']
version = config['version']
apikey = config['apikey']
timeout = config['timeout']

api_client = APIClient(api_address=address, api_port=port, api_version=version, api_key=apikey, timeout=timeout)


# region action api


action_api_url = '/api/v{}/Action/{}'


def replace_apikey_while_runtime(apikey: str = ''):
    api_client.replace_apikey(apikey=apikey)


def _action_api_(command: str = '', call_type: APIType = APIType.GET):
    url = action_api_url.format(api_client.version, command)
    return api_client.call(url=url, call_type=call_type)


def run_import():
    return _action_api_('RunImport')


def sync_hashes():
    return _action_api_('SyncHashes')


def sync_votes():
    return _action_api_('SyncVotes')


def sync_trakt():
    return _action_api_('SyncTrakt')


def remove_missing_files():
    return _action_api_('RemoveMissingFiles/{removeFromMyList}')


def update_all_tvdbinfo():
    return _action_api_('UpdateAllTvDBInfo')


def update_all_images():
    return _action_api_('UpdateAllImages')


def update_all_moviedb_info():
    return _action_api_('UpdateAllMovieDBInfo')


def update_all_trakt_info():
    return _action_api_('UpdateAllTraktInfo')


def validate_all_images():
    return _action_api_('ValidateAllImages')


def avdump_mismatched_files():
    return _action_api_('AVDumpMismatchedFiles')


def download_missing_anidb_anime_data():
    return _action_api_('DownloadMissingAniDBAnimeData')


def regenerate_all_tvdb_episodes_matching():
    return _action_api_('RegenerateAllTvDBEpisodeMatchings')


def sync_mylist():
    return _action_api_('SyncMyList')


def update_all_anidb_info():
    return _action_api_('UpdateAllAniDBInfo')


def update_all_mediainfo():
    return _action_api_('UpdateAllMediaInfo')


def update_series_stats():
    return _action_api_('UpdateSeriesStats')

# endregion

# region auth


auth_api_url = '/api/auth'


def _auth_api_(command: str = '', call_type: APIType = APIType.GET, data: dict = None, auth: bool = True):
    url = auth_api_url if command == '' else auth_api_url + '/' + command
    return api_client.call(url=url, call_type=call_type, data=data, auth=auth)


def login_user(user: str = '', password: str = '', device: str = ''):

    data = {"user": user,
            "pass": password,
            "device": device
            }
    response = _auth_api_(call_type=APIType.POST, data=data, auth=False)
    return AuthUser.from_dict(response)
    # return json.loads(response, object_hook=AuthUser.decoder)


def delete_user_apikey(apikey: str = ''):
    data = {'apikey': apikey}
    return _auth_api_(call_type=APIType.DELETE, data=data, auth=True)


def change_user_password(password: str = ''):
    # string only, no json, no brackets
    data = password
    return _auth_api_(command='ChangePassword', call_type=APIType.POST, data=data)

# endregion

# region dashboard


dashboard_api_url = '/api/v{}/Dashboard/{}'


def _dashboard_api_(command: str = '', call_type: APIType = APIType.GET, data: dict = None):
    url = dashboard_api_url.format(api_client.version, command)
    return api_client.call(url=url, call_type=call_type, data=data)


def get_stats():
    from api3models import Stats
    response = _dashboard_api_(command='Stats')
    return json.loads(response, object_hook=Stats.decoder)


def get_top_tags():
    from api3models import Tags
    response = _dashboard_api_(command='TopTags')
    return json.loads(response, object_hook=Tags.decoder)


def get_top_tags_by_page(page: int):
    from api3models import Tags
    response = _dashboard_api_(command=f'TopTags/{page}')
    return json.loads(response, object_hook=Tags.decoder)


def queue_summary():
    return _dashboard_api_(command='QueueSummary')


def series_summary():
    from api3models import Summary
    response = _dashboard_api_(command='SeriesSummary')
    return json.loads(response, object_hook=Summary.decoder)


# endregion

# region episode

episode_api_url = '/api/v{}/Episode/{}'


def _episode_api_(command: str = '', call_type: APIType = APIType.GET, data: dict = None):
    url = episode_api_url.format(api_client.version, command)
    return api_client.call(url=url, call_type=call_type, data=data)


def episode_by_id(id: int):
    from api3models import Episode
    response = _episode_api_(command=f'{id}')
    return json.loads(response, object_hook=Episode.decoder)


def episode_by_id_anidb_info(id: int):
    from api3models import EpisodeAniDB
    response = _episode_api_(command=f'{id}/AniDB')
    return json.loads(response, object_hook=EpisodeAniDB.decoder)


def episode_by_id_tvdb_info(id: int):
    from api3models import Episode
    response = _episode_api_(command=f'{id}/TvDB')
    return json.loads(response, object_hook=Episode.decoder)


def episode_by_id_watched_state(id: int, watched: bool = True):
    return _episode_api_(command=f'{id}/watched/{watched}', call_type=APIType.POST)

# endregion

# region file


file_api_url = '/api/v{}/File/{}'


def _file_api_(command: str = '', call_type: APIType = APIType.GET, data: dict = None):
    url = file_api_url.format(api_client.version, command)
    return api_client.call(url=url, call_type=call_type, data=data)


def file_by_id(id: int):
    from api3models import File
    response = _file_api_(command=f'{int}')
    return json.loads(response, object_hook=File.decoder)


def remove_file_by_id(id: int, removefolder: bool):
    return _file_api_(command=f'{id}?removeFolder={removefolder}', call_type=APIType.DELETE)


def file_by_id_anidb_info(id: int):
    from api3models import FileAniDB
    response = _file_api_(command=f'{id}/AniDB')
    return json.loads(response, object_hook=FileAniDB.decoder)


def file_by_id_MediaInfo(id: int):
    from api3models import FileMediaInfo
    response = _file_api_(command=f'{id}/MediaInfo')
    return json.loads(response, object_hook=FileMediaInfo.decoder)


def file_api_watched_state(id: int, watched: bool = True):
    return _file_api_(command=f'{id}/watched/{watched}', call_type=APIType.POST)


def file_by_id_scrobble(id: int, watched: bool = True, resumeposition: int = 0):
    return _file_api_(command=f'{id}/Scrobble?watched={watched}&resumePosition={resumeposition}', call_type=APIType.PATCH)


def file_by_id_avdump(id: int, fulloutput: str, ed2k: str):
    data = {'FullOutput': fulloutput, "Ed2k": ed2k}
    return _file_api_(command=f'{id}/avdump', call_type=APIType.POST, data=data)


def file_ends_with_path(path: str):
    from api3models import File
    response = _file_api_(command='PathEndsWith/{}'.format(str(path)))
    return json.loads(response, object_hook=File.decoder)


def file_path_regex(path: str):
    from api3models import File
    response = _file_api_(command='PathRegex/{}'.format(str(path)))
    return json.loads(response, object_hook=File.decoder)


def recent_file(limit: int):
    from api3models import File
    response = _file_api_(command='Recent/{}'.format(int(limit)))
    return json.loads(response, object_hook=File.decoder)


def unrecognized_file():
    from api3models import File
    response = _file_api_(command='Unrecognized')
    return json.loads(response, object_hook=File.decoder)


# endregion

# region filter

filter_api_url = '/api/v{}/Filter/{}'


def _filter_api_(command: str = '', call_type: APIType = APIType.GET, data: dict = None):
    url = filter_api_url.format(api_client.version, command)
    return api_client.call(url=url, call_type=call_type, data=data)


def filter_by_id(id: int):
    from api3models import Filter
    response = _filter_api_(command='{}'.format(int(id)))
    return json.loads(response, object_hook=Filter.decoder)


def remove_filter_by_id(id: int):
    from api3models import Filter
    response = _filter_api_(command='{}'.format(int(id)), call_type=APIType.DELETE)
    return json.loads(response, object_hook=Filter.decoder)


def filter_by_id_filter(id: int):
    from api3models import Filter
    # duplicate of filter_by_id ?
    response = _filter_api_(command='{}/Filter'.format(int(id)))
    return json.loads(response, object_hook=Filter.decoder)


def filter_by_id_conditions(id: int):
    from api3models import Conditions
    response = _filter_api_(command='{}/Conditions'.format(id))
    return json.loads(response, object_hook=Conditions.decoder)


def filter_by_id_sorting(id: int):
    from api3models import Filter
    response = _filter_api_(command='{}/Sorting'.format(id))
    return json.loads(response, object_hook=Filter.decoder)


def filter_preview():
    from api3models import Filter
    response = _filter_api_(command='Preview', call_type=APIType.POST)
    return json.loads(response, object_hook=Filter.decoder)


def filter():
    # duplicate filter_preview?
    from api3models import Filter
    response = _filter_api_(command = '', call_type=APIType.POST)
    return json.loads(response, object_hook=Filter.decoder)

# endregion

# region tree


tree_api_url = '/api/v{}/{}'


def _tree_api_(command: str = '', call_type: APIType = APIType.GET, data: dict = None):
    url = tree_api_url.format(api_client.version, command)
    return api_client.call(url=url, call_type=call_type, data=data)


def tree_filter(includeempty : bool = False, includeinvisible : bool = False):
    from api3models import Filter
    response = _tree_api_(command=f'Filter?includeEmpty={includeempty}&includeInvisible={includeinvisible}')
    return json.loads(response, object_hook=Filter.decoder)  # cls=json.JSONdecoder) #


def tree_group_in_filter_by_id(id: int):
    from api3models import Group
    response = _tree_api_(command=f'Filter/{id}/Group')
    return json.loads(response, object_hook=Group.decoder)


def tree_group_by_id_in_filter_by_id(fid: int, gid: int):
    from api3models import Series
    response = _tree_api_(command=f'Filter/{fid}/Group/{gid}/Series')
    return json.loads(response, object_hook=Series.decoder)


def tree_episode_in_series_by_id(id: int, includemissing: bool = False):
    from api3models import Episode
    response = _tree_api_(command=f'Series/{id}/Episode?includeMissing={includemissing}')
    return json.loads(response, object_hook=Episode.decoder)


# endregion

# region folder

folder_api_url = '/api/v{}/Folder{}'


def _folder_api(command: str = '', call_type: APIType = APIType.GET, data: dict = None):
    url = folder_api_url.format(api_client.version, command)
    return api_client.call(url=url, call_type=call_type, data=data)


def folder_drives():
    from api3models import FolderDrives
    response = _folder_api(command='/drives')
    return json.loads(response, object_hook=FolderDrives.decoder)


def folder(path: str):
    from api3models import Folder
    response = _folder_api(command='?path={}'.format(str(path)))
    return json.loads(response, object_hook=Folder.decoder)


# endregion

# region group

group_api_url = '/api/v{}/Group{}'


def _group_api(command: str = '', call_type: APIType = APIType.GET, data: dict = None):
    url = group_api_url.format(api_client.version, command)
    return api_client.call(url=url, call_type=call_type, data=data)


def group():
    from api3models import Group
    response = _group_api()
    return json.loads(response, object_hook=Group.decoder)


def group_add(data: dict):
    return _group_api(call_type=APIType.POST, data=data)


def group_by_id(id: int):
    from api3models import Group
    response = _group_api(command=f'/{id}')
    return json.loads(response, object_hook=Group.decoder)


def group_by_id_recalculate(id: int):
    return _group_api(command='/{id)}/Recalculate', call_type  = APIType.POST)


def delete_group_by_id(id: int, deleteseries: bool = False, deletefiles: bool = False):
    return _group_api(command=f'/{id}?deleteSeries={deleteseries}&deleteFiles={deletefiles}')


def recreate_all_groups():
    _group_api(command='/RecreateAllGroups')

# endregion

# region image


image_api_url = '/api/v{}/Image/{}'


def _image_api(command: str = '', call_type: APIType = APIType.GET, data: dict = None):
    url = image_api_url.format(api_client.version, command)
    return api_client.call(url=url, call_type=call_type, data=data)


def image(source: str, type: str, value: str):
    response = _image_api(command=f'{source}/{type}/{value}')
    # return binary image
    return response

# endregion

# region import folder


import_folder_api_url = '/api/v{}/ImportFolder{}'


def _import_folder_api(command: str = '', call_type: APIType = APIType.GET, data: dict = None):
    url = import_folder_api_url.format(api_client.version, command)
    return api_client.call(url=url, call_type=call_type, data=data)


def import_folder():
    from api3models import ImportFolder
    response = _import_folder_api()
    return json.loads(response, object_hook=ImportFolder.decoder)


def import_folder_add(data: dict):
    return _import_folder_api(data=data, call_type=APIType.POST)


def import_folder_update(data: dict):
    return _import_folder_api(data=data, call_type=APIType.PUT)


def import_folder_by_id(id: int):
    from api3models import ImportFolder
    # TODO PATCH
    response = _import_folder_api(command=f'/{id}', call_type=APIType.PATCH)
    return json.loads(response, object_hook=ImportFolder.decoder)


def delete_import_folder_by_id(id: int, removerecords: bool = True, updatemylist: bool = True):
    return _import_folder_api(command=f'/{id}?removeRecords={removerecords}&updateMyList={updatemylist}', call_type=APIType.DELETE)


def scan_import_folder_by_id(id:int):
    return _import_folder_api(command=f'/{id}/Scan')


# endregion

# region init

init_api_url = '/api/v{}/Init/{}'


def _init_api(command: str = '', call_type: APIType = APIType.GET, data: dict = None):
    url = init_api_url.format(api_client.version, command)
    return api_client.call(url=url, call_type=call_type, data=data)


def version():
    from api3models import Version
    response = _init_api(command='Version')
    return json.loads(response, object_hook=Version.decoder)


def status():
    from api3models import Status
    response = _init_api(command='status')
    return json.loads(response, object_hook=Status.decoder)


def inuse():
    from api3models import InUse

    response = _init_api(command='inuse')
    return json.loads(response, object_hook=InUse.decoder)


def default_user():
    from api3models import DefaultUser
    response = _init_api(command='defaultuser')
    return json.loads(response, object_hook=DefaultUser.decoder)


def create_default_user(username: str, password: str):
    data = {'Username': username, 'Password': password}
    response = _init_api(command='defaultuser', data=data, call_type=APIType.POST)
    return response


def start_server():
    return _init_api(command='startserver')


def database_test():
    return _init_api(command='database/test')


def database_instance():
    return _init_api(command='database/sqlserverinstance')

# endregion

# region integrity check


integrity_check_api_url = '/api/v{}/IntegrityCheck{}'


def _integrity_check_api(command: str = '', call_type: APIType = APIType.GET, data: dict = None):
    url = integrity_check_api_url.format(api_client.version, command)
    return api_client.call(url=url, call_type=call_type, data=data)


def integrity_check(data: dict):
    return _init_api(call_type=APIType.POST, data=data)


def integrity_check_by_id(id: int):
    return _init_api(command=f'{id}/Start')

# endregion

# region plex webhook


plex_api_url = '/plex{}'


def _plex_api(command: str = '', call_type: APIType = APIType.GET, data: dict = None):
    url = plex_api_url.format(api_client.version, command)
    return api_client.call(url=url, call_type=call_type, data=data)


def plex_magic_that_only_plex_need(data: dict):
    return _plex_api(command='.json', call_type=APIType.POST, data=data)


def plex_magic_that_only_plex_need2(data: dict):
    return _plex_api(call_type=APIType.POST, data=data)


def plex_login_url():
    return _plex_api(command='/loginurl')


def plex_pin_authenticated():
    return _plex_api(command='/pin/authenticated')


def plex_token_invalidate():
    return _plex_api(command='/token/invalidate')


def plex_sync():
    return _plex_api(command='/sync')


def plex_sync_all():
    return _plex_api(command='/sync/all')


def plex_sync_by_id(id: int):
    return _plex_api(command=f'/sync/{id}')


# endregion

# region renamer

# TODO renamer

# endregion

# region reverse tree


reverse_tree_api_url = '/api/v{}/{}'


def _reverse_tree_api(command: str = '', call_type: APIType = APIType.GET, data: dict = None):
    url = reverse_tree_api_url.format(api_client.version, command)
    return api_client.call(url=url, call_type=call_type, data=data)


def group_from_series_by_id(id: int):
    from api3models import Group
    response = _reverse_tree_api(command=f'Series/{id}/Group')
    return json.loads(response, object_hook=Group.decoder)


def series_from_episode_by_id(id: int):
    from api3models import Series
    response = _reverse_tree_api(command=f'Episode/{id}/Series')
    return json.loads(response, object_hook=Series.decoder)


def episode_from_file_by_id(id: int):
    from api3models import Episode
    response = _reverse_tree_api(command=f'File/{id}/Episode')
    return json.loads(response, object_hook=Episode.decoder)

# endregion

# region series


series_api_url = '/api/v{}/Series{}'


def _series_api(command: str = '', call_type: APIType = APIType.GET, data: dict = None):
    url = series_api_url.format(api_client.version, command)
    return api_client.call(url=url, call_type=call_type, data=data)


def series():
    from api3models import Series
    response = _series_api()
    return json.loads(response, object_hook=Series.decoder)


def series_by_id(id: int):
    from api3models import Series
    response = _series_api(command=f'/{id}')
    return json.loads(response, object_hook=Series.decoder)


def series_path_ending_with(path: str):
    from api3models import Series
    response = _series_api(command=f'/PathEndsWith/{path}')
    return json.loads(response, object_hook=Series.decoder)


def series_by_id_anidb_info(id: int):
    from api3models import Series
    response = _series_api(command=f'/{id}/AniDB')
    return json.loads(response, object_hook=Series.decoder)


def series_by_id_tvdb_info(id: int):
    from api3models import Series
    response =_series_api(command=f'/{id}/TvDB')
    return json.loads(response, object_hook=Series.decoder)


def images_from_series_by_id(id: int, includedisabled: bool = True):
    from api3models import Images
    response =_series_api(command=f'/{id}/Images/{includedisabled}')
    return json.loads(response, object_hook=Images.decoder)


def tag_from_series_by_id_and_filter(id: int, filter: int):
    from api3models import Tags
    response = _series_api(command=f'/{id}/Tags/{filter}')
    return json.loads(response, object_hook=Tags.decoder)


def cast_from_series_by_id(id: int):
    from api3models import FullCast
    response = _series_api(command=f'/{id}/Cast')
    return json.loads(response, object_hook=FullCast.decoder)


def move_series_to_group(sid: int, gid: int):
    from api3models import Series
    response = _series_api(command=f'/{sid}/Move/{gid}', call_type=APIType.PATCH)
    return json.loads(response, object_hook=Series.decoder)


def delete_series_by_id(id: int):
    from api3models import Series
    response = _series_api(command=f'/{id}', call_type=APIType.DELETE)
    return json.loads(response, object_hook=Series.decoder)


def search_series(query: str):
    from api3models import Series
    response = _series_api(command=f'/Search/{query}')
    return json.loads(response, object_hook=Series.decoder)


def series_starts_with(query: str):
    from api3models import Series
    response = _series_api(command=f'/StartsWith/{query}')
    return json.loads(response, object_hook=Series.decoder)


# endregion

# region settings


settings_api_url = '/api/v{}/Settings{}'


def _settings_api(command: str = '', call_type: APIType = APIType.GET, data: dict = None):
    url = settings_api_url.format(api_client.version, command)
    return api_client.call(url=url, call_type=call_type, data=data)


def settings_get():
    from api3models import Settings
    response = _settings_api()
    return json.loads(response, object_hook=Settings.decoder)


def settings_set(data: dict = None):
    from api3models import Settings
    response = _settings_api(call_type=APIType.PATCH, data=data)
    return json.loads(response, object_hook=Settings.decoder)


def settings_anidb_test(username: str, password: str):
    data = {'Username': username, 'Password': password}
    return _settings_api(call_type=APIType.POST, data=data)


# endregion

# region user


user_api_url = '/api/v{}/User{}'


def _user_api(command: str = '', call_type: APIType = APIType.GET, data: dict = None):
    url = user_api_url.format(api_client.version, command)
    return api_client.call(url=url, call_type=call_type, data=data)


def user_get():
    from api3models import User
    response = _user_api()
    return json.loads(response, object_hook=User.decoder)


def user_add(data: dict = None):
    from api3models import User
    response = _user_api(call_type=APIType.POST, data=data)
    return json.loads(response, object_hook=User.decoder)


def user_update(data: dict = None):
    from api3models import User
    response = _user_api(call_type=APIType.PUT, data=data)
    return json.loads(response, object_hook=User.decoder)


def user_patch(id: int, data: dict = None):
    from api3models import User
    # TODO MAP THIS
    data = [{"path": "string", "op": "string", "from": "string"}]
    response = _user_api(command=f'/{id}', call_type=APIType.PATCH, data=data)
    return json.loads(response, object_hook=User.decoder)


def user_delete(id: int):
    return _user_api(command='/{}'.format(id), call_type=APIType.DELETE)


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
# #x = delete_group_by_id(id: int. deleteSeries=False, deleteFiles=False)
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
# # x = file_by_id_scrobble(id: int. watched=True, resumePosition=0)
# # print(x)
#
# # TODO not doing this right now
# #x = file_by_id_avdump(id: int. FullOutput, Ed2k)
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
# # x = user_patch(id: int. data='')
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
