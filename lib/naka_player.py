# -*- coding: utf-8 -*-
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

from lib.kodi_utils import get_device_id

#from nakamori_utils.globalvars import *
#from nakamori_utils import script_utils, kodi_utils, eigakan_utils
from threading import Thread

#from proxy.kodi_version_proxy import kodi_proxy
#from proxy.python_version_proxy import python_proxy as pyproxy
#from proxy.python_version_proxy import http_error as http_error
#import error_handler as eh
#from error_handler import spam, log, ErrorPriority
import json
import sys

from api.shoko.v2 import api2, api2models


plugin_addon = xbmcaddon.Addon(id='plugin.video.nakamori')

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


def trancode_url(file_id):
    video_url = eigakan_host + '/api/transcode/%s/%s' % (clientid, file_id)
    return video_url


def scrobble_trakt(ep_id, status, current_time, total_time, movie):
    if plugin_addon.getSetting('trakt_scrobble') == 'true':
        # clamp it to 0-100
        progress = max(0, min(100, int(current_time / total_time * 100.0)))
        API.episode_scrobble(ep_id, progress, status, movie)


def finished_episode(ep_id, file_id, current_time, total_time):
    _finished = False
    # spam('finished_episode > ep_id = %s, file_id = %s, current_time = %s, total_time = %s' % (ep_id, file_id, current_time, total_time))
    mark = float(plugin_addon.getSetting('watched_mark'))
    if plugin_addon.getSetting('external_player').lower() == 'false':
        pass
    else:
        # mitigate the external player, skipping intro/outro/pv so we cut your setting in half
        mark /= 2
    mark /= 100
    # spam('mark = %s * total (%s) = %s vs current = %s' % (mark, total_time, (total_time * mark), current_time))
    if (total_time * mark) <= current_time:
        _finished = True
        # log('Video current_time (%s) has passed watch mark (%s). Marking is as watched!' % (current_time, (total_time * mark)))

    # TODO this got broken for addons in Leia18, until this is somehow fixed we count time by hand (in loop)
    # else:
    # external set position = 1.0 when it want to mark it as watched (based on configuration of external
    # if current_time > 0.0:
    #    _finished = True
    # else:
    #   log('Using an external player, but the settings are set to not mark as watched. Check advancedsettings.xml')
    # _finished = False
    if _finished:
        if int(ep_id) != 0 and plugin_addon.getSetting('vote_always') == 'true':
            #spam('vote_always, voting on episode')
            # TODO rating
            #API.episode_vote()
            pass

        if ep_id != 0:
            API.episode_watch(ep_id)
            #spam('mark as watched, episode')

            # vote on finished series
            if plugin_addon.getSetting('vote_on_series') == 'true':
                q = api2models.QueryOptions()
                q.id = ep_id
                series: api2models.Serie = API.series_from_ep(q)
                # voting should be only when you really watch full series
                # spam('vote_on_series, mark: %s / %s' % (series.watched_sizes.Episodes, series.total_sizes.Episodes))
                if series.watched_sizes.Episodes - series.total_sizes.Episodes == 0:
                    #script_utils.vote_for_series(series.id)
                    # TODO rating
                    pass

        elif file_id != 0:
            # file watched states
            pass

        # refresh only when we really did watch episode, this way we wait until all action after watching are executed
        #script_utils.arbiter(10, 'Container.Refresh')


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
    :param mark_as_watched: should we mark it after playback
    :param resume: should we auto-resume
    :param force_direct_play: force direct play
    :param force_transcode_play: force transcoding file
    :return: True if successfully playing
    """

    #eh.spam('Processing play_video %s %s %s %s %s %s' % (file_id, ep_id, mark_as_watched, resume, force_direct_play, force_transcode_play))

    #from shoko_models.v2 import Episode, File, get_series_for_episode

    # check if we're already playing something
    player = xbmc.Player()

    if player.isPlayingVideo():
        playing_item = player.getPlayingFile()
        #log('Player is currently playing %s' % playing_item)
        #log('Player Stopping')
        player.stop()

    # wait for it to stop
    while True:
        try:
            if not player.isPlayingVideo():
                break
            xbmc.sleep(500)
            continue
        except:
            pass

    # now continue
    file_url = ''
    f: api2models.RawFile
    if int(ep_id) != 0:
        q = api2models.QueryOptions()
        q.id = ep_id
        ep: api2models.Episode = API.episodes_get(q)
        #ep = Episode(ep_id, build_full_object=True)
        #series = get_series_for_episode(ep_id)
        series: api2models.Serie
        if s_id == 0:
            series = API.series_from_ep(q)
        else:
            q.id = s_id
            series = API.series_get(q)
        #ep.series_id = series.id
        #ep.series_name = series.name
        # item = ep.get_listitem()
        #f = ep.get_file_with_id(file_id)
        f = API.file(id=file_id)
    else:
        f = API.file(id=file_id)
        # item = f.get_listitem()

    #if item is not None:
    #    if resume:
    #        # TODO looks like this does nothing...
    #        item.resume()
    #    else:
    #        item.setProperty('ResumeTime', '0')
    #    file_url = f.url_for_player if f is not None else None

    if file_url is not None:
        is_transcoded = False
        m3u8_url = ''
        subs_extension = ''
        is_finished = False
        if not force_direct_play:
            if 'smb://' in file_url:
                file_url = f.url
            is_transcoded, m3u8_url, subs_extension, is_finished = process_transcoder(file_id, file_url,
                                                                                      force_transcode_play)

        player = Player()
        player.feed(file_id, ep_id, f.duration, m3u8_url if is_transcoded else file_url, mark_as_watched)

        try:
            item = xbmcgui.ListItem()
            item.setProperty('IsPlayable', 'true')

            if is_transcoded:
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
                # file_url = f.remote_url_for_player
                # player.play(item=file_url, listitem=item)
                url_for_player = f.url  # file_url
                item.setPath(url_for_player)

            handle = int(sys.argv[1])
            xbmc.log('------------------------- NAKA PLAYAER PLAy-------------------', xbmc.LOGINFO)
            if handle == -1:
                player.play(item=url_for_player, listitem=item)
            else:
                # thanks to anxdpanic for pointing in right direction
                xbmcplugin.setResolvedUrl(handle, True, item)
        except Exception as e:
            xbmc.log('ERROR NAKA PLAYAER---------------------------', xbmc.LOGINFO)
            xbmc.log(f'{e}', xbmc.LOGINFO)

        # leave player alive so we can handle onPlayBackStopped/onPlayBackEnded
        # TODO Move the instance to Service, so that it is never disposed
        xbmc.sleep(int(plugin_addon.getSetting('player_sleep')))
        return player_loop(player, is_transcoded, is_finished, ep_id, party_mode)


def player_loop(player, is_transcoded, is_transcode_finished, ep_id, party_mode):
    try:
        monitor = xbmc.Monitor()

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
                    xbmc.executeJSONRPC(
                        '{"jsonrpc":"2.0","method":"Player.Seek","params":{"playerid":1,"value":{"seconds":0}},"id":1}')

        while player.PlaybackStatus != PlaybackStatus.STOPPED and player.PlaybackStatus != PlaybackStatus.ENDED:
            xbmc.sleep(500)

        if player.PlaybackStatus == PlaybackStatus.STOPPED or player.PlaybackStatus == PlaybackStatus.ENDED:
            #log('Playback Ended - Shutting Down: ', monitor.abortRequested())

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
            #log('Playback Ended - Playback status was not "Stopped" or "Ended". It was ', player.PlaybackStatus)
            pass
        return 0
    except:
        #eh.exception(ErrorPriority.HIGHEST)
        return -1


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
        #spam('Player Initialized')
        xbmc.Player.__init__(self)
        self._t = None  # trakt thread
        self._s = None  # shoko thread
        self._u = None  # update thread
        self._details = None
        self.Playlist = None
        self.PlaybackStatus = PlaybackStatus.STOPPED
        # self.LoopStatus = 'None'
        # self.Shuffle = False
        self.is_transcoded = False
        self.is_movie = None
        self.file_id = 0
        self.ep_id = 0
        # we will store duration and time in kodi format here, so that calls to the player will match
        self.duration = 0
        self.time = 0
        self.path = ''
        self.scrobble = True
        self.is_external = False
        self.is_finished = False
        self.party_mode = False

        self.CanControl = True

    def reset(self):
        #spam('Player reset')
        self.__init__()

    def feed(self, file_id, ep_id, duration, path, scrobble):
        #spam('Player feed - file_id=%s ep_id=%s duration=%s path=%s scrobble=%s' % (file_id, ep_id, duration, path, scrobble))
        self.file_id = file_id
        self.ep_id = ep_id
        self.duration = duration # kodi_proxy.duration_to_kodi(duration)
        self.path = path
        self.scrobble = scrobble

    def onAVStarted(self):
        # Will be called when Kodi has a video or audiostream, before playing file
        #spam('onAVStarted')

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
        # Will be called when Kodi has a video, audio or subtitle stream. Also happens when the stream changes.
        #spam('onAVChange')
        pass

    def onPlayBackStarted(self):
        #spam('Playback Started')
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
        #spam('Playback Resumed')
        self.PlaybackStatus = PlaybackStatus.PLAYING
        try:
            self.start_loops()
        except:
            #eh.exception(ErrorPriority.HIGH)
            pass

    def start_loops(self):
        #spam('start_loops')
        try:
            self._t.stop()
        except:
            pass
        self._t = Thread(target=self.tick_loop_trakt, args=())
        self._t.daemon = True
        self._t.start()

        try:
            self._s.stop()
        except:
            pass
        self._s = Thread(target=self.tick_loop_shoko, args=())
        self._s.daemon = True
        self._s.start()

        try:
            self._u.stop()
        except:
            pass
        self._u = Thread(target=self.tick_loop_update_time, args=())
        self._u.daemon = True
        self._u.start()

    def onPlayBackStopped(self):
        #spam('Playback Stopped')
        try:
            self.handle_finished_episode()
        except:
            #eh.exception(ErrorPriority.HIGH)
            pass
        self.PlaybackStatus = PlaybackStatus.STOPPED

    def onPlayBackEnded(self):
        #spam('Playback Ended')
        try:
            self.handle_finished_episode()
        except:
            #eh.exception(ErrorPriority.HIGH)
            pass
        self.PlaybackStatus = PlaybackStatus.ENDED

    def onPlayBackPaused(self):
        #spam('Playback Paused')
        self.PlaybackStatus = PlaybackStatus.PAUSED
        self.scrobble_time()

    def onPlayBackSeek(self, time_to_seek, seek_offset):
        #log('Playback Paused - time_to_seek=%s seek_offset=%s' % (time_to_seek, seek_offset))
        self.time = self.getTime()
        self.scrobble_time()

    def set_duration(self):
        try:
            if self.duration != 0:
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
            #eh.exception(ErrorPriority.HIGH)
            pass

    def tick_loop_trakt(self):
        if not self.scrobble:
            return
        while True:
            if self.PlaybackStatus == PlaybackStatus.PLAYING and self.isPlayingVideo():
                try:
                    scrobble_trakt(self.ep_id, 1, self.time, self.duration, self.is_movie)
                except:
                    pass
                xbmc.sleep(2500)

    def tick_loop_shoko(self):
        if not self.scrobble:
            return
        while True:
            if self.PlaybackStatus == PlaybackStatus.PLAYING and self.isPlayingVideo():
                try:
                    if plugin_addon.getSetting('file_resume') == 'true' and self.time > 10:
                        #from shoko_models.v2 import File
                        #f = File(self.file_id)
                        #f.set_resume_time(kodi_proxy.duration_from_kodi(self.time))
                        pass
                except:
                    pass
                xbmc.sleep(2500)

    def tick_loop_update_time(self):
        while True:
            if self.PlaybackStatus == PlaybackStatus.PLAYING and self.isPlayingVideo():
                try:
                    # Leia seems to have a bug where calling self.getTotalTime() fails at times
                    # Try until it succeeds
                    self.set_duration()

                    if not self.is_external:
                        self.time = self.getTime()
                    else:
                        self.time += 1
                except:
                    pass  # while buffering
                xbmc.sleep(1000)  # wait 1sec

    def handle_finished_episode(self):
        self.Playlist = None

        if self.scrobble:
            scrobble_trakt(self.ep_id, 3, self.time, self.duration, self.is_movie)

        if self.is_transcoded:
            #pyproxy.get_json(trancode_url(self.file_id) + '/cancel')
            pass

        self.is_finished = finished_episode(self.ep_id, self.file_id, self.time, self.duration)
