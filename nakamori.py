#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import resources.lib.debug as dbg
import resources.lib.guibuilder as gb
import resources.lib.search as search
import resources.lib.util as util

import nakamoritools as nt
from Calendar import Wizard

import xbmcplugin
import xbmcaddon
import xbmcgui
import xbmc

import sys
import os

if sys.version_info < (3, 0):
    from urllib2 import HTTPError
else:
    # For Python 3.0 and later
    # noinspection PyUnresolvedReferences
    from urllib.error import HTTPError


def play_video(ep_id, raw_id, movie):
    """
    Plays a file or episode
    Args:
        ep_id: episode id, if applicable for watched status and stream details
        raw_id: file id, that is only used when ep_id = 0
        movie: determinate if played object is movie or episode (ex.Trakt)
    Returns:

    """
    details = {
        'plot':          xbmc.getInfoLabel('ListItem.Plot'),
        'title':         xbmc.getInfoLabel('ListItem.Title'),
        'sorttitle':     xbmc.getInfoLabel('ListItem.Title'),
        'rating':        xbmc.getInfoLabel('ListItem.Rating'),
        'duration':      xbmc.getInfoLabel('ListItem.Duration'),
        'mpaa':          xbmc.getInfoLabel('ListItem.Mpaa'),
        'year':          xbmc.getInfoLabel('ListItem.Year'),
        'tagline':       xbmc.getInfoLabel('ListItem.Tagline'),
        'episode':       xbmc.getInfoLabel('ListItem.Episode'),
        'aired':         xbmc.getInfoLabel('ListItem.Premiered'),
        'tvshowtitle':   xbmc.getInfoLabel('ListItem.TVShowTitle'),
        'votes':         xbmc.getInfoLabel('ListItem.Votes'),
        'originaltitle': xbmc.getInfoLabel('ListItem.OriginalTitle'),
        'size':          xbmc.getInfoLabel('ListItem.Size'),
        'season':        xbmc.getInfoLabel('ListItem.Season'),
    }

    file_id = ''
    file_url = ''
    file_body = None
    offset = 0
    item = ''

    try:
        if ep_id != "0":
            episode_url = nt.server + "/api/ep?id=" + str(ep_id)
            episode_url = nt.set_parameter(episode_url, "level", "1")
            html = nt.get_json(nt.encode(episode_url))
            if nt.addon.getSetting("spamLog") == "true":
                xbmc.log(html, xbmc.LOGWARNING)
            episode_body = nt.json.loads(html)
            if nt.addon.getSetting("pick_file") == "true":
                file_id = util.file_list_gui(episode_body)
            else:
                file_id = episode_body["files"][0]["id"]
        else:
            file_id = raw_id

        if file_id is not None and file_id != 0:
            file_url = nt.server + "/api/file?id=" + str(file_id)
            file_body = nt.json.loads(nt.get_json(file_url))

            file_url = file_body['url']
            serverpath = file_body.get('server_path', '')
            if serverpath is not None and serverpath != '':
                try:
                    if os.path.isfile(serverpath):
                        if nt.python_two:
                            if unicode(serverpath).startswith('\\\\'):
                                serverpath = "smb:"+serverpath
                        else:
                            if serverpath.startswith('\\\\'):
                                serverpath = "smb:"+serverpath
                        file_url = serverpath
                except:
                    pass

            # Information about streams inside video file
            # Video
            codecs = dict()
            util.video_file_information(file_body["media"], codecs)

            details['duration'] = file_body.get('duration', 0)
            details['size'] = file_body['size']

            item = xbmcgui.ListItem(details.get('title', 'Unknown'),
                                    thumbnailImage=xbmc.getInfoLabel('ListItem.Thumb'),
                                    path=file_url)
            item.setInfo(type='Video', infoLabels=details)

            # item.setProperty('IsPlayable', 'true')

            if 'offset' in file_body:
                offset = file_body.get('offset', 0)
                if offset != 0:
                    offset = int(offset) / 1000
                    item.setProperty('ResumeTime', str(offset))

            for stream_index in codecs["VideoStreams"]:
                if not isinstance(codecs["VideoStreams"][stream_index], dict):
                    continue
                item.addStreamInfo('video', codecs["VideoStreams"][stream_index])
            for stream_index in codecs["AudioStreams"]:
                if not isinstance(codecs["AudioStreams"][stream_index], dict):
                    continue
                item.addStreamInfo('audio', codecs["AudioStreams"][stream_index])
            for stream_index in codecs["SubStreams"]:
                if not isinstance(codecs["SubStreams"][stream_index], dict):
                    continue
                item.addStreamInfo('subtitle', codecs["SubStreams"][stream_index])
        else:
            if nt.addon.getSetting("pick_file") == "false":
                nt.error("file_id not retrieved")
            return 0
    except Exception as exc:
        nt.error('util.error getting episode info', str(exc))

    is_transcoded = False
    player = xbmc.Player()

    try:
        # region Eigakan
        if nt.addon.getSetting("enableEigakan") == "true":
            eigakan_url = nt.addon.getSetting("ipEigakan")
            eigakan_port = nt.addon.getSetting("portEigakan")
            eigakan_host = 'http://' + eigakan_url + ':' + eigakan_port
            video_url = eigakan_host + '/api/transcode/' + str(file_id)
            post_data = '"file":"' + file_url + '"'
            try_count = 0
            m3u8_url = eigakan_host + '/api/video/' + str(file_id) + '/play.m3u8'
            ts_url = eigakan_host + '/api/video/' + str(file_id) + '/play0.ts'

            try:
                eigakan_data = nt.get_json(eigakan_host + '/api/version')
                if 'eigakan' in eigakan_data:
                    audio_stream_id = -1
                    stream_index = -1
                    for audio_code in nt.addon.getSetting("audiolangEigakan").split(","):
                        for audio_stream in file_body['media']['audios']:
                            stream_index += 1
                            if 'Language' in file_body['media']['audios'][audio_stream]:
                                if audio_code in file_body['media']['audios'][audio_stream].get('Language').lower():
                                    audio_stream_id = stream_index
                                    break
                            if 'LanguageCode' in file_body['media']['audios'][audio_stream]:
                                if audio_code in file_body['media']['audios'][audio_stream].get('LanguageCode').lower():
                                    audio_stream_id = stream_index
                                    break
                            if 'Title' in file_body['media']['audios'][audio_stream]:
                                if audio_code in file_body['media']['audios'][audio_stream].get('Language').lower():
                                    audio_stream_id = stream_index
                                    break
                        if audio_stream_id != -1:
                            break

                    sub_stream_id = -1
                    stream_index = -1
                    for sub_code in nt.addon.getSetting("subEigakan").split(","):
                        for sub_stream in file_body['media']['subtitles']:
                            stream_index += 1
                            if 'Language' in file_body['media']['subtitles'][sub_stream]:
                                if sub_code in file_body['media']['subtitles'][sub_stream].get('Language').lower():
                                    sub_stream_id = stream_index
                                    break
                            if 'LanguageCode' in file_body['media']['subtitles'][sub_stream]:
                                if sub_code in file_body['media']['subtitles'][sub_stream].get('LanguageCode').lower():
                                    sub_stream_id = stream_index
                                    break
                            if 'Title' in file_body['media']['subtitles'][sub_stream]:
                                if sub_code in file_body['media']['subtitles'][sub_stream].get('Language').lower():
                                    sub_stream_id = stream_index
                                    break
                        if sub_stream_id != -1:
                            break

                    gb.busy.create(nt.addon.getLocalizedString(30160), nt.addon.getLocalizedString(30165))

                    if audio_stream_id != -1:
                        post_data += ',"audio_stream":"' + str(audio_stream_id) + '"'
                    if sub_stream_id != -1:
                        post_data += ',"subtitles_stream":"' + str(sub_stream_id) + '"'

                    if nt.addon.getSetting("advEigakan") == "true":
                        post_data += ',"resolution":"' + nt.addon.getSetting("resolutionEigakan") + '"'
                        post_data += ',"audio_codec":"' + nt.addon.getSetting("audioEigakan") + '"'
                        post_data += ',"video_bitrate":"' + nt.addon.getSetting("vbitrateEigakan") + '"'
                        post_data += ',"x264_profile":"' + nt.addon.getSetting("profileEigakan") + '"'
                    nt.post_json(video_url, post_data)
                    xbmc.sleep(1000)
                    gb.busy.close()

                    gb.busy.create(nt.addon.getLocalizedString(30160), nt.addon.getLocalizedString(30164))
                    while True:
                        if nt.head(url_in=ts_url) is False:
                            x_try = int(nt.addon.getSetting("tryEigakan"))
                            if try_count > x_try:
                                break
                            if gb.busy.iscanceled():
                                break
                            try_count += 1
                            gb.busy.update(try_count)
                            xbmc.sleep(1000)
                        else:
                            break
                    gb.busy.close()

                    postpone_seconds = int(nt.addon.getSetting("postponeEigakan"))
                    if postpone_seconds > 0:
                        gb.busy.create(nt.addon.getLocalizedString(30160), nt.addon.getLocalizedString(30166))
                        while postpone_seconds > 0:
                            xbmc.sleep(1000)
                            postpone_seconds -= 1
                            gb.busy.update(postpone_seconds)
                            if gb.busy.iscanceled():
                                break
                        gb.busy.close()

                    if nt.head(url_in=ts_url):
                        is_transcoded = True
                        player.play(item=m3u8_url, startpos=-1)
                else:
                    nt.error("Eigakan server is unavailable")
            except Exception as exc:
                nt.error('eigakan.post_json error', str(exc))
                gb.busy.close()
        # endregion
        else:
            player.play(item=file_url, listitem=item)

        if not is_transcoded:
            if nt.addon.getSetting("file_resume") == "true":
                if offset > 0:
                    for i in range(0, 1000):  # wait up to 10 secs for the video to start playing before we try to seek
                        if not player.isPlayingVideo():  # and not xbmc.abortRequested:
                            xbmc.sleep(100)
                        else:
                            xbmc.Player().seekTime(offset)
                            xbmc.log("-----player: seek_time offset:" + str(offset), xbmc.LOGNOTICE)
                            break

    except Exception as player_ex:
        xbmc.log(str(player_ex), xbmc.LOGWARNING)
        pass

    # wait for player (network issue etc)
    xbmc.sleep(1000)
    mark = float(nt.addon.getSetting("watched_mark"))
    mark /= 100
    file_fin = False
    trakt_404 = False
    # hack for slow connection and buffering time
    xbmc.sleep(int(nt.addon.getSetting("player_sleep")))

    try:
        if raw_id == "0":  # skip for raw_file
            progress = 0
            while player.isPlaying():
                try:

                    xbmc.sleep(2500)  # 2.5sec this will make the server handle it better
                    if is_transcoded:
                        total_time = details['duration']
                    else:
                        total_time = player.getTotalTime()
                    current_time = player.getTime()

                    # region Resume support (work with shoko 3.6.0.7+)
                    # don't sync until the files is playing and more than 10 seconds in
                    # we'll sync the offset if it's set to sync watched states, and leave file_resume to auto resuming
                    if nt.addon.getSetting("syncwatched") == "true" and current_time > 10:
                        nt.sync_offset(file_id, current_time)
                    # endregion

                    # region Trakt support
                    # endregion

                    if (total_time * mark) < current_time:
                        file_fin = True
                    if not player.isPlaying():
                        break
                except:
                    xbmc.sleep(60)
                    if not trakt_404:
                        # send 'pause' to trakt
                        nt.json.loads(nt.get_json(nt.server + "/api/ep/scrobble?id=" + str(ep_id) +
                                            "&ismovie=" + str(movie) +
                                            "&status=" + str(2) +
                                            "&progress=" + str(progress)))
                    break

            if is_transcoded:
                nt.get_json(video_url + '/cancel')
    except Exception as ops_ex:
        nt.dbg(ops_ex)
        pass

    if raw_id == "0":  # skip for raw_file
        no_watch_status = False
        if nt.addon.getSetting('no_mark') != "0":
            no_watch_status = True
            # reset no_mark so next file will mark watched status
            nt.addon.setSetting('no_mark', '0')

        if file_fin is True:
            if no_watch_status is False:
                return ep_id
    return 0


# region Setting up Remote Debug
if nt.addon.getSetting('remote_debug') == 'true':
    try:
        if dbg.has_pydev:
            dbg.pydevd.settrace(nt.addon.getSetting('ide_ip'), port=int(nt.addon.getSetting('ide_port')),
                                stdoutToServer=True, stderrToServer=True, suspend=False)
        else:
            nt.error('pydevd not found, disabling remote_debug')
            nt.addon.setSetting('remote_debug', 'false')
    except Exception as ex:
        nt.error('Unable to start debugger, disabling', str(ex))
        nt.addon.setSetting('remote_debug', 'false')
# endregion

# Script run from here

if nt.addon.getSetting('spamLog') == "true":
    nt.dump_dictionary(sys.argv, 'sys.argv')

# 3 is not checked
if nt.addon.getSetting('kodi18') == '3':
    python = xbmcaddon.Addon('xbmc.addon')
    if python is not None:
        # kodi18 return 17.9.701 as for now
        if str(python.getAddonInfo('version')) == '17.9.701':
            nt.addon.setSetting(id='kodi18', value='1')
        else:
            nt.addon.setSetting(id='kodi18', value='0')

if nt.addon.getSetting('wizard') == '0':
    wizard = Wizard(nt.addon.getLocalizedString(30082))
    wizard.doModal()
    if wizard.setup_ok:
        nt.addon.setSetting(id='wizard', value='1')
    del wizard

if nt.get_server_status(ip=nt.addon.getSetting('ipaddress'), port=nt.addon.getSetting('port')) is True:
    try:
        if nt.valid_user() is True:
            try:
                parameters = nt.parseParameters(sys.argv[2])
            except Exception as exp:
                nt.error('valid_userid_1 parseParameters() util.error', str(exp))
                parameters = {'mode': 2}

            if parameters:
                try:
                    mode = int(parameters['mode'])
                except Exception as exp:
                    nt.error('valid_userid set \'mode\' util.error', str(exp) + " parameters: " + str(parameters))
                    mode = None
            else:
                mode = None

            try:
                if 'cmd' in parameters:
                    cmd = parameters['cmd']
                else:
                    cmd = None
            except Exception as exp:
                nt.error('valid_userid_2 parseParameters() util.error', str(exp))
                cmd = None
            if cmd is not None:
                if cmd == "voteSer":
                    nt.vote_series(parameters['serie_id'])
                elif cmd == "voteEp":
                    nt.vote_episode(parameters['ep_id'])
                elif cmd == "viewCast":
                    gb.build_cast_menu(parameters)
                elif cmd == "searchCast":
                    gb.search_for(parameters.get('url', ''))
                elif cmd == "watched":
                    if nt.get_kodi_setting_int('videolibrary.tvshowsselectfirstunwatcheditem') == 0 or \
                            nt.addon.getSetting("select_unwatched") == "true":
                        try:
                            win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
                            ctl = win.getControl(win.getFocusId())
                            # noinspection PyTypeChecker
                            ui_index = parameters.get('ui_index', '')
                            if ui_index != '':
                                nt.move_position_on_list(ctl, int(ui_index) + 1)
                        except Exception as exp:
                            xbmc.log(str(exp), xbmc.LOGWARNING)
                            pass
                    parameters['watched'] = True
                    nt.mark_watch_status(parameters)
                    if nt.addon.getSetting("vote_always") == "true":
                        if parameters.get('userrate', 0) == 0:
                            nt.vote_episode(parameters['ep_id'])
                elif cmd == "unwatched":
                    parameters['watched'] = False
                    nt.mark_watch_status(parameters)
                elif cmd == "playlist":
                    util.play_continue_item()
                elif cmd == "no_mark":
                    nt.addon.setSetting('no_mark', '1')
                    xbmc.executebuiltin('Action(Select)')
                elif cmd == "pickFile":
                    if str(parameters['ep_id']) != "0":
                        ep_url = nt.server + "/api/ep?id=" + str(parameters['ep_id']) + "&level=2"
                        util.file_list_gui(nt.json.loads(nt.get_json(ep_url)))
                elif cmd == 'rescan':
                    util.rescan_file(parameters, True)
                elif cmd == 'rehash':
                    util.rescan_file(parameters, False)
                elif cmd == 'missing':
                    util.remove_missing_files()
                elif cmd == 'createPlaylist':
                    gb.create_playlist(parameters['serie_id'])
                elif cmd == 'refresh':
                    nt.refresh()
            else:
                if mode == 0:  # string label
                    pass
                elif mode == 1:  # play_file
                    try:
                        win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
                        ctl = win.getControl(win.getFocusId())
                        if play_video(parameters['ep_id'],
                                      parameters['raw_id'] if 'raw_id' in parameters else "0",
                                      parameters['movie'] if 'movie' in parameters else 0) > 0:
                            # noinspection PyTypeChecker
                            ui_index = parameters.get('ui_index', '')
                            if ui_index != '':
                                nt.move_position_on_list(ctl, int(ui_index) + 1)
                            parameters['watched'] = True
                            nt.mark_watch_status(parameters)
                    except Exception as exp:
                        xbmc.log(str(exp), xbmc.LOGWARNING)
                        pass
                elif mode == 2:  # DIRECTORY
                    xbmcgui.Dialog().ok('MODE=2', 'MODE')
                elif mode == 3:  # Search
                    try:
                        if parameters['extras'] == "force-search" and 'query' in parameters:
                            url = nt.server + '/api/search'
                            url = nt.set_parameter(url, 'query', parameters['query'])
                            gb.search_for(url)
                        else:
                            xbmcplugin.setContent(int(gb.handle), "movies")
                            gb.execute_search_and_add_query()
                    except:
                        gb.build_search_directory()
                elif mode == 4:  # Group/Serie
                    try:
                        if dbg.has_line_profiler:
                            profiler = dbg.line_profiler.LineProfiler()
                            profiler.add_function(gb.build_groups_menu)
                            profiler.enable_by_count()
                            gb.build_groups_menu(parameters)
                    finally:
                        if dbg.has_line_profiler:
                            profiler.print_stats(open('stats.txt', 'w'))
                elif mode == 5:  # Serie EpisodeTypes (episodes/ovs/credits)
                    gb.build_serie_episodes_types(parameters)
                elif mode == 6:  # Serie Episodes (list of episodes)
                    gb.build_serie_episodes(parameters)
                elif mode == 7:  # Playlist -continue-
                    util.play_continue_item()
                elif mode == 8:  # File List
                    gb.build_raw_list(parameters)
                elif mode == 9:  # Calendar
                    gb.build_serie_soon(parameters)
                elif mode == 10:  # newCalendar
                    gb.build_serie_soon_new(parameters)
                elif mode == 11:  # Settings
                    xbmcaddon.Addon(id='plugin.video.nakamori').openSettings()
                elif mode == 31:  # Clear Search History
                    search.clear_search_history(parameters)
                else:
                    gb.build_filters_menu()
        else:
            nt.error(nt.addon.getLocalizedString(30194), nt.addon.getLocalizedString(30195))
    except HTTPError as err:
        if err.code == 401:
            gb.build_network_menu()
else:
    nt.addon.setSetting(id='wizard', value='0')
    gb.build_network_menu()

if nt.addon.getSetting('remote_debug') == 'true':
    try:
        if dbg.has_pydev:
            dbg.pydevd.stoptrace()
    except Exception as remote_exc:
        xbmc.log(str(remote_exc), xbmc.LOGWARNING)
        pass
