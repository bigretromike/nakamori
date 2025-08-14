# -*- coding: utf-8 -*-
import xbmc # type: ignore
import xbmcgui # type: ignore
import xbmcplugin # type: ignore
import xbmcaddon # type: ignore
import xbmcvfs # type: ignore

from lib.kodi_utils import get_device_id, message_box, debug, if_debug
from models.kodi_models import set_watch_mark, is_series_watched, vote_for_episode, vote_for_series
from lib.naka_utils import ThisType, WatchedStatus
from threading import Thread
import sys
import os
import json
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError

from api.shoko.v2 import api2, api2models
from sqlite3 import dbapi2 as database

plugin_addon = xbmcaddon.Addon(id='plugin.video.nakamori')
profileDir = plugin_addon.getAddonInfo('profile')
profileDir = xbmcvfs.translatePath(profileDir)

db_file = os.path.join(profileDir, 'player.db')

# connect to db
_db_connection = database.connect(db_file)
_db_cursor = _db_connection.cursor()

# create table
try:
    _db_cursor.execute('CREATE TABLE IF NOT EXISTS [player] ([series] INTEGER PRIMARY KEY, [audio] TEXT, [sub] TEXT, [speed] TEXT, [updated] FLOAT)')
    _db_connection.commit()
except:
    pass

# close connection
_db_connection.close()


busy = xbmcgui.DialogProgress()
clientid = get_device_id()
API = api2.Client(address=plugin_addon.getSetting('ipaddress'),
                  port=plugin_addon.getSettingInt('port'),
                  apikey=plugin_addon.getSetting('apikey'),
                  timeout=plugin_addon.getSettingInt('timeout'))


class PlaybackStatus(object):
    PLAYING = 'Playing'
    PAUSED = 'Paused'
    STOPPED = 'Stopped'
    ENDED = 'Ended'


eigakan_url = plugin_addon.getSetting('ipEigakan')
eigakan_port = plugin_addon.getSetting('portEigakan')
eigakan_host = 'http://' + eigakan_url + ':' + eigakan_port

magic_chunk = 'chunk-stream0-00003.m4s'


def get_player_info():
    try:
        # {'id': 1, 'jsonrpc': '2.0', 'result': {'currentaudiostream': {'bitrate': 0, 'channels': 2, 'codec': 'aac', 'index': 0, 'isdefault': True, 'isimpaired': False, 'isoriginal': False, 'language': 'eng', 'name': 'English - AAC-LC stereo', 'samplerate': 0}, 'currentsubtitle': {'index': 1, 'isdefault': True, 'isforced': False, 'isimpaired': False, 'language': 'eng', 'name': 'Dialogue'}, 'speed': 1, 'subtitleenabled': True}}
        _data = json.loads(xbmc.executeJSONRPC(json.dumps({"jsonrpc": "2.0","method": "Player.GetProperties","params":{"playerid": 1,"properties": ["currentsubtitle", "currentaudiostream", "speed", "subtitleenabled"]},"id": 1})))
        _ai = _data['result']['currentaudiostream']['index']  # 0
        _si = _data['result']['currentsubtitle']['index']  # 1
        _se = _data['result']['subtitleenabled']  # True
        _s = _data['result']['speed']  # 1
        debug(str(_data))
        # if file is not playing speed = 0, we dont need that
        if _s == 0:
            _s = 1
        return (_ai, _se, _si, _s)
    except Exception as e:
        debug("issue with get_player_info(): " + str(e))
        return None


def get_user_settings(series_id: int, text: str = ""):
    item = None
    _data = '--before--'
    try:
        db_connection = database.connect(db_file)
        db_cursor = db_connection.cursor()
        db_cursor.execute(f'SELECT audio, sub, speed FROM player WHERE series="{series_id}"')
        _se = True
        _data = db_cursor.fetchone()
        debug('USER_DB_DATA = ' + str(_data) + ' ' + text)
        if _data is not None:
            _a, _si, _s = _data
            if _si == -1:
                _se = False
            return (_a, _se, _si, _s)
    except Exception as E:
        debug('get_user_settings() '+ text + 'issue: ' + str(E) + ' value ' + str(_data))
    return None


def set_user_settings(series_id: int, audio: str, is_sub: bool, sub: str, speed: str):
    date = time.time()
    debug(f'set_user_settings() input: id={series_id}, a={audio}, se={is_sub}, si={sub}, s={speed}, d={date}')
    if is_sub == False:
        sub = -1
        
    try:
        db_connection = database.connect(db_file)
        db_cursor = db_connection.cursor()
        old_settings = get_user_settings(series_id, "inside set_user_settings() ")
        if old_settings is None:
            debug('OLD_SETTINGS IS NONE')
            db_cursor.execute('INSERT INTO player (series, audio, sub, speed, updated) VALUES (?, ?, ?, ?, ?)', (series_id, audio, sub, speed, date))
        else:
            if audio is None:
                audio = old_settings[0]
            if sub is None:
                is_sub = old_settings[1]
                if is_sub == False:
                    sub = -1
                else:
                    sub = old_settings[2]
            db_cursor.execute('UPDATE player set audio = ?, sub = ?, speed = ?, updated = ? where series = ?', (audio, sub, speed, date, series_id))
            debug(f'USER_SETTINGS SAVED: id={series_id}, a={audio}, se={is_sub}, si={sub}, s={speed} ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        db_connection.commit()
        db_connection.close()
    except Exception as e:
        debug('issue with set_user_settings(): ' + str(e))

def trancode_url(file_id):
    video_url = eigakan_host + '/api/transcode/%s/%s' % (clientid, file_id)
    return video_url


def scrobble_trakt(ep_id, status, current_time, total_time, movie):
    if plugin_addon.getSetting('trakt_scrobble') == 'true':
        # clamp it to 0-100
        progress = max(0, min(100, int(current_time / total_time * 100.0)))
        API.episode_scrobble(ep_id, progress, status, movie)


def finished_episode(ep_id, file_id, current_time, total_time):
    debug('----------------------- FINISHIND EPISODE ----------------')
    debug(f'ep_id: {ep_id} / file_id: {file_id} / now: {current_time} / total: {total_time}')

    _finished = False

    mark = float(plugin_addon.getSettingInt('watched_mark'))
    if not plugin_addon.getSettingBool('external_player'):
        pass
    else:
        # mitigate the external player, skipping intro/outro/pv so we cut your setting in half
        mark /= 2
    mark /= 100

    if (total_time * mark) <= current_time:
        _finished = True

    # TODO this got broken for addons in Leia18, until this is somehow fixed we count time by hand (in loop)
    # else:
    # external set position = 1.0 when it want to mark it as watched (based on configuration of external
    # if current_time > 0.0:
    #    _finished = True
    # else:
    #   log('Using an external player, but the settings are set to not mark as watched. Check advancedsettings.xml')
    # _finished = False

    if _finished:
        if int(ep_id) != 0 and plugin_addon.getSettingBool('vote_always'):
            vote_for_episode(ep_id)

        if ep_id != 0:
            set_watch_mark(mark_type=ThisType.episodes, mark_id=ep_id, watched=True)

            # vote on finished series
            if plugin_addon.getSettingBool('vote_on_series'):
                q = api2models.QueryOptions()
                q.id = ep_id
                series: api2models.Serie = API.series_from_ep(q)
                if is_series_watched(series) == WatchedStatus.WATCHED:
                    vote_for_series(series.id)

        elif file_id != 0:
            # file watched states
            pass

        # refresh only when we really did watch episode, this way we wait until all action after watching are executed
        xbmc.executebuiltin('Container.Refresh')
    return _finished


def transcode_play_video(file_id, ep_id=0, mark_as_watched=True, resume=False):
    play_video(file_id, ep_id, mark_as_watched, resume, force_transcode_play=True)


def direct_play_video(file_id, ep_id=0, mark_as_watched=True, resume=False):
    play_video(file_id, ep_id, mark_as_watched, resume, force_direct_play=True)


def play_video(file_id, ep_id=0, s_id=0, mark_as_watched=True, resume=False, force_direct_play=False,
               force_transcode_play=False, party_mode=False):
    """
    Plays a file
    :param file_id: file ID. It is needed to look up the file
    :param ep_id: episode ID, not needed, but it fills in a lot of info
    :param s_id: series ID
    :param mark_as_watched: should we mark it after playback
    :param resume: should we auto-resume
    :param force_direct_play: force direct play
    :param force_transcode_play: force transcoding file
    :param party_mode:
    :return: True if successfully playing
    """

    debug('Get Player')
    # check if we're already playing something
    # player = xbmc.Player()
    player = Player()

    debug('Check if Player is playing video')
    if player.isPlayingVideo():
        debug('Player is playin video...')
        playing_item = player.getPlayingFile()
        debug(f'Video playing: {playing_item}')
        player.stop()
        debug('Player.stop()')

    # wait for it to stop
    while True:
        debug('Waiting for player stopping video...')
        try:
            if not player.isPlayingVideo():
                debug('Player is not playing video')
                break
            xbmc.sleep(500)
            continue
        except:
            debug('Exception in waiting function')
            pass

    # now continue
    url_for_player = ''

    f: api2models.RawFile
    if int(ep_id) != 0:
        debug(f'Episode ID: {ep_id}')
        q = api2models.QueryOptions()
        q.id = ep_id
        ep: api2models.Episode = API.episode_get(q)
        debug(f'Episode data: {str(ep)}')
        series: api2models.Serie
        if s_id == 0:
            debug('Get series info...')
            series = API.series_from_ep(q)
            s_id = series.id
            debug(f'Series data: {str(series)}')
        else:
            q.id = s_id
            debug(f'Series Id: {s_id}')
            series = API.series_get_by_id(q)
            debug(f'Series data: {str(series)}')

        f = API.file(id=file_id)
    else:
        f = API.file(id=file_id)
    debug(f'File Id: {file_id}')
    debug(f'File data: {str(f)}')

    # check if we have same access to file as server aka localhost
    debug('Check if file is accessible')
    if os.path.isfile(f.server_path):
        debug('File accessible, fixing file path')
        if f.server_path.startswith(u'\\\\'):
            url_for_player = 'smb:' + f.server_path.replace('\\', '/')
        else:
            # TODO maybe use xbmcvfs.exists for 404 ?
            url_for_player = f.server_path
        debug(f'File local path: {url_for_player}')
    else:
        try:
            debug('Accessing file via http')
            req = Request(f.url, method='HEAD')
            resp = urlopen(req)
            a = resp.read()
            url_for_player = f.url
            debug(f'File url discovered: {url_for_player}')
        except HTTPError as htterr:
            debug('Error while discovering url via http')
            url_for_player = ''
            if htterr.code == 404:
                message_box(title=plugin_addon.getLocalizedString(30242) + ': ' + str(htterr.code),
                            text=plugin_addon.getLocalizedString(30241))
            else:
                message_box(title=plugin_addon.getLocalizedString(30242),
                            text=str(htterr.code))

    if url_for_player != '':
        is_transcoded = False
        m3u8_url = ''
        subs_extension = ''
        is_finished = False
        if not force_direct_play:
            #if 'smb://' in url_for_player:
            #    url_for_player = f.url
            is_transcoded, m3u8_url, subs_extension, is_finished = process_transcoder(file_id, url_for_player, force_transcode_play)

        debug('Create Nakamori Player')
        # player = Player()
        debug(f'Feed player with file_id: {file_id}, ep_id: {ep_id}, s_id {s_id}, duration: {int(f.duration/1000)}, '
              f'm3u8_url: {m3u8_url}, is_transcoded: {is_transcoded}, url_for_player: {url_for_player}, '
              f'mark_as_watched: {mark_as_watched}')
        player.feed(file_id, ep_id, s_id, int(f.duration/1000), m3u8_url if is_transcoded else url_for_player, mark_as_watched)

        try:
            item = xbmcgui.ListItem(path=url_for_player, offscreen=True)
            item.setProperty('IsPlayable', 'true')
            item.setIsFolder(False)
            from models.kodi_models import set_info_for_episode
            set_info_for_episode(item, ep, series.titles[0].Title)
            # based on https://github.com/xbmc/xbmc/pull/19530  Kodi20
            item.setProperty('ForceResolvePlugin', 'true')

            #file_url = f.url_for_player if f is not None else None

            if is_transcoded:
                debug('Transcoding...')
                # player.play(item=m3u8_url)
                url_for_player = m3u8_url
                item.setPath(url_for_player)
                item.setProperty('inputstreamaddon', 'inputstream.adaptive')
                item.setProperty('inputstream.adaptive.manifest_type', 'mpd')
                item.setMimeType('application/dash+xml')
                item.setContentLookup(False)

                # TODO maybe extract all subs and include them ?
                subs_url = eigakan_host + '/api/video/%s/%s/subs.%s' % (clientid, file_id, subs_extension)
                #if pyproxy.head(url_in=subs_url):
                #    item.setSubtitles([subs_url, ])
                #    item.addStreamInfo('subtitle', {'language': 'Default', })
            else:
                debug(f'setPath: {url_for_player}')
                item.setPath(url_for_player)

            debug(f'============== [ HANDLE for Player ] = {sys.argv[1]}')
            try:
                handle = int(sys.argv[1])
                #xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), listitem=item, url=url_for_player, isFolder=False, totalItems=1)
                #xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True, cacheToDisc=False)

                if handle == -1:
                    debug('Player method: play')

                    player.play(item=url_for_player, listitem=item)
                else:
                    # item.setContentLookup(False)
                    # item.setMimeType('video/x-matroska')
                    debug('Player method: setResolvedUrl')
                    # thanks to anxdpanic for pointing in right direction
                    xbmcplugin.setResolvedUrl(handle, True, item)
            except:
                debug('Error in handle, use method: play')
                # when playing thing tru context menu, handle is not there
                # TODO without handle there is no episode info we can look, Is it a dealbreaker? no but if fix is there use one.
                player.play(item=url_for_player, listitem=item)
        except Exception as e:
            xbmc.log('ERROR NAKA PLAYER---------------------------', xbmc.LOGERROR)
            xbmc.log(f'{e}', xbmc.LOGINFO)

        debug('Player loop: start')
        # leave loop from player alive so we can handle onPlayBackStopped/onPlayBackEnded
        player_loop(player, is_transcoded, is_finished, ep_id, party_mode)
        debug('Player loop: stops')
    del player


def player_loop(player, is_transcoded, is_transcode_finished, ep_id, party_mode):
    monitor = xbmc.Monitor()
    try:
        # seek to beginning of stream :hack: https://github.com/peak3d/inputstream.adaptive/issues/94
        if is_transcoded:
            while not xbmc.Player().isPlayingVideo():
                monitor.waitForAbort(0.25)

            if not is_transcode_finished:
                if xbmc.Player().isPlayingVideo():
                    #log('Seek back - so the stream is from beginning')
                    # TODO part1: hack is temporary and not working in 100%
                    # TODO part2: (with small segments + fast cpu, you wont start from 1st segment)
                    # xbmc.executebuiltin('Seek(-60)')
                    xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Player.Seek","params":{"playerid":1,"value":{"seconds":0}},"id":1}')

        # let's check if the only file in player has started
        while not player.started_playing:
            xbmc.sleep(500)

        while player.PlaybackStatus != PlaybackStatus.STOPPED and player.PlaybackStatus != PlaybackStatus.ENDED:
            # we loop here so threads that updates status can work, without this they will get killed
            # because 'player' will exit
            xbmc.sleep(500)

        if player.PlaybackStatus == PlaybackStatus.STOPPED or player.PlaybackStatus == PlaybackStatus.ENDED:
            if player.is_finished:
                pass
                #log('post-finish: start events')

                # if ep_id != 0:
                #     from shoko_models.v2 import Episode
                #     ep = Episode(ep_id, build_full_object=False)
                #     spam('mark as watched, episode')
                #     ep.set_watched_status(True)
                #
                # # wait till directory is loaded
                # while kodi_utils.is_dialog_active():
                #     xbmc.sleep(500)
                # # refresh it, so it moves onto next item and the mark watched is refreshed
                # kodi_utils.refresh()
                #
                # # wait till it load again
                # while kodi_utils.is_dialog_active():
                #     xbmc.sleep(500)
                #
                # if int(ep_id) != 0 and plugin_addon.getSetting('vote_always') == 'true' and not party_mode:
                #     spam('vote_always, voting on episode')
                #     script_utils.vote_for_episode(ep_id)
                #
                # if int(ep_id) != 0 and plugin_addon.getSetting('vote_on_series') == 'true' and not party_mode:
                #     from shoko_models.v2 import get_series_for_episode
                #     series = get_series_for_episode(ep_id)
                #     # voting should be only when you really watch full series
                #     spam('vote_on_series, mark: %s / %s' % (
                #         series.sizes.watched_episodes, series.sizes.total_episodes))
                #     if series.sizes.watched_episodes - series.sizes.total_episodes == 0:
                #         script_utils.vote_for_series(series.id)

            return -1
        else:
            pass
    except Exception as e:
        xbmc.log(f'=== player_loop exception: {e}', xbmc.LOGINFO)
    del monitor


def get_client_settings():
    settings = {}
    #try:
    #    settings = json.loads(pyproxy.get_json(eigakan_host + '/api/clientid/%s' % clientid))
    #except http_error as er:
    #    if er.code == 404:
    #        log('Client profile not found on Eigakan, sending new one...')
    #        kodi_utils.send_profile()
    return settings


def process_transcoder(file_id, file_url, force_transcode_play=False):
    """

    :param file_id:
    :param file_url:
    :param force_transcode_play: force transcode
    :return:
    """

    is_transcoded = False
    m3u8_url = ''
    subs_type = ''
    is_finished = False

    # if plugin_addon.getSetting('enableEigakan') != 'true' and not force_transcode_play:
    #     return is_transcoded, m3u8_url, subs_type, is_finished
    #
    # video_url = trancode_url(file_id)
    # post_data = '"file":"' + file_url + '"'
    #
    # is_dash = True
    # end_url = eigakan_host + '/api/video/%s/%s/end.eigakan' % (clientid, file_id)
    # if is_dash:
    #     m3u8_url = eigakan_host + '/api/video/%s/%s/play.mpd' % (clientid, file_id)
    #     ts_url = eigakan_host + '/api/video/%s/%s/%s' % (clientid, file_id, magic_chunk)
    # else:
    #     m3u8_url = eigakan_host + '/api/video/%s/%s/play.m3u8' % (clientid, file_id)
    #     ts_url = eigakan_host + '/api/video/%s/%s/play0.ts' % (clientid, file_id)
    #
    # try:
    #     kodi_utils.check_eigakan()
    #
    #     # server is alive so send profile of device we didn't before
    #     if plugin_addon.getSetting('eigakan_handshake') == 'false':
    #         kodi_utils.send_profile()
    #     settings = get_client_settings()
    #
    #     # check if file is already transcoded
    #     is_finished = pyproxy.head(url_in=end_url)
    #     if not is_finished:
    #         # let's probe file, maybe we already know which streams we want
    #         busy.create(plugin_addon.getLocalizedString(30160), plugin_addon.getLocalizedString(30177))
    #         audio_streams, subs_streams = eigakan_utils.probe_file(file_id, file_url)
    #         busy.close()
    #
    #         # pick streams that are preferred via profile on eigakan
    #         a_index, s_index, subs_type = eigakan_utils.pick_best_streams(audio_streams, subs_streams)
    #
    #         # region BUSY Dialog Hell
    #         # please wait, Sending request to Transcode server...
    #         busy.create(plugin_addon.getLocalizedString(30160), plugin_addon.getLocalizedString(30165))
    #         if a_index > -1:
    #             post_data += ',"audio":"%s"' % a_index
    #         if s_index > -1:
    #             post_data += ',"subtitles":"%s"' % s_index
    #         pyproxy.post_json(video_url, post_data, custom_timeout=0.1)  # non blocking
    #         xbmc.sleep(1000)
    #         # busy.close()
    #
    #         try_count = 0
    #         found = False
    #         # please wait,waiting for being queued
    #         busy.update(0, plugin_addon.getLocalizedString(30192))
    #         while True:
    #             if busy.iscanceled():
    #                 break
    #             if eigakan_utils.is_fileid_added_to_transcoder(file_id):
    #                 break
    #
    #             try_count += 1
    #             busy.update(try_count)
    #             xbmc.sleep(1000)
    #
    #         try_count = 0
    #         found = False
    #         # plase wait, waiting for subs to be dump
    #         busy.update(try_count, plugin_addon.getLocalizedString(30205))
    #         while True:
    #             if busy.iscanceled():
    #                 break
    #             ask_for_subs = json.loads(pyproxy.get_json(eigakan_host + '/api/queue/%s' % file_id))
    #             if ask_for_subs is None:
    #                 ask_for_subs = {}
    #             y = ask_for_subs.get('queue', {"videos": {}}).get('videos', {})
    #
    #             for k in y:
    #                 if int(k) == int(file_id):
    #                     found = True
    #                     break
    #                 if found:
    #                     break
    #             if found:
    #                 break
    #             try_count += 1
    #             if try_count >= 100:
    #                 try_count = 0
    #                 busy.update(try_count, plugin_addon.getLocalizedString(30218))
    #             busy.update(try_count)
    #             xbmc.sleep(1000)
    #
    #         try_count = 0
    #         found = False
    #         # please waiting, waiting for starting transcode
    #         busy.update(try_count, plugin_addon.getLocalizedString(30206))
    #         while True:
    #             if busy.iscanceled():
    #                 break
    #             ask_for_subs = json.loads(pyproxy.get_json(eigakan_host + '/api/queue/%s' % file_id))
    #             if ask_for_subs is None:
    #                 ask_for_subs = {}
    #             x = ask_for_subs.get('queue', {"videos": {}}).get('videos', {})
    #             for k in x:
    #                 if int(k) == int(file_id):
    #                     percent = x[k].get('percent', 0)
    #                     if int(percent) > 0:
    #                         found = True
    #                         log('percent found of transcoding: %s' % percent)
    #                         break
    #             if found:
    #                 break
    #             try_count += 1
    #             if try_count >= 100:
    #                 try_count = 0
    #                 busy.update(try_count, plugin_addon.getLocalizedString(30218))
    #             busy.update(try_count)
    #             xbmc.sleep(1000)
    #
    #         try_count = 0
    #         # please wait, Waiting for response from Server...
    #         busy.update(try_count, plugin_addon.getLocalizedString(30164))
    #         while True:
    #             if busy.iscanceled():
    #                 break
    #             if pyproxy.head(url_in=ts_url) is False:
    #                 try_count += 1
    #                 busy.update(try_count)
    #                 xbmc.sleep(1000)
    #             else:
    #                 break
    #         busy.close()
    #
    #         # endregion
    #
    #     if pyproxy.head(url_in=ts_url):
    #         is_transcoded = True
    #
    # except:
    #     eh.exception(ErrorPriority.BLOCKING)
    #     try:
    #         busy.close()
    #     except:
    #         pass

    return is_transcoded, m3u8_url, subs_type, is_finished


# TODO this could be reusable and used before probing ?
# TODO part2: check if data in shoko are populated correctly + send in api (still)
# def find_language_index(streams, setting):
#    stream_index = -1
#    stream_id = -1
#    for code in setting.split(','):
#        for stream in streams:
#            stream_index += 1
#            if code in streams[stream].get('Language', '').lower() != '':
#                stream_id = stream_index
#                break
#            if code in streams[stream].get('LanguageCode', '').lower() != '':
#                stream_id = stream_index
#                break
#            if code in streams[stream].get('Title', '').lower() != '':
#                stream_id = stream_index
#                break
#        if stream_id != -1:
#            break
#    return stream_id


# noinspection PyUnusedFunction
class Player(xbmc.Player):
    def __init__(self):
        debug('Player Initialized')
        xbmc.Player.__init__(self)
        self._t: Thread = None  # trakt thread
        self._t_running = True
        self._s: Thread = None  # shoko thread
        self._s_running = True
        self._u: Thread = None  # update thread
        self._u_running = True
        self._n: Thread = None  # user_settings thread
        self._n_running = True
        self._details = None
        self.Playlist = None
        self.PlaybackStatus = PlaybackStatus.STOPPED
        # self.LoopStatus = 'None'
        # self.Shuffle = False
        self.is_transcoded = False
        self.is_movie = None
        self.file_id = 0
        self.ep_id = 0
        self.s_id = 0
        # we will store duration and time in kodi format here, so that calls to the player will match
        self.duration = 0
        self.time = 0
        self.path = ''
        self.scrobble = True
        self.is_external = False
        self.is_finished = False
        self.party_mode = False
        self.started_playing = False
        self.CanControl = True
        self.user_setting_loaded = False
        self.user_speed = 1.0
        self.user_audio_index = None
        self.user_sub = None
        self.user_sub_index = None
        self.shoko_offset_update_allow = True

    def reset(self):
        debug('Player reset')
        self.__init__()

    def feed(self, file_id, ep_id, s_id, duration, path, scrobble):
        debug('Player feed - file_id=%s ep_id=%s s_id=%s duration=%s path=%s scrobble=%s' % (file_id, ep_id, s_id, duration, path, scrobble))
        self.file_id = file_id
        self.ep_id = ep_id
        self.s_id = s_id
        self.duration = duration
        self.path = path
        self.scrobble = scrobble

    def update_user_setting(self):
        if self.user_setting_loaded:
            try:
                if not self.isExternalPlayer() and self.isPlayingVideo():
                    _s = get_player_info()
                    debug('update_user_setting(): ' + str(_s))
                    if _s is not None:
                        audio, is_sub, sub, speed = _s
                        self.user_speed = speed
                        self.user_audio_index = audio
                        self.user_sub = is_sub
                        self.user_sub_index = sub
                        set_user_settings(self.s_id, self.user_audio_index, self.user_sub, self.user_sub_index, self.user_speed)
            except Exception as e:
                debug('issue in update_user_setting(): ' + str(e))
        else:
            debug('update_user_setting() not triggered because not self.user_setting_loaded')
            
    def pass_user_setting_to_player(self, audio, is_sub, sub, speed):
        try:
            # _data = json.loads(xbmc.executeJSONRPC(json.dumps({"jsonrpc": "2.0","method": "Player.GetProperties","params":{"playerid": 1,"properties": ["currentsubtitle", "currentaudiostream", "speed", "subtitleenabled"]},"id": 1})))
            # debug(str(_data))
            # speed is fast-fowarding but I dont judge; You need to enable Sync_playback_to_display to being able to speed up until 1.5
            # tempo is what we need but kodi dont allow to access it, we need to intercept keymapping and inject counter etc.... 
            # 
            debug(f'user_setting: SetSpeed {speed}')
            _a1 = xbmc.executeJSONRPC(json.dumps({"jsonrpc":"2.0","id":1,"method":"Player.SetSpeed","params":{"playerid": 1, "speed": int(speed)}}))
            # TODO setting works, reading does not, I dont want custom windows to set speed
            # _a11 = xbmc.executeJSONRPC(json.dumps({"jsonrpc":"2.0","id":1,"method":"Player.SetTempo","params":{"playerid": 1, "tempo": 1.2}}))  
            debug('JSON-RPC: speed: ' + str(_a1))
            # debug('JSON-RPC: tempo: ' + str(_a11))
            debug(f'user_setting: SetAudioStream {audio}')
            # _a2 = xbmc.executeJSONRPC(json.dumps({"jsonrpc":"2.0","id":1,"method":"Player.SetAudioStream","params":{"playerid": 1, "stream": int(audio)}}))
            self.setAudioStream(int(audio))
            debug(f'user_setting: SetSubtitle {sub}')
            if str(is_sub).lower() == "true":
                # enabling subtitles via JSON-RPC add 10second delay before they are shown, to fix it you have to Seek, which is not fun for multi episode night
                #_a3 = xbmc.executeJSONRPC(json.dumps({"jsonrpc":"2.0","id":1,"method":"Player.SetSubtitle","params":{"playerid": 1, "subtitle": int(sub), "enable": True}}))
                debug('enable subs')
                self.setSubtitleStream(int(sub))
                self.showSubtitles(True)
            else:
                #_a3 = xbmc.executeJSONRPC(json.dumps({"jsonrpc":"2.0","id":1,"method":"Player.SetSubtitle","params":{"playerid": 1, "subtitle": "off", "enable": False}}))
                debug('disable subs')
                self.showSubtitles(False)
            
            # debug('JSON-RPC: audio: ' + str(_a2))
            # debug('JSON-RPC: subtitle: ' + str(_a3))
        except Exception as E:
            debug('issue in pass_user_setting_to_player: ' + str(E))

    def onAVStarted(self):
        # Will be called when Kodi has a video or audiostream, before playing file
        # this is good place for user_settings, this is trigger just after loading audio/video stream to player, and is trigger once (please test it)
        debug('onAVStarted')
        debug('Series:' + str(self.s_id) + ' Episode:' + str(self.ep_id) + ' File:' + str(self.file_id))
        
        debug('Access user audio/sub settings for this series')
        _settings = get_user_settings(self.s_id)
        debug('USER_SETTING: ' + str(_settings))
        #self.user_setting_loaded = True
        if _settings is not None:
            audio, is_sub, sub, speed = _settings
            self.user_speed = speed
            self.user_audio_index = audio
            self.user_sub = is_sub
            self.user_sub_index = sub
            self.pass_user_setting_to_player(self.user_audio_index, self.user_sub, self.user_sub_index, self.user_speed)
            xbmc.sleep(1000)
            self.user_setting_loaded = True
        else:
            # if missing use default ones
            self.update_user_setting()

        # isExternalPlayer() ONLY works when isPlaying(), other than that it throw 0 always
        # setting it before results in false setting
        try:
            # is_external = str(kodi_proxy.external_player(self)).lower()
            #plugin_addon.setSetting(id='external_player', value=is_external)
            pass
        except:
            #eh.exception(ErrorPriority.HIGH)
            pass
        #spam(self)
        
        #if kodi_proxy.external_player(self):
        #    log('Using External Player')
        #    self.is_external = True

    def onAVChange(self):
        # Will be called when Kodi has a video, audio or subtitle stream. Also happens when the stream changes. - naka - which is also change of audio stream, but not sub stream
        # also this is trigger few times just before playing file (on loading audio stream, then on loading video stream)
        debug('onAVChange')
        # self.update_user_setting() # overwrite setting while setting player with user settings

    def onPlayBackStarted(self):
        debug('onPlayBackStarted')
        self.started_playing = True
        try:
            if plugin_addon.getSetting('enableEigakan') == 'true':
                #log('Player is set to use Transcoding')
                self.is_transcoded = True

            # wait until the player is init'd and playing
            self.set_duration()

            self.PlaybackStatus = PlaybackStatus.PLAYING
            # we are making the player global, so if a stop is issued, then Playing will change
            while not self.isPlaying() and self.PlaybackStatus == PlaybackStatus.PLAYING:
                xbmc.sleep(250)

            # TODO get series and populate info so we know if its movie or not
            # TODO maybe we could read trakt_id from shoko,
            self.is_movie = False
            if self.duration > 0 and self.scrobble:
                scrobble_trakt(self.ep_id, 1, self.getTime(), self.duration, self.is_movie)

            self.start_loops()
        except:
            #eh.exception(ErrorPriority.HIGHEST)
            pass

    def onPlayBackResumed(self):
        debug('onPlayBackResumed')
        self.PlaybackStatus = PlaybackStatus.PLAYING
        try:
            self.start_loops()
        except:
            #eh.exception(ErrorPriority.HIGH)
            pass

    def start_loops(self):
        debug('===== [ naka-player ] ===== start_loops')
        try:
            self.kill_tick_loop_trakt()
        except Exception as e:
            debug(f'===== [ naka-player ] ===== {e}')
            pass
        self._t_running = True
        self._t = Thread(target=self.tick_loop_trakt, args=())
        self._t.daemon = True
        self._t.start()

        try:
            self.kill_tick_loop_shoko()
        except:
            pass
        self._s_running = True
        self._s = Thread(target=self.tick_loop_shoko, args=())
        self._s.daemon = True
        self._s.start()

        try:
            self.kill_tick_loop_update_time()
        except:
            pass
        self._u_running = True
        self._u = Thread(target=self.tick_loop_update_time, args=())
        self._u.daemon = True
        self._u.start()
        
        try:
            self.kill_tick_loop_user()
        except:
            pass
        self._n_running = True
        self._n = Thread(target=self.tick_loop_user, args=())
        self._n.daemon = True
        self._n.start()
        
        debug('===== [ naka-player ] ===== end start_loops')

    def onPlayBackStopped(self):
        try:
            self.handle_finished_episode()
        except:
            pass
        self.PlaybackStatus = PlaybackStatus.STOPPED

    def onPlayBackEnded(self):
        try:
            self.handle_finished_episode()
        except:
            pass
        self.PlaybackStatus = PlaybackStatus.ENDED

    def onPlayBackPaused(self):
        debug('onPlayBackPaused')
        self.update_user_setting()
        self.PlaybackStatus = PlaybackStatus.PAUSED
        self.scrobble_time()

    def onPlayBackSeek(self, time_to_seek, seek_offset):
        self.time = self.getTime()
        self.scrobble_time()

    def set_duration(self):
        try:
            if self.duration != 0 and self.duration != 0.0:
                return
            duration = int(self.getTotalTime())
            if self.is_transcoded:
                duration = self.duration
            self.duration = duration
        except:
            pass

    def scrobble_time(self):
        if not self.scrobble:
            return
        try:
            scrobble_trakt(self.ep_id, 2, self.time, self.duration, self.is_movie)
        except:
            pass

    def kill_tick_loop_trakt(self):
        self._t_running = False

    def tick_loop_trakt(self):
        if not self.scrobble:
            return
        while self._t_running:
            if not self._t_running:
                break
            if self.PlaybackStatus == PlaybackStatus.PLAYING and self.isPlayingVideo():
                try:
                    scrobble_trakt(self.ep_id, 1, self.time, self.duration, self.is_movie)
                except:
                    pass
                for x in range(0, 10):
                    xbmc.sleep(1000)
                    if self._t_running:
                        break
        debug('===== [ naka-player ] ===== KILLED: tick_loop_trakt')

    def kill_tick_loop_shoko(self):
        self._s_running = False

    def tick_loop_shoko(self):
        if not self.scrobble:
            return
        while self._s_running:
            if not self._s_running:
                break
            if self.PlaybackStatus == PlaybackStatus.PLAYING and self.isPlayingVideo():
                try:
                    if plugin_addon.getSettingBool('file_resume') and self.time > 10 and self.shoko_offset_update_allow:
                        self.shoko_offset_update_allow = False
                        x = API.file_offset({"id": self.file_id, "offset": int(self.time)})
                        xbmc.sleep(1000) # wait 3 seconds, because with higher Tempo we hit this more often
                        self.shoko_offset_update_allow = True
                        if if_debug():
                            # 5 years and kodi did not fix the issue, leaving this to easy check for fix
                            debug(str(xbmc.executeJSONRPC('{"jsonrpc":"2.0","id":6,"method":"Player.GetItem","params":{"playerid":1,"properties":["dynpath","showtitle","title","episode","season","uniqueid","playcount","lastplayed","userrating","tvshowid","file","mediapath"]}}')))
                except:
                    self.shoko_offset_update_allow = True
                    
            for x in range(10):
                xbmc.sleep(1000)
                if not self._s_running:
                    break
        debug('===== [ naka-player ] ===== KILLED: tick_loop_shoko')

    def kill_tick_loop_update_time(self):
        self._u_running = False

    def tick_loop_update_time(self):
        while self._u_running:
            if not self._u_running:
                break
                
            if self.PlaybackStatus == PlaybackStatus.PLAYING and self.isPlayingVideo():
                try:
                    # Leia seems to have a bug where calling self.getTotalTime() fails at times
                    # Try until it succeed (we first init duration from feed())
                    self.set_duration()
                    if not self.is_external:
                        self.time = self.getTime()
                        if self.time is None:
                            debug('[ naka-player-external time is None ]')
                        else:
                            debug('[ naka-player-external ] time = ' + str(self.time))
                    else:
                        self.time += 5
                        debug('[ naka-player-external +5] time = ' + str(self.time))
                except:
                    pass  # while buffering/loading getTime() will raise error

            for _ in range(5):
                xbmc.sleep(1000)
                if not self._u_running:
                    break
        debug('===== [ naka-player ] ===== KILLED: tick_loop_update_time')
        
    def kill_tick_loop_user(self):
        self._n_running = False

    def tick_loop_user(self):
        while self._n_running:
            if not self._n_running:
                break
            try:
                # try to update current used settings as user settings # once 60 second
                self.update_user_setting()
            except:
                pass

            for x in range(0, 60):
                xbmc.sleep(1000)
                if not self._n_running:
                    break
        debug('===== [ naka-player ] ===== KILLED: tick_loop_user')

    def handle_finished_episode(self):
        self.Playlist = None

        if self.scrobble:
            scrobble_trakt(self.ep_id, 3, self.time, self.duration, self.is_movie)

        if self.is_transcoded:
            #pyproxy.get_json(trancode_url(self.file_id) + '/cancel')
            pass

        self.is_finished = finished_episode(self.ep_id, self.file_id, self.time, self.duration)
        
        self._t_running = False
        self._s_running = False
        self._u_running = False
        self._n_running = False
        # self.kill_tick_loop_trakt()
        # self.kill_tick_loop_shoko()
        # self.kill_tick_loop_update_time()
        # self.kill_tick_loop_user()
        
        def stop_thread(thread, thread_name=""):
            if thread and thread.is_alive():
                debug(f"Stopping {thread_name} thread...")
                thread.join(timeout=5.0)  # Wait up to 5 seconds for clean shutdown
                if thread.is_alive():
                    debug(f"Warning: {thread_name} thread did not stop gracefully")
        
        stop_thread(self._t, "Trakt")
        stop_thread(self._s, "Shoko")
        stop_thread(self._u, "Update Time")
        stop_thread(self._n, "User Settings")        
        
        self._t = None
        self._s = None
        self._u = None
        self._n = None
        # self._t.join()
        # self._s.join()
        # self._u.join()
        # self._n.join()
        # self._t.stop()
        # self._s.stop()
        # self._u.stop()
        # self._n.stop()
