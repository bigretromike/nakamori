#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
this is main file that will execute on entering add-on
this should be minimal as possible
anything that build/create lists/dialogs (based on xbmcgui) should go to guibuilder
anything else should go to util
"""

from __future__ import absolute_import, division, unicode_literals

import resources.lib.debug as dbg
import resources.lib.guibuilder as gb
import resources.lib.search as search
import resources.lib.util as util

import nakamoritools as nt

import xbmcplugin
import xbmcaddon
import xbmcgui
import xbmc

import sys

if sys.version_info < (3, 0):
    # noinspection PyCompatibility
    from urllib2 import HTTPError
else:
    # For Python 3.0 and later
    # noinspection PyUnresolvedReferences,PyCompatibility
    from urllib.error import HTTPError

dbg.debug_init()

util.detect_kodi18()

util.wizard()

if nt.get_shoko_status() is True:
    try:
        if nt.valid_user() is True:
            try:
                parameters = nt.parse_parameters(sys.argv[2])
            except Exception as exp:
                nt.error('valid_userid_1 parse_parameters() util.error', str(exp))
                parameters = {'mode': 2}

            mode = None
            if parameters:
                try:
                    if 'mode' in parameters:
                        mode = int(parameters['mode'])
                except Exception as exp:
                    nt.error('valid_userid set \'mode\' util.error', str(exp) + " parameters: " + str(parameters))

            try:
                if 'cmd' in parameters:
                    cmd = parameters['cmd']
                else:
                    cmd = None
            except Exception as exp:
                nt.error('valid_userid_2 parse_parameters() util.error', str(exp))
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
                    # noinspection PyTypeChecker
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
                elif cmd == 'mediainfo':
                    util.mediainfo_update()
                elif cmd == 'statsupdate':
                    util.stats_update()
                elif cmd == 'folderlist':
                    util.folder_list()
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
                        if util.play_video(parameters['ep_id'],
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
                            xbmcplugin.setContent(int(gb.handle), str('movies'))
                            gb.execute_search_and_add_query()
                    except:
                        gb.build_search_directory()
                elif mode == 4:  # Group/Serie
                    try:
                        if dbg.has_line_profiler:
                            # noinspection PyUnresolvedReferences
                            profiler = dbg.line_profiler.LineProfiler()
                            profiler.add_function(gb.build_groups_menu)
                            profiler.enable_by_count()
                        gb.build_groups_menu(parameters)
                    finally:
                        if dbg.has_line_profiler:
                            # noinspection PyUnboundLocalVariable
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
                    # noinspection PyTypeChecker
                    xbmcaddon.Addon(id='plugin.video.nakamori').openSettings()
                elif mode == 12:  # Settings
                    gb.build_shoko_menu()
                elif mode == 31:  # Clear Search History
                    search.clear_search_history(parameters)
                else:
                    # starting point
                    gb.build_filters_menu()
        else:
            nt.error(nt.addon.getLocalizedString(30194), nt.addon.getLocalizedString(30195))
    except HTTPError as err:
        if err.code == 401:
            gb.build_network_menu()
else:
    nt.addon.setSetting(id='wizard', value='0')
    gb.build_network_menu()
