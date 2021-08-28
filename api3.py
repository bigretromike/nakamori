# -*- coding: utf-8 -*-

# BASED OF :8111/swagger/index.html?urls.primaryName=3.0
# Asahara

import gzip
import json
from enum import Enum
from io import BytesIO
from urllib.request import Request, urlopen


class Api(Enum):
    GET = 1
    POST = 2
    DELETE = 3
    PATCH = 4
    PUT = 5


api_version = 3
api_key = ''


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


def _api_call_(url, call_type=Api.GET, data={}, auth=True):
    url = 'http://10.1.1.100:8111' + url
    print('{}'.format(url))
    x = ''

    headers = {
        'Accept': '*/*',
        'Content-Type': 'application/json'
    }
    if auth:
        headers['apikey'] = api_key

    if '127.0.0.1' not in url and 'localhost' not in url:
        headers['Accept-Encoding'] = 'gzip'
    if '/Stream/' in url:
        headers['api-version'] = '1.0'

    if call_type == Api.GET:
        print('get {}'.format(url))
        req = Request(url, headers=headers)
    elif call_type == Api.POST:
        print('post {} - {}'.format(url, data))
        data = json.dumps(data).encode('utf-8')
        req = Request(url, data=data, headers=headers)
    elif call_type == Api.DELETE:
        print('delete {}'.format(url))
        data = json.dumps(data).encode('utf-8')
        req = Request(url, data=data, headers=headers)
    elif call_type == Api.PATCH:
        print('patch {}'.format(url))
        data = json.dumps(data).encode('utf-8')
        req = Request(url, data=data, headers=headers)
    elif call_type == Api.PUT:
        print('put {}'.format(url))
        data = json.dumps(data).encode('utf-8')
        req = Request(url, data=data, headers=headers)
    else:
        print('??? {}'.format(url))

    timeout = 120

    response = urlopen(req, timeout=int(timeout))

    if response.info().get('Content-Encoding') == 'gzip':
        try:
            buf = BytesIO(response.read())
            f = gzip.GzipFile(fileobj=buf)
            data = f.read()
        except Exception as e:
            print('Failed to decompress.{}'.format(e))
    else:
        data = response.read()
    response.close()

    return data

# region action api
action_api_url = '/api/v{}/Action/{}'


def _action_api_(command='', call_type=Api.GET):
    url = action_api_url.format(api_version, command)
    _api_call_(url, call_type)


def run_import():
    _action_api_('RunImport')


def sync_hashes():
    _action_api_('SyncHashes')


def sync_votes():
    _action_api_('SyncVotes')


def sync_trakt():
    _action_api_('SyncTrakt')


def remove_missing_files():
    _action_api_('RemoveMissingFiles/{removeFromMyList}')


def update_all_tvdbinfo():
    _action_api_('UpdateAllTvDBInfo')


def update_all_images():
    _action_api_('UpdateAllImages')


def update_all_moviedb_info():
    _action_api_('UpdateAllMovieDBInfo')


def update_all_trakt_info():
    _action_api_('UpdateAllTraktInfo')


def validate_all_images():
    _action_api_('ValidateAllImages')


def avdump_mismatched_files():
    _action_api_('AVDumpMismatchedFiles')


def download_missing_anidb_anime_data():
    _action_api_('DownloadMissingAniDBAnimeData')


def regenerate_all_tvdb_episodes_matching():
    _action_api_('RegenerateAllTvDBEpisodeMatchings')


def sync_mylist():
    _action_api_('SyncMyList')


def update_all_anidb_info():
    _action_api_('UpdateAllAniDBInfo')


def update_all_mediainfo():
    _action_api_('UpdateAllMediaInfo')


def update_series_stats():
    _action_api_('UpdateSeriesStats')

# endregion

# region auth


auth_api_url = '/api/auth'


def _auth_api_(command='', call_type=Api.GET, data={}):
    url = auth_api_url if command == '' else auth_api_url + '/' + command
    return _api_call_(url, call_type, data=data, auth=False)


def login_user(user='', password='', device=''):
    from models import AuthUser
    data = {"user": user,
            "pass": password,
            "device": device
            }
    response = _auth_api_(call_type=Api.POST, data=data)
    return json.loads(response, object_hook=AuthUser.Decoder)


def delete_user_apikey(apikey=''):
    data = {'apikey': apikey}
    response = _auth_api_(call_type=Api.DELETE, data=data)


def change_user_password(password):
    data = password
    response = _auth_api_(command='ChangePassword', call_type=Api.POST, data=data)

# endregion

# region dashboard


dashboard_api_url = '/api/v{}/Dashboard/{}'


def _dashboard_api_(command='', call_type=Api.GET, data={}):
    url = dashboard_api_url.format(api_version, command)
    _api_call_(url=url, call_type=call_type, data=data)


def get_stats():
    _dashboard_api_(command='Stats')


def get_top_tags():
    _dashboard_api_(command='TopTags')


def get_top_tags_by_page(page):
    _dashboard_api_(command='TopTags/{}'.format(int(page)))


def queue_summary():
    _dashboard_api_(command='QueueSummary')


def series_summary():
    _dashboard_api_(command='SeriesSummary')


# endregion

# region episode

episode_api_url = 'api/v{}/Episode/'


def _episode_api_(command='', call_type=Api.GET, data={}):
    url = episode_api_url.format(api_version, command)
    _api_call_(url=url, call_type=call_type, data=data)


def episode_by_id(id):
    _episode_api_(command='{}'.format(int(id)))


def episode_by_id_anidb_info(id):
    _episode_api_(command='{}/AniDB'.format(int(id)))


def episode_by_id_tvdb_info(id):
    _episode_api_(command='{}/TvDB'.format(int(id)))


def episode_by_id_watched_state(id, watched=True):
    _episode_api_(command='{}/watched/{}'.format(int(id), int(watched)), call_type=Api.POST)

# endregion

# region file


file_api_url = '/api/v{}/File/{}'


def _file_api_(command='', call_type=Api.GET, data={}):
    url = file_api_url.format(api_version, command)
    _api_call_(url=url, call_type=call_type, data=data)


def file_by_id(id):
    _file_api_(command='{}'.format(int(id)))


def remove_file_by_id(id, removeFolder):
    _file_api_(command='{}?removeFolder={}'.format(int(id), bool(removeFolder)), call_type=Api.DELETE)


def file_by_id_anidb_info(id):
    _file_api_(command='{}/AniDB'.format(int(id)))


def file_by_id_MediaInfo(id):
    _file_api_(command='{}/MediaInfo'.format(int(id)))


def file_api_watched_state(id, watched=True):
    _file_api_(command='{}/watched/{}'.format(int(id), int(watched)), call_type=Api.POST)


def file_by_id_scrobble(id, watched=True, resumePosition=0):
    _file_api_(command='{}/Scrobble?watched={}&resumePosition={}'.format(int(id), bool(watched), int(resumePosition)), call_type=Api.PATCH)


def file_by_id_avdump(id, FullOutput, Ed2k):
    data = {'FullOutput': FullOutput, "Ed2k": Ed2k}
    _file_api_(command='{}/avdump'.format(int(id)), call_type=Api.POST, data=data)


def file_ends_with_path(path):
    _file_api_(command='PathEndsWith/{}'.format(str(path)))


def file_path_regex(path):
    _file_api_(command='PathRegex/{}'.format(str(path)))


def recent_file(limit):
    _file_api_(command='Recent/{}'.format(int(limit)))


def unrecognized_file():
    _file_api_(command='Unrecognized')


# endregion

# region filter

filter_api_url = '/api/v{}/Filter/'


def _filter_api_(command='', call_type=Api.GET, data={}):
    url = filter_api_url.format(api_version, command)
    _api_call_(url=url, call_type=call_type, data=data)


def filter_by_id(id):
    _filter_api_(command='{}'.format(int(id)))


def remove_filter_by_id(id):
    _filter_api_(command='{}'.format(int(id)), call_type=Api.DELETE)


def filter_by_id_filter(id):
    # duplicate of filter_by_id ?
    _filter_api_(command='{}/Filter'.format(int(id)))


def filter_by_id_conditions(id):
    _filter_api_(command='{}/Conditions'.format(id))


def filter_by_id_sorting(id):
    _filter_api_(command='{}/Sorting'.format(id))


def filter_preview():
    _filter_api_(command='Filter/Preview', call_type=Api.POST)


def filter():
    # duplicate filter_preview?
    _filter_api_(command='', call_type=Api.POST)

# endregion

# region tree


tree_api_url = '/api/v{}/{}'


def _tree_api_(command='', call_type=Api.GET, data={}):
    url = tree_api_url.format(api_version, command)
    return _api_call_(url=url, call_type=call_type, data=data)


def tree_filter(includeEmpty=False, includeInvisible=False):
    from models import Filter
    response = _tree_api_(command='Filter?includeEmpty={}&includeInvisible={}'.format(bool(includeEmpty), bool(includeInvisible)))
    return json.loads(response, object_hook=Filter.Decoder)  # cls=json.JSONDecoder) #


def tree_group_in_filter_by_id(id):
    from models import Group
    response = _tree_api_(command='Filter/{}/Group'.format(int(id)))
    return json.loads(response, object_hook=Group.Decoder)


def tree_group_by_id_in_filter_by_id(fid, gid):
    from models import Series
    response = _tree_api_(command='Filter/{}/Group/{}/Series'.format(int(fid), int(gid)))
    return json.loads(response, object_hook=Series.Decoder)


def tree_episode_in_series_by_id(id, includeMissing=False):
    from models import Episode
    response = _tree_api_(command='Series/{}/Episode?includeMissing={}'.format(int(id), bool(includeMissing)))
    return json.loads(response, object_hook=Episode.Decoder)


# endregion

# region folder

folder_api_url = '/api/v{}/Folder'


def _folder_api(command='', call_type=Api.GET, data={}):
    url = folder_api_url.format(api_version, command)
    _api_call_(url=url, call_type=call_type, data=data)


def folder_drives():
    _folder_api(command='/drives')


def folder(path):
    _folder_api(command='?path={}'.format(str(path)))


# endregion

# region group

group_api_url = '/api/v{}/Group'


def _group_api(command='', call_type=Api.GET, data={}):
    url = group_api_url.format(api_version, command)
    _api_call_(url=url, call_type=call_type, data=data)


def group():
    _group_api()


def group_add(data):
    _group_api(call_type=Api.POST, data=data)


def group_by_id(id):
    _group_api(command='/{}'.format(int(id)))


def group_by_id_recalculate(id):
    _group_api(command='/{}/Recalculate'.format(int(id)), call_type=Api.POST)


def delete_group_by_id(id, deleteSeries=False, deleteFiles=False):
    _group_api(command='/{}?deleteSeries={}&deleteFiles={}'.format(int(id), bool(deleteSeries), bool(deleteFiles)))


def recreate_all_groups():
    _group_api(command='/RecreateAllGroups')

# endregion

# region image


image_api_url = '/api/v{}/Image/{}'


def _image_api(command='', call_type=Api.GET, data={}):
    url = image_api_url.format(api_version, command)
    return _api_call_(url=url, call_type=call_type, data=data)


def image(source, type, value):
    from models import Images
    response = _image_api(command='{}/{}/{}'.format(str(source), str(type), str(value)))
    # return binary image
    return response

# endregion

# region import folder

import_folder_api_url = '/api/v{}/ImportFolder'


def _import_folder_api(command='', call_type=Api.GET, data={}):
    url = import_folder_api_url.format(api_version, command)
    _api_call_(url=url, call_type=call_type, data=data)


def import_folder():
    _import_folder_api()


def import_folder_add(data):
    _import_folder_api(data=data, call_type=Api.POST)


def import_folder_update(data):
    _import_folder_api(date=data, call_type=Api.PUT)


def import_folder_by_id(id):
    _import_folder_api(command='/{}'.format(int(id)), call_type=Api.PATCH)


def delete_import_folder_by_id(id, removeRecords=True, updateMyList=True):
    _import_folder_api(command='/{}?removeRecords={}&'.format(int(id), bool(removeRecords), bool(updateMyList)), call_type=Api.DELETE)


def scan_import_folder_by_id(id):
    _import_folder_api(command='/{}/Scan'.format(int(id)))


# endregion

# region init

init_api_url = '/api/v{}/Init/{}'


def _init_api(command='', call_type=Api.GET, data={}):
    url = init_api_url.format(api_version, command)
    return _api_call_(url=url, call_type=call_type, data=data)


def version():
    from models import Version

    response = _init_api(command='Version')
    return json.loads(response, object_hook=Version.Decoder)
    # json.dumps(y, cls=Version.Encoder)


def status():
    from models import Status

    response = _init_api(command='status')
    return json.loads(response, object_hook=Status.Decoder)


def inuse():
    from models import InUse

    response = _init_api(command='inuse')
    return json.loads(response, object_hook=InUse.Decoder)


def default_user():
    from models import DefaultUser
    response = _init_api(command='defaultuser')
    return json.loads(response, object_hook=DefaultUser.Decoder)


def create_default_user(username, password):
    data = {'Username': str(username), 'Password': str(password)}
    response = _init_api(command='defaultuser', data=data, call_type=Api.POST)


def start_server():
    response = _init_api(command='startserver')


def database_test():
    response = _init_api(command='database/test')


def database_instance():
    response = _init_api(command='database/sqlserverinstance')

# endregion

# region integrity check


integrity_check_api_url = '/api/v{}/IntegrityCheck'


def _integrity_check_api(command='', call_type=Api.GET, data={}):
    url = integrity_check_api_url.format(api_version, command)
    _api_call_(url=url, call_type=call_type, data=data)


def integrity_check(data):
    _init_api(call_type=Api.POST, data=data)


def integrity_check_by_id(id):
    _init_api(command='/{}/Start')

# endregion

# region plex webhook

# TODO PLEX

# endregion

# region renamer

# TODO renamer

# endregion

# region reverse tree


reverse_tree_api_url = '/api/v{}/{}'


def _reverse_tree_api(command='', call_type=Api.GET, data={}):
    url = reverse_tree_api_url.format(api_version, command)
    return _api_call_(url=url, call_type=call_type, data=data)


def group_from_series_by_id(id):
    from models import Group
    response = _reverse_tree_api(command='Series/{}/Group'.format(int(id)))
    return json.loads(response, object_hook=Group.Decoder)


def series_from_episode_by_id(id):
    from models import Series
    response = _reverse_tree_api(command='Episode/{}/Series'.format(int(id)))
    return json.loads(response, object_hook=Series.Decoder)


def episode_from_file_by_id(id):
    from models import Episode
    response = _reverse_tree_api(command='File/{}/Episode'.format(int(id)))
    return json.loads(response, object_hook=Episode.Decoder)

# endregion

# region series


series_api_url = '/api/v{}/Series{}'


def _series_api(command='', call_type=Api.GET, data={}):
    url = series_api_url.format(api_version, command)
    return _api_call_(url=url, call_type=call_type, data=data)


def series():
    from models import Series
    response = _series_api()
    return json.loads(response, object_hook=Series.Decoder)


def series_by_id(id):
    from models import Series
    response = _series_api(command='/{}'.format(int(id)))
    return json.loads(response, object_hook=Series.Decoder)


def series_path_ending_with(path):
    from models import Series
    response = _series_api(command='/PathEndsWith/{}'.format(str(path)))
    return json.loads(response, object_hook=Series.Decoder)


def series_by_id_anidb_info(id):
    from models import Series
    response = _series_api(command='/{}/AniDB'.format(int(id)))
    return json.loads(response, object_hook=Series.Decoder)


def series_by_id_tvdb_info(id):
    from models import Series
    response =_series_api(command='/{}/TvDB'.format(int(id)))
    return json.loads(response, object_hook=Series.Decoder)


def images_from_series_by_id(id, includeDisabled=True):
    from models import Images
    response =_series_api(command='/{}/Images/{}'.format(int(id), bool(includeDisabled )))
    return json.loads(response, object_hook=Images.Decoder)


def tag_from_series_by_id_and_filter(id, filter):
    from models import Tags
    response = _series_api(command='/{}/Tags/{}'.format(int(id), int(filter)))
    return json.loads(response, object_hook=Tags.Decoder)


def cast_from_series_by_id(id):
    from models import FullCast
    response = _series_api(command='/{}/Cast'.format(int(id)))
    return json.loads(response, object_hook=FullCast.Decoder)


def move_series_to_group(sid, gid):
    from models import Series
    response = _series_api(command='/{}/Move/{}'.format(int(sid), int(gid)), call_type=Api.PATCH)
    return json.loads(response, object_hook=Series.Decoder)


def delete_series_by_id(id):
    from models import Series
    response = _series_api(command='/{}'.format(int(id)), call_type=Api.DELETE)
    return json.loads(response, object_hook=Series.Decoder)


def search_series(query):
    from models import Series
    response = _series_api(command='/Search/{}'.format(str(query)))
    return json.loads(response, object_hook=Series.Decoder)


def series_starts_with(query):
    from models import Series
    response = _series_api(command='/StartsWith/{}'.format(str(query)))
    return json.loads(response, object_hook=Series.Decoder)


# endregion

# region settings
# TODO settings
# endregion

# region user
# TODO user
# endregion

# flow
# 0.check if online/busy
# 1.login (login='default' password='')
api_key = login_user('default', '', 'from-inside-ide').apikey
x = api_key
print(x)
# 2.save apikey ( apikey is user+device ) / or store it in api_key for debugging
# 3. list all available filters
x = tree_filter()
print(x)
# 4. list all availables groups in filter of id:8  /8 - newly added series
x = tree_group_in_filter_by_id(8)
print(x)
# 5. list all availables series in group of id: 3981 (mine is this)
x = tree_group_by_id_in_filter_by_id(8, 3981)
print(x)
# 6. list all episodes for give series :
x = tree_episode_in_series_by_id(22, True)
print(x)

# region TEST
# region SERIES
x = series()
print(x)

x = series_by_id(22)
print(x)

x = series_path_ending_with('naruto')
print(x)

x = series_by_id_anidb_info(22)
print(x)

# TODO got empty, sure ?
x = series_by_id_tvdb_info(22)
print(x)

x = images_from_series_by_id(22, includeDisabled=True)
print(x)

x = tag_from_series_by_id_and_filter(22, 8)
print(x)

x = cast_from_series_by_id(22)
print(x)

# TODO not doing this right now
# x = move_series_to_group(sid, gid)

# TODO not doing this right now
# x = delete_series_by_id(id)

x = search_series('naruto')
print(x)

x = series_starts_with('ano')
print(x)

# endregion

# region REVERSE_TREE


x = group_from_series_by_id(20)
print(x)

x = series_from_episode_by_id(20)
print(x)

x = episode_from_file_by_id(20)
print(x)

# endregion

# region IMAGE

x = image('AniDB', 'Poster', 1)
print(x)

# endregion
# endregion
