# -*- coding: utf-8 -*-
import lib.windows.ac_calendar
from lib import kodi_utils
from lib import shoko_utils
from lib import naka_player
from lib.addon_utils import plugin
from lib.naka_utils import ThisType, map_episodetype_int_to_thistype
from models import kodi_models
from sys import argv
from lib.windows import wizard
import xbmc
import xbmcgui
from xbmcgui import ListItem
import xbmcaddon
from xbmcplugin import addDirectoryItem, endOfDirectory, addDirectoryItems

import lib.search as search
import lib.favorite as favorite
from operator import itemgetter
import string

plugin_addon = xbmcaddon.Addon(id='plugin.video.nakamori')


# TODO  this is setthing inside Shoko that will Group Series into parent Groups (ex. Monogatari-Series)
do_we_want_to_make_eptype_setting = plugin_addon.getSettingBool('show_eptypes')


@plugin.route('/')
def list_all_filters():
    """
    List all Filters for current User
    :return: Draw ListItem's Collection of Filters
    """

    if not plugin_addon.getSettingBool('skip_information'):
        # spot for 'what's new window'
        # also let's flag this information in sqlite version, mark
        pass

    kodi_models.set_sorting_method(ThisType.filter)
    y = kodi_models.list_all_filters()
    x = kodi_models.main_menu_items()
    for extra in x:
        y.append((0, ThisType.menu, extra, kodi_models.remove_markdown(extra.getLabel())))
    y_count = len(y)
    # sort them by name
    y.sort(key=itemgetter(3))

    for filter_id, f_type, li, label in y:
        if label == "Tags":
            li.setArt({
                'fanart': f'{kodi_models.plugin_img_path}/backgrounds/tags.png',
                'banners': f'{kodi_models.plugin_img_path}/banners/tags.png',
                'poster': f'{kodi_models.plugin_img_path}/icons/tags.png',
                'icon': f'{kodi_models.plugin_img_path}/icons/tags.png'
            })
        elif label == "Years":
            li.setArt({
                'fanart': f'{kodi_models.plugin_img_path}/backgrounds/years.png',
                'banners': f'{kodi_models.plugin_img_path}/banners/years.png',
                'poster': f'{kodi_models.plugin_img_path}/icons/years.png',
                'icon': f'{kodi_models.plugin_img_path}/icons/years.png'
            })
        elif label == "Seasons":
            li.setArt({
                'fanart': f'{kodi_models.plugin_img_path}/backgrounds/seasons.png',
                'banners': f'{kodi_models.plugin_img_path}/banners/seasons.png',
                'poster': f'{kodi_models.plugin_img_path}/icons/seasons.png',
                'icon': f'{kodi_models.plugin_img_path}/icons/seasons.png'
            })
        if f_type == ThisType.filter:
            addDirectoryItem(plugin.handle, plugin.url_for(list_groups_by_filter_id, filter_id), li, True, totalItems=y_count)
        elif f_type == ThisType.filters:
            addDirectoryItem(plugin.handle, plugin.url_for(list_filter_by_filters_id, filter_id), li, True, totalItems=y_count)
        elif f_type == ThisType.menu:
            addDirectoryItem(plugin.handle, li.getPath(), li, True, totalItems=y_count)

    endOfDirectory(plugin.handle, cacheToDisc=False)


@plugin.route('/fs-<filters_id>')
def list_filter_by_filters_id(filters_id: int):
    kodi_models.set_content('tvshows')
    kodi_models.set_sorting_method(ThisType.filter)
    y = kodi_models.list_all_filter_by_filters_id(filters_id)
    y_count = len(y)
    for obj_id, obj_type, li in y:
        if obj_type == ThisType.filter:
            addDirectoryItem(plugin.handle, plugin.url_for(list_groups_by_filter_id, obj_id), li, True, totalItems=y_count)
        if obj_type == ThisType.filters:
            addDirectoryItem(plugin.handle, plugin.url_for(list_filter_by_filters_id, obj_id), li, True, totalItems=y_count)

    endOfDirectory(plugin.handle, cacheToDisc=False)


@plugin.route('/f-<filter_id>')
def list_groups_by_filter_id(filter_id: int):
    """
    List all Groups for current User in Filter
    :param filter_id: ID of Filter that we want list content of
    :return: Draw ListItem's Collection of Group
    """
    kodi_models.set_content('tvshows')

    if int(filter_id) == 0:
        list_unsorted()
        return
    kodi_models.set_sorting_method(ThisType.series)
    y = kodi_models.list_all_groups_by_filter_id(filter_id)
    y_count = len(y)
    for obj_id, obj_type, li in y:
        if obj_type == ThisType.group:
            addDirectoryItem(plugin.handle, plugin.url_for(open_group_by_group_id_and_filter_id, filter_id, obj_id), li, True, totalItems=y_count)
        if obj_type == ThisType.series:
            addDirectoryItem(plugin.handle, plugin.url_for(open_series_by_series_id_and_filter_id, filter_id, obj_id), li, True, totalItems=y_count)

    endOfDirectory(plugin.handle, cacheToDisc=False)


@plugin.route('/f-<filter_id>/g-<group_id>')
def open_group_by_group_id_and_filter_id(filter_id: int, group_id: int):
    kodi_models.set_content('tvshows')
    kodi_models.set_sorting_method(ThisType.series)
    y = kodi_models.list_all_series_by_group_id(group_id)
    y_count = len(y)
    for obj_id, li in y:
        addDirectoryItem(plugin.handle, plugin.url_for(open_series_by_series_id_and_filter_id, filter_id, obj_id), li, True, totalItems=y_count)
    endOfDirectory(plugin.handle, cacheToDisc=False)


@plugin.route('/f-<filter_id>/s-<series_id>')
def open_series_by_series_id_and_filter_id(filter_id: int, series_id: int):
    list_of_ep_types = []
    list_of_eps = []

    _e, s = kodi_models.list_episodes_for_series_by_series_id(series_id)

    for e in _e:
        list_of_eps.append(e)

    for ep_id, ep_type, li in list_of_eps:
        if ep_type not in list_of_ep_types:
            list_of_ep_types.append(ep_type)

    first_not_watched = -1
    list_items_to_add = []
    if len(list_of_ep_types) > 1 and do_we_want_to_make_eptype_setting:
        kodi_models.set_content('seasons')
        kodi_models.set_sorting_method(ThisType.tvepisodes)
        for ep_type in list_of_ep_types:
            li = kodi_models.get_listitem_from_episodetype(ep_type, s.art)
            addDirectoryItem(plugin.handle, plugin.url_for(open_eptype_by_eptype_by_series_id_and_filter_id, filter_id, series_id, int(ep_type)), li, True, totalItems=len(list_of_ep_types))
    else:
        kodi_models.set_content('episodes')
        kodi_models.set_sorting_method(ThisType.episodes)

        con = kodi_models.add_continue_item(series=s, episode_type=list_of_ep_types[0])

        _index = 0 if con is None else 1
        for ep_id, ep_type, li in list_of_eps:
            _index += 1
            if first_not_watched == -1 and li.getVideoInfoTag().getPlayCount() == 0:
                li.select(selected=True)
                first_not_watched = _index
            list_items_to_add.append((plugin.url_for(open_episode, filter_id, series_id, ep_id), li, False))

        if con is not None:
            _con = (plugin.url_for(move_to, first_not_watched), con, False)
            list_items_to_add.insert(0, _con)

        addDirectoryItems(plugin.handle, list_items_to_add)

    endOfDirectory(plugin.handle, cacheToDisc=False)
    if len(list_of_ep_types) == 1:
        kodi_utils.move_to(first_not_watched)


@plugin.route('/f-<filter_id>/s-<series_id>/et-<eptype_id>')
def open_eptype_by_eptype_by_series_id_and_filter_id(filter_id: int, series_id: int, eptype_id: int):
    kodi_models.set_content('episodes')

    kodi_models.set_sorting_method(ThisType.episodes)
    y, s = kodi_models.list_episodes_for_series_by_series_id(series_id)

    first_not_watched = -1
    con = kodi_models.add_continue_item(series=s, episode_type=map_episodetype_int_to_thistype(eptype_id))
    list_items_to_add = []
    _index = 0 if con is None else 1
    for ep_id, ep_type, li in y:
        if int(ep_type) == int(eptype_id):
            _index += 1
            if first_not_watched == -1 and li.getVideoInfoTag().getPlayCount() == 0:
                li.select(selected=True)
                first_not_watched = _index
            list_items_to_add.append((plugin.url_for(open_episode, filter_id, series_id, ep_id), li, False))

    if con is not None:
        _con = (plugin.url_for(move_to, first_not_watched), con, False)
        list_items_to_add.insert(0, _con)

    addDirectoryItems(plugin.handle, list_items_to_add)
    endOfDirectory(plugin.handle, cacheToDisc=False)
    kodi_utils.move_to(first_not_watched)


@plugin.route('/f-<filter_id>/s-<series_id>/e-<ep_id>-play/dontmark')
def open_episode_dont_mark(filter_id: int, series_id: int, ep_id: int):
    play_episode(filter_id, series_id, ep_id, False)


@plugin.route('/f-<filter_id>/s-<series_id>/e-<ep_id>-play')
def open_episode(filter_id: int, series_id: int, ep_id: int):
    kodi_utils.debug(f'open_episode: /f-{filter_id}/s-{series_id}/e-{ep_id}-play')
    play_episode(filter_id, series_id, ep_id, True)


def play_episode(filter_id: int, series_id: int, ep_id: int, use_watch_mark: bool):
    kodi_utils.debug(f'play_episode: {filter_id}, {series_id}, {ep_id}, {use_watch_mark}')
    is_resume_enable = plugin_addon.getSettingBool('file_resume')
    raw_files_list = kodi_models.get_file_id_from_ep_id(ep_id)
    file_id = 0
    if len(raw_files_list) == 1:
        file_id = raw_files_list[0].id
    else:
        if plugin_addon.getSettingBool('pick_file'):
            items = [kodi_models.get_file_name(x.filename) for x in raw_files_list]
            my_file = xbmcgui.Dialog().select(plugin_addon.getLocalizedString(30196), items)
            if my_file > -1:
                file_id = raw_files_list[my_file].id
            else:
                # cancel -1,0
                file_id = 0
        else:
            file_id = raw_files_list[0].id
    if file_id != 0:
        naka_player.play_video(file_id=file_id, ep_id=ep_id, s_id=series_id, force_direct_play=True, resume=is_resume_enable, mark_as_watched=use_watch_mark)


@plugin.route('/f-0/s-<series_id>/e-<ep_id>-pick')
def pick_file_and_play(series_id: int, ep_id: int):
    is_resume_enable = plugin_addon.getSettingBool('file_resume')
    raw_files_list = kodi_models.get_file_id_from_ep_id(ep_id)
    items = [kodi_models.get_file_name(x.filename) for x in raw_files_list]
    my_file = xbmcgui.Dialog().select(plugin_addon.getLocalizedString(30196), items)
    if my_file > -1:
        file_id = raw_files_list[my_file].id
    else:
        # cancel -1,0
        file_id = 0
    if file_id != 0:
        naka_player.play_video(file_id=file_id, ep_id=ep_id, s_id=series_id, force_direct_play=True, resume=is_resume_enable, mark_as_watched=True)


@plugin.route('/f-0/r-<file_id>-play')
def open_rawfile(file_id: int):
    naka_player.play_video(file_id=file_id, ep_id=0, s_id=0, force_direct_play=True)


def list_unsorted():
    kodi_models.set_category('Unsort')
    kodi_models.set_content('video')
    x = kodi_models.list_all_unsorted()
    x_count = len(x)
    for r_id, r in x:
        addDirectoryItem(plugin.handle, plugin.url_for(open_rawfile, r_id), r, False, totalItems=x_count)
    endOfDirectory(plugin.handle, cacheToDisc=False)


@plugin.route('/dialog/wizard/logout')
def logout_user_from_nakamori():
    xbmc.executebuiltin('ReplaceWindow("10000")')
    plugin_addon.setSettingString('apikey', 'set-new-apikey')
    # reset apikey
    pass


@plugin.route('/dialog/wizard/login')
def open_login_screen():
    xbmc.executebuiltin("Dialog.Close(all, true)")
    wizard.open_login_wizard()


@plugin.route('/dialog/wizard/connection')
def open_login_screen():
    xbmc.executebuiltin("Dialog.Close(all, true)")
    wizard.open_connection_wizard()


@plugin.route('/search')
def show_search_menu():
    kodi_models.set_content('tvshows')
    kodi_models.set_category(plugin_addon.getLocalizedString(30221))

    # A-Z search (no keyboard needed)
    li = ListItem(label=kodi_models.bold('A-Z'), offscreen=True)
    kodi_models.set_art(li, None, 'search.png')
    addDirectoryItem(plugin.handle, plugin.url_for(az_search), li, True)

    use_fuzzy = plugin_addon.getSettingBool('use_fuzzy_search')
    # Search
    if not use_fuzzy:
        li = ListItem(label=kodi_models.bold(plugin_addon.getLocalizedString(30224)), offscreen=True)
        kodi_models.set_art(li, None, 'new-search.png')
        addDirectoryItem(plugin.handle, plugin.url_for(new_search, True, False, False), li, True)

        li = ListItem(label=kodi_models.bold(plugin_addon.getLocalizedString(30224)) + " Tag", offscreen=True)
        kodi_models.set_art(li, None, 'new-search.png')
        addDirectoryItem(plugin.handle, plugin.url_for(new_search, True, False, True), li, True)

        li = ListItem(label=kodi_models.bold(plugin_addon.getLocalizedString(30225)), offscreen=True)
        kodi_models.set_art(li, None, 'new-search.png')
        addDirectoryItem(plugin.handle, plugin.url_for(new_search, False, False, False), li, True)

        li = ListItem(label=kodi_models.bold(plugin_addon.getLocalizedString(30225)) + ' Tag', offscreen=True)
        kodi_models.set_art(li, None, 'new-search.png')
        addDirectoryItem(plugin.handle, plugin.url_for(new_search, False, False, True), li, True)

    else:
        li = ListItem(label=kodi_models.bold(plugin_addon.getLocalizedString(30224) + " (Fuzzy)"), offscreen=True)
        kodi_models.set_art(li, None, 'new-search.png')
        addDirectoryItem(plugin.handle, plugin.url_for(new_search, True, True, False), li, True)

        li = ListItem(label=kodi_models.bold(plugin_addon.getLocalizedString(30224) + " Tag (Fuzzy)"), offscreen=True)
        kodi_models.set_art(li, None, 'new-search.png')
        addDirectoryItem(plugin.handle, plugin.url_for(new_search, True, True, True), li, True)

        li = ListItem(label=kodi_models.bold(plugin_addon.getLocalizedString(30225) + " (Fuzzy)"), offscreen=True)
        kodi_models.set_art(li, None, 'new-search.png')
        addDirectoryItem(plugin.handle, plugin.url_for(new_search, False, True, False), li, True)

        li = ListItem(label=kodi_models.bold(plugin_addon.getLocalizedString(30225) + " Tag (Fuzzy)"), offscreen=True)
        kodi_models.set_art(li, None, 'new-search.png')
        addDirectoryItem(plugin.handle, plugin.url_for(new_search, False, True, True), li, True)

    # draw search history we have saved
    search_history = search.get_search_history()
    search_count = len(search_history)
    for ss in search_history:
        query = ss[0]
        fuzziness = ss[1]
        taginess = ss[2]
        if len(query) == 0:
            continue
        fuzzy = ''
        if fuzziness == 1:
            fuzzy = ' [fuzzy]'
        tag = ''
        if taginess == 1:
            tag = 'tag:'
        item = ListItem(label=tag + query + fuzzy, offscreen=True)
        kodi_models.set_art(item, None, 'search.png')
        remove_item = (plugin_addon.getLocalizedString(30204), f'RunScript(plugin.video.nakamori, /dialog/search/{query}-{fuzziness}-{taginess}/remove)')
        item.addContextMenuItems([remove_item])

        addDirectoryItem(plugin.handle, plugin.url_for(search_for, query, fuzziness, taginess), item, True, totalItems=search_count)

    # add clear all for more than 10 items, no one wants to clear them one by one
    if len(search_history) > 10:
        li = ListItem(label=kodi_models.bold(plugin_addon.getLocalizedString(30224)), offscreen=True)
        kodi_models.set_art(li, None, 'new-search.png')
        addDirectoryItem(plugin.handle, plugin.url_for(url_clear_search_terms), li, False)

    endOfDirectory(plugin.handle, cacheToDisc=False)


@plugin.route('/search/<save>-<fuzzy>-<tag>')
def new_search(save: bool, fuzzy: bool, tag: bool):
    fuzziness = 1 if str(fuzzy).lower() == 'true' else 0
    taginess = 1 if str(tag).lower() == 'true' else 0
    query = kodi_models.search_box()
    if query != '':
        if str(save).lower() == "true":
            if search.check_in_database(query, fuzziness, taginess):
                search.remove_search_history(query, fuzziness, taginess)
            search.add_search_history(query, fuzziness, taginess)
        search_for(query, fuzzy, tag)
    else:
        show_search_menu()


@plugin.route('/menu-search/<query>-<fuzzy>-<tag>')
def search_for(query: str, fuzzy: bool, tag: bool):
    kodi_models.set_content('tvshows')
    kodi_models.set_category(query)

    fuzziness = True if str(fuzzy).lower() == 'true' else False
    taginess = True if str(tag).lower() == 'true' else False
    if len(query) > 0:
        list_of_s = kodi_models.show_search_result_menu(query, fuzziness, taginess)
        list_count = len(list_of_s)
        for s in list_of_s:
            addDirectoryItem(plugin.handle, plugin.url_for(open_series_by_series_id_and_filter_id, 0, s.id),
                             kodi_models.get_listitem_from_serie(s), True, totalItems=list_count)

        endOfDirectory(plugin.handle, cacheToDisc=False)


@plugin.route('/search/az')
def az_search():
    kodi_models.set_content('tvshows')
    kodi_models.set_content('A-Z')
    az_count = len(string.ascii_uppercase)
    for c in string.ascii_uppercase:
        item = ListItem(label=c, offscreen=True)
        kodi_models.set_art(item, None, 'search.png')
        addDirectoryItem(plugin.handle, plugin.url_for(az_search_for, c), item, True, totalItems=az_count)
    endOfDirectory(plugin.handle, cacheToDisc=False)


@plugin.route('/menu-search/az/<characters>')
def az_search_for(characters: str):
    kodi_models.set_content('tvshows')
    kodi_models.set_content('A-Z')

    # adding items to go "dir up" would make a backward loop while using backspace
    # TODO find a good way to go 3-5 levels up without later looping with backspace or '..' item

    ss = kodi_models.show_az_search_results(characters)
    list_count = len(ss)
    character_list = []
    for s in ss:
        _index = len(characters)
        if len(s.match) > _index:
            _new_char = s.match[_index].lower()
            if _new_char not in character_list:
                character_list.append(_new_char)
        addDirectoryItem(plugin.handle, plugin.url_for(open_series_by_series_id_and_filter_id, 0, s.id),
                         kodi_models.get_listitem_from_serie(s, s.match), True, totalItems=list_count)
    for new_char in character_list:
        item = ListItem(label=characters + new_char, offscreen=True)
        kodi_models.set_art(item, None, 'search.png')
        addDirectoryItem(plugin.handle, plugin.url_for(az_search_for, characters + new_char), item, True, totalItems=list_count)
    endOfDirectory(plugin.handle, cacheToDisc=False)


@plugin.route('/dialog/search/clear')
def url_clear_search_terms():
    search.clear_search_history()
    xbmc.executebuiltin('Container.Refresh')


@plugin.route('/dialog/search/<query>-<fuzzy>-<tag>/remove')
def url_remove_search_term(query, fuzzy, tag):
    search.remove_search_history(query, fuzzy, tag)
    xbmc.executebuiltin('Container.Refresh')


@plugin.route('/dialog/series/<series_id>/vote')
def vote_for_series(series_id):
    kodi_models.vote_for_series(int(series_id))


@plugin.route('/dialog/episode/vote/<ep_id>')
def vote_for_episode(ep_id):
    kodi_models.vote_for_episode(ep_id)


@plugin.route('/dialog/refresh')
def refresh_kodi():
    xbmc.executebuiltin('Container.Refresh')


@plugin.route('/favorites')
def show_favorites():
    kodi_models.set_content('tvshows')
    kodi_models.set_category(plugin_addon.getLocalizedString(30211))

    list_of_li = kodi_models.list_all_favorites()
    count_li = len(list_of_li)
    for s_id, li in list_of_li:
        remove_item = (plugin_addon.getLocalizedString(30213), f'RunScript(plugin.video.nakamori, /dialog/favorites/{s_id}/remove)')
        li.addContextMenuItems([remove_item])
        addDirectoryItem(plugin.handle, plugin.url_for(open_series_by_series_id_and_filter_id, 0, s_id), li, True, totalItems=count_li)
    endOfDirectory(plugin.handle, cacheToDisc=False)


@plugin.route('/dialog/favorites/<sid>/remove')
def remove_favorite(sid):
    favorite.remove_favorite(sid)
    favorite.add_favorite(sid)
    xbmc.executebuiltin('Notification(%s, %s, 7500, %s)' % (plugin_addon.getLocalizedString(30211),
                                                            plugin_addon.getLocalizedString(30213),
                                                            plugin_addon.getAddonInfo('icon')))
    xbmc.executebuiltin('Container.Refresh')


@plugin.route('/dialog/favorites/<sid>/add')
def add_favorite(sid):
    favorite.add_favorite(sid)
    xbmc.executebuiltin('Notification(%s, %s, 7500, %s)' % (plugin_addon.getLocalizedString(30211),
                                                            plugin_addon.getLocalizedString(30212),
                                                            plugin_addon.getAddonInfo('icon')))


@plugin.route('/shoko')
def show_shoko():
    # - AniDB                       (Folder)
    # - Import folders              (Folder)
    # - TvDB                        (Folder)
    # - MovieDB                     (Folder)
    # - Images                      (Folder)
    # - Trakt                       (Folder)
    # - AVDump mismatched files     (item) apiv3.avdump_mismatched_files
    # - Recreate all groups         (item) apiv3.recreate_all_groups
    # - Sync hashes                 (item) apiv2.sync_hashes (apiv3.sync_hashes always returns BadRequest)
    # - Update all mediainfo        (item) apiv3.update_all_mediainfo
    # - Update series stats         (item) apiv3.update_series_stats

    # kodi_models.set_content('tvshows')
    # set category to '.. / Shoko'
    kodi_models.set_category(plugin_addon.getLocalizedString(30115))

    list_item_art = {
        'poster': f'{kodi_models.plugin_img_path}/icons/command.png',
        'icon': f'{kodi_models.plugin_img_path}/icons/command.png'
    }

    avdump_mismatched_files_li = xbmcgui.ListItem(label=plugin_addon.getLocalizedString(30373))
    avdump_mismatched_files_li.setArt(list_item_art)
    avdump_mismatched_files_li.setInfo(type="video", infoLabels={"plot": plugin_addon.getLocalizedString(30394)}) # setting 'description'
    recreate_all_groups_li = xbmcgui.ListItem(label=plugin_addon.getLocalizedString(30374))
    recreate_all_groups_li.setArt(list_item_art)
    recreate_all_groups_li.setInfo(type="video", infoLabels={"plot": plugin_addon.getLocalizedString(30395)}) # setting 'description'
    sync_hashes_li = xbmcgui.ListItem(label=plugin_addon.getLocalizedString(30375))
    sync_hashes_li.setArt(list_item_art)
    sync_hashes_li.setInfo(type="video", infoLabels={"plot": ""}) # setting 'description'
    update_all_mediainfo_li = xbmcgui.ListItem(label=plugin_addon.getLocalizedString(30376))
    update_all_mediainfo_li.setArt(list_item_art)
    update_all_mediainfo_li.setInfo(type="video", infoLabels={"plot": plugin_addon.getLocalizedString(30396)}) # setting 'description'
    update_series_stats_li = xbmcgui.ListItem(label=plugin_addon.getLocalizedString(30377))
    update_series_stats_li.setArt(list_item_art)
    update_series_stats_li.setInfo(type="video", infoLabels={"plot": plugin_addon.getLocalizedString(30397)}) # setting 'description'

    directory_items = [
        # AniDB (url, ListItem, isFolder)
        (plugin.url_for(show_shoko_anidb_directory), ListItem(label=plugin_addon.getLocalizedString(30367)), True),
        # Import folders (url, ListItem, isFolder)
        (plugin.url_for(show_shoko_import_folders_directory), ListItem(label=plugin_addon.getLocalizedString(30368)), True),
        # TvDB (url, ListItem, isFolder)
        (plugin.url_for(show_shoko_tvdb_directory), ListItem(label=plugin_addon.getLocalizedString(30369)), True),
        # MovieDB (url, ListItem, isFolder)
        (plugin.url_for(show_shoko_moviedb_directory), ListItem(label=plugin_addon.getLocalizedString(30370)), True),
        # Images (url, ListItem, isFolder)
        (plugin.url_for(show_shoko_images_directory), ListItem(label=plugin_addon.getLocalizedString(30371)), True),
        # Trakt (url, ListItem, isFolder)
        (plugin.url_for(show_shoko_trakt_directory), ListItem(label=plugin_addon.getLocalizedString(30372)), True),
        # AVDump mismatched files (url, ListItem, isFolder)
        (plugin.url_for(shoko_avdump_mismatched_files), avdump_mismatched_files_li, False),
        # Recreate all groups (url, ListItem, isFolder)
        (plugin.url_for(shoko_recreate_all_groups), recreate_all_groups_li, False),
        # Sync hashes (url, ListItem, isFolder)
        (plugin.url_for(shoko_sync_hashes), sync_hashes_li, False),
        # Update all mediainfo (url, ListItem, isFolder)
        (plugin.url_for(shoko_update_all_mediainfo), update_all_mediainfo_li, False),
        # Update series stats (url, ListItem, isFolder)
        (plugin.url_for(shoko_update_series_stats), update_series_stats_li, False)
    ]
    # add folders and items to 'Shoko' directory
    addDirectoryItems(handle=plugin.handle, items=directory_items, totalItems=directory_items.__len__())
    endOfDirectory(handle=plugin.handle, cacheToDisc=False)


@plugin.route('/shoko/avdump_mismatched_files')
def shoko_avdump_mismatched_files():
    kodi_models.shoko_avdump_mismatched_files()
    xbmc.executebuiltin('Notification(%s / %s, %s, 7500, %s)' % (plugin_addon.getLocalizedString(30115),
                                                                   plugin_addon.getLocalizedString(30373),
                                                                   plugin_addon.getLocalizedString(30392),
                                                                    plugin_addon.getAddonInfo('icon')))


@plugin.route('/shoko/recreate_all_groups')
def shoko_recreate_all_groups():
    kodi_models.shoko_recreate_all_groups()
    xbmc.executebuiltin('Notification(%s / %s, %s, 7500, %s)' % (plugin_addon.getLocalizedString(30115),
                                                                   plugin_addon.getLocalizedString(30374),
                                                                   plugin_addon.getLocalizedString(30392),
                                                                    plugin_addon.getAddonInfo('icon')))


@plugin.route('/shoko/sync_hashes')
def shoko_sync_hashes():
    kodi_models.shoko_sync_hashes()
    xbmc.executebuiltin('Notification(%s / %s, %s, 7500, %s)' % (plugin_addon.getLocalizedString(30115),
                                                                   plugin_addon.getLocalizedString(30375),
                                                                   plugin_addon.getLocalizedString(30392),
                                                                    plugin_addon.getAddonInfo('icon')))


@plugin.route('/shoko/update_all_mediainfo')
def shoko_update_all_mediainfo():
    kodi_models.shoko_update_all_mediainfo()
    xbmc.executebuiltin('Notification(%s / %s, %s, 7500, %s)' % (plugin_addon.getLocalizedString(30115),
                                                                   plugin_addon.getLocalizedString(30376),
                                                                   plugin_addon.getLocalizedString(30392),
                                                                    plugin_addon.getAddonInfo('icon')))


@plugin.route('/shoko/update_series_stats')
def shoko_update_series_stats():
    kodi_models.shoko_update_series_stats()
    xbmc.executebuiltin('Notification(%s / %s, %s, 7500, %s)' % (plugin_addon.getLocalizedString(30115),
                                                                   plugin_addon.getLocalizedString(30377),
                                                                   plugin_addon.getLocalizedString(30392),
                                                                    plugin_addon.getAddonInfo('icon')))                                                                                                                                                                                                                                                                                

# # IN CASE OF - we want separate folder for Shoko actions in Shoko directory (the one in '/' route)
# # 1. uncomment this function
# # 2. add directory item in show_shoko()
# # 3. delete duplicate items
# # 4. (opt) add localized string for directory name
# @plugin.route('/shoko/shoko')
# def show_shoko_shoko_directory():
#     # 'Shoko'                         (Folder)
#     # - AVDump mismatched files       (item) apiv3.avdump_mismatched_files
#     # - Recreate all groups           (item) apiv3.recreate_all_groups
#     # - Sync hashes                   (item) apiv2.sync_hashes (apiv3.sync_hashes always returns BadRequest)
#     # - Update all mediainfo          (item) apiv3.update_all_mediainfo
#     # - Update series stats           (item) apiv3.update_series_stats

#     kodi_models.set_content('tvshows')
#     kodi_models.set_category(plugin_addon.getLocalizedString())

#     directory_items = [
#         # AVDump mismatched files (url, ListItem, isFolder)
#         ('', ListItem(label=plugin_addon.getLocalizedString(30373)), False),
#         # Recreate all groups (url, ListItem, isFolder)
#         ('', ListItem(label=plugin_addon.getLocalizedString(30374)), False),
#         # Sync hashes (url, ListItem, isFolder)
#         ('', ListItem(label=plugin_addon.getLocalizedString(30375)), False),
#         # Update all mediainfo (url, ListItem, isFolder)
#         ('', ListItem(label=plugin_addon.getLocalizedString(30376)), False),
#         # Update series stats (url, ListItem, isFolder)
#         ('', ListItem(label=plugin_addon.getLocalizedString(30377)), False)
#     ]
#     # add items to 'Shoko' directory 
#     addDirectoryItems(handle=plugin.handle, items=directory_items, totalItems=directory_items.__len__())
#     endOfDirectory(handle=plugin.handle, cacheToDisc=False)


@plugin.route('/shoko/anidb')
def show_shoko_anidb_directory():
    # 'AniDB'                           (Folder)
    #     - Download missing data       (item)
    #     - Sync votes                  (item)
    #     - Sync "My List"              (item)
    #     - Update all info             (item)

    # kodi_models.set_content('tvshows')
    # set category to ' .. / Shoko / AniDB'
    kodi_models.set_category(f'{plugin_addon.getLocalizedString(30115)} / {plugin_addon.getLocalizedString(30367)}')

    list_item_art = {
        'poster': f'{kodi_models.plugin_img_path}/icons/command.png',
        'icon': f'{kodi_models.plugin_img_path}/icons/command.png'
    }

    download_missing_data_li = xbmcgui.ListItem(label=plugin_addon.getLocalizedString(30378))
    download_missing_data_li.setArt(list_item_art)
    download_missing_data_li.setInfo(type="video", infoLabels={"plot": plugin_addon.getLocalizedString(30398)}) # setting 'description'
    sync_votes_li = xbmcgui.ListItem(label=plugin_addon.getLocalizedString(30379))
    sync_votes_li.setArt(list_item_art)
    sync_votes_li.setInfo(type="video", infoLabels={"plot": plugin_addon.getLocalizedString(30399)}) # setting 'description'
    sync_my_list_li = xbmcgui.ListItem(label=plugin_addon.getLocalizedString(30380))
    sync_my_list_li.setArt(list_item_art)
    sync_my_list_li.setInfo(type="video", infoLabels={"plot": plugin_addon.getLocalizedString(30400)}) # setting 'description'
    update_all_info_li = xbmcgui.ListItem(label=plugin_addon.getLocalizedString(30381))
    update_all_info_li.setArt(list_item_art)
    update_all_info_li.setInfo(type="video", infoLabels={"plot": plugin_addon.getLocalizedString(30401)}) # setting 'description'

    directory_items = [
        # Download missing data (url, ListItem, isFolder)
        (plugin.url_for(anidb_download_missing_data), download_missing_data_li, False),
        # Sync votes (url, ListItem, isFolder)
        (plugin.url_for(anidb_sync_votes), sync_votes_li, False),
        # Sync "My List" (url, ListItem, isFolder)
        (plugin.url_for(anidb_sync_my_list), sync_my_list_li, False),
        # Update all info (url, ListItem, isFolder)
        (plugin.url_for(anidb_update_all_info), update_all_info_li, False)
    ]
    # add items to 'AniDB' directory 
    addDirectoryItems(handle=plugin.handle, items=directory_items, totalItems=directory_items.__len__())
    endOfDirectory(handle=plugin.handle, cacheToDisc=False)


@plugin.route('/shoko/anidb/download_missing_data')
def anidb_download_missing_data():
    kodi_models.anidb_download_missing_data()
    xbmc.executebuiltin('Notification(%s / %s, %s, 7500, %s)' % (plugin_addon.getLocalizedString(30367),
                                                                   plugin_addon.getLocalizedString(30378),
                                                                   plugin_addon.getLocalizedString(30392),
                                                                    plugin_addon.getAddonInfo('icon')))


@plugin.route('/shoko/anidb/sync_votes')
def anidb_sync_votes():
    kodi_models.anidb_sync_votes()
    xbmc.executebuiltin('Notification(%s / %s, %s, 7500, %s)' % (plugin_addon.getLocalizedString(30367),
                                                                   plugin_addon.getLocalizedString(30379),
                                                                   plugin_addon.getLocalizedString(30392),
                                                                    plugin_addon.getAddonInfo('icon')))


@plugin.route('/shoko/anidb/sync_my_list')
def anidb_sync_my_list():
    kodi_models.anidb_sync_my_list()
    xbmc.executebuiltin('Notification(%s / %s, %s, 7500, %s)' % (plugin_addon.getLocalizedString(30367),
                                                                   plugin_addon.getLocalizedString(30380),
                                                                   plugin_addon.getLocalizedString(30392),
                                                                    plugin_addon.getAddonInfo('icon')))


@plugin.route('/shoko/anidb/update_all_info')
def anidb_update_all_info():
    kodi_models.anidb_update_all_info()
    xbmc.executebuiltin('Notification(%s / %s, %s, 7500, %s)' % (plugin_addon.getLocalizedString(30367),
                                                                   plugin_addon.getLocalizedString(30381),
                                                                   plugin_addon.getLocalizedString(30392),
                                                                    plugin_addon.getAddonInfo('icon')))


@plugin.route('/shoko/import_folders')
def show_shoko_import_folders_directory():
    # Import folders                                    (Folder)
    #     - Remove missing files                        (item)
    #     - Remove missing files (keep in "My List")    (item)
    #     - Run import                                  (item)
    #     - (User import folders)                       (Folders)

    # kodi_models.set_content('tvshows')
    # set category to ' .. / Shoko / Import folders'
    kodi_models.set_category(f'{plugin_addon.getLocalizedString(30115)} / {plugin_addon.getLocalizedString(30368)}')

    list_item_art = {
        'poster': f'{kodi_models.plugin_img_path}/icons/command.png',
        'icon': f'{kodi_models.plugin_img_path}/icons/command.png'
    }

    remove_missing_files_li = xbmcgui.ListItem(label=plugin_addon.getLocalizedString(30382))
    remove_missing_files_li.setArt(list_item_art)
    remove_missing_files_li.setInfo(type="video", infoLabels={"plot": plugin_addon.getLocalizedString(30402)}) # setting 'description'
    remove_missing_files_keep_li = xbmcgui.ListItem(label=plugin_addon.getLocalizedString(30383))
    remove_missing_files_keep_li.setArt(list_item_art)
    remove_missing_files_keep_li.setInfo(type="video", infoLabels={"plot": plugin_addon.getLocalizedString(30403)}) # setting 'description'
    run_import_li = xbmcgui.ListItem(label=plugin_addon.getLocalizedString(30384))
    run_import_li.setArt(list_item_art)
    run_import_li.setInfo(type="video", infoLabels={"plot": plugin_addon.getLocalizedString(30404)}) # setting 'description'

    directory_items = [
        # Remove missing files (url, ListItem, isFolder)
        (plugin.url_for(import_folder_remove_missing_files), remove_missing_files_li, False),
        # Remove missing files (keep in "My List") (url, ListItem, isFolder)
        (plugin.url_for(import_folder_remove_missing_files_keep), remove_missing_files_keep_li, False),
        # Run import (url, ListItem, isFolder)
        (plugin.url_for(import_folder_run_import_all), run_import_li, False)
    ]
    
    # get list items of import folders
    directory_items += kodi_models.get_import_folders_items()

    # add items to 'Import folders' directory 
    addDirectoryItems(handle=plugin.handle, items=directory_items, totalItems=directory_items.__len__())
    endOfDirectory(handle=plugin.handle, cacheToDisc=False)


@plugin.route('/shoko/import_folders/remove_missing_files')
def import_folder_remove_missing_files():
    kodi_models.import_folder_remove_missing_files(True)
    xbmc.executebuiltin('Notification(%s / %s, %s, 7500, %s)' % (plugin_addon.getLocalizedString(30368),
                                                                   plugin_addon.getLocalizedString(30382),
                                                                   plugin_addon.getLocalizedString(30392),
                                                                    plugin_addon.getAddonInfo('icon')))


@plugin.route('/shoko/import_folders/remove_missing_files_keep')
def import_folder_remove_missing_files_keep():
    kodi_models.import_folder_remove_missing_files(False)
    xbmc.executebuiltin('Notification(%s / %s, %s, 7500, %s)' % (plugin_addon.getLocalizedString(30368),
                                                                   plugin_addon.getLocalizedString(30383),
                                                                   plugin_addon.getLocalizedString(30392),
                                                                    plugin_addon.getAddonInfo('icon')))


@plugin.route('/shoko/import_folders/run_import_all')
def import_folder_run_import_all():
    kodi_models.import_folders_run_import_all()
    xbmc.executebuiltin('Notification(%s / %s, %s, 7500, %s)' % (plugin_addon.getLocalizedString(30368),
                                                                   plugin_addon.getLocalizedString(30384),
                                                                   plugin_addon.getLocalizedString(30392),
                                                                    plugin_addon.getAddonInfo('icon')))


@plugin.route('/shoko/import_folders/<folder_name>-<folder_id>')
def show_shoko_user_import_folder_directory(folder_name, folder_id):
    # Import folder             (folder)
    #     - Rescan folder       (item)

    # kodi_models.set_content('tvshows')
    # set category to ' .. / Shoko / Import folders / folder_name'
    kodi_models.set_category(f'{plugin_addon.getLocalizedString(30115)} / {plugin_addon.getLocalizedString(30368)} / {folder_name}')

    list_item_art = {
        'poster': f'{kodi_models.plugin_img_path}/icons/command.png',
        'icon': f'{kodi_models.plugin_img_path}/icons/command.png'
    }

    rescan_folder_li = xbmcgui.ListItem(label=plugin_addon.getLocalizedString(30393))
    rescan_folder_li.setArt(list_item_art)

    directory_items = [
        # Rescan folder (url, ListItem, isFolder)
        (plugin.url_for(user_import_folder_rescan, folder_name, folder_id), rescan_folder_li, False),
    ]

    # add items to this user's import folder directory 
    addDirectoryItems(handle=plugin.handle, items=directory_items, totalItems=directory_items.__len__())
    endOfDirectory(handle=plugin.handle, cacheToDisc=False)


@plugin.route('/shoko/import_folders/<folder_name>-<folder_id>/rescan')
def user_import_folder_rescan(folder_name, folder_id):
    kodi_models.user_import_folder_rescan(folder_id)
    xbmc.executebuiltin('Notification(%s / %s, %s, 7500, %s)' % (folder_name,
                                                                   plugin_addon.getLocalizedString(30393),
                                                                   plugin_addon.getLocalizedString(30392),
                                                                    plugin_addon.getAddonInfo('icon')))


@plugin.route('/shoko/tvdb')
def show_shoko_tvdb_directory():
    # TvDB                      (Folder)
    #     - Regenerate links    (item)
    #     - Update all info     (item)

    # kodi_models.set_content('tvshows')
    # set category to ' .. / Shoko / TvDB'
    kodi_models.set_category(f'{plugin_addon.getLocalizedString(30115)} / {plugin_addon.getLocalizedString(30369)}')

    list_item_art = {
        'poster': f'{kodi_models.plugin_img_path}/icons/command.png',
        'icon': f'{kodi_models.plugin_img_path}/icons/command.png'
    }

    regenerate_links_li = xbmcgui.ListItem(label=plugin_addon.getLocalizedString(30385))
    regenerate_links_li.setArt(list_item_art)
    regenerate_links_li.setInfo(type="video", infoLabels={"plot": plugin_addon.getLocalizedString(30405)}) # setting 'description'
    update_all_info_li = xbmcgui.ListItem(label=plugin_addon.getLocalizedString(30386))
    update_all_info_li.setArt(list_item_art)
    update_all_info_li.setInfo(type="video", infoLabels={"plot": plugin_addon.getLocalizedString(30406)}) # setting 'description'

    directory_items = [
        # Regenerate links (url, ListItem, isFolder)
        (plugin.url_for(tvdb_regenerate_links), regenerate_links_li, False),
        # Update all info (url, ListItem, isFolder)
        (plugin.url_for(tvdb_update_all_info), update_all_info_li, False)
    ]
    # add items to 'TvDB' directory 
    addDirectoryItems(handle=plugin.handle, items=directory_items, totalItems=directory_items.__len__())
    endOfDirectory(handle=plugin.handle, cacheToDisc=False)


@plugin.route('/shoko/tvdb/regenerate_links')
def tvdb_regenerate_links():
    kodi_models.tvdb_regenerate_links()
    xbmc.executebuiltin('Notification(%s / %s, %s, 7500, %s)' % (plugin_addon.getLocalizedString(30369),
                                                                   plugin_addon.getLocalizedString(30385),
                                                                   plugin_addon.getLocalizedString(30392),
                                                                    plugin_addon.getAddonInfo('icon')))


@plugin.route('/shoko/tvdb/update_all_info')
def tvdb_update_all_info():
    kodi_models.tvdb_update_all_info()
    xbmc.executebuiltin('Notification(%s / %s, %s, 7500, %s)' % (plugin_addon.getLocalizedString(30369),
                                                                   plugin_addon.getLocalizedString(30386),
                                                                   plugin_addon.getLocalizedString(30392),
                                                                    plugin_addon.getAddonInfo('icon')))


@plugin.route('/shoko/moviedb')
def show_shoko_moviedb_directory():
    # MovieDB                   (Folder)
    #     - Update all info     (item)

    # kodi_models.set_content('tvshows')
    # set category to ' .. / Shoko / MovieDB'
    kodi_models.set_category(f'{plugin_addon.getLocalizedString(30115)} / {plugin_addon.getLocalizedString(30370)}')

    list_item_art = {
        'poster': f'{kodi_models.plugin_img_path}/icons/command.png',
        'icon': f'{kodi_models.plugin_img_path}/icons/command.png'
    }

    update_all_info_li = xbmcgui.ListItem(label=plugin_addon.getLocalizedString(30387))
    update_all_info_li.setArt(list_item_art)
    update_all_info_li.setInfo(type="video", infoLabels={"plot": plugin_addon.getLocalizedString(30407)}) # setting 'description'

    directory_items = [
        # Update all info (url, ListItem, isFolder)
        (plugin.url_for(moviedb_update_all_info), update_all_info_li, False)
    ]
    # add items to 'MovieDB' directory 
    addDirectoryItems(handle=plugin.handle, items=directory_items, totalItems=directory_items.__len__())
    endOfDirectory(handle=plugin.handle, cacheToDisc=False)


@plugin.route('/shoko/moviedb/update_all_info')
def moviedb_update_all_info():
    kodi_models.moviedb_update_all_info()
    xbmc.executebuiltin('Notification(%s / %s, %s, 7500, %s)' % (plugin_addon.getLocalizedString(30370),
                                                                   plugin_addon.getLocalizedString(30387),
                                                                   plugin_addon.getLocalizedString(30392),
                                                                    plugin_addon.getAddonInfo('icon')))


@plugin.route('/shoko/images')
def show_shoko_images_directory():
    # Images                (Folder)
    #     - Update all      (item)
    #     - Validate all    (item)

    # kodi_models.set_content('tvshows')
    # set category to ' .. / Shoko / Images'
    kodi_models.set_category(f'{plugin_addon.getLocalizedString(30115)} / {plugin_addon.getLocalizedString(30371)}')

    list_item_art = {
        'poster': f'{kodi_models.plugin_img_path}/icons/command.png',
        'icon': f'{kodi_models.plugin_img_path}/icons/command.png'
    }

    update_all_li = xbmcgui.ListItem(label=plugin_addon.getLocalizedString(30388))
    update_all_li.setArt(list_item_art)
    update_all_li.setInfo(type="video", infoLabels={"plot": plugin_addon.getLocalizedString(30408)}) # setting 'description'
    validate_all_li = xbmcgui.ListItem(label=plugin_addon.getLocalizedString(30389))
    validate_all_li.setArt(list_item_art)
    validate_all_li.setInfo(type="video", infoLabels={"plot": plugin_addon.getLocalizedString(30409)}) # setting 'description'

    directory_items = [
        # Update all (url, ListItem, isFolder)
        (plugin.url_for(images_update_all), update_all_li, False),
        # Validate all (url, ListItem, isFolder)
        (plugin.url_for(images_validate_all), validate_all_li, False)
    ]
    # add items to 'Images' directory 
    addDirectoryItems(handle=plugin.handle, items=directory_items, totalItems=directory_items.__len__())
    endOfDirectory(handle=plugin.handle, cacheToDisc=False)


@plugin.route('/shoko/images/update_all')
def images_update_all():
    kodi_models.images_update_all()
    xbmc.executebuiltin('Notification(%s / %s, %s, 7500, %s)' % (plugin_addon.getLocalizedString(30371),
                                                                   plugin_addon.getLocalizedString(30388),
                                                                   plugin_addon.getLocalizedString(30392),
                                                                    plugin_addon.getAddonInfo('icon')))


@plugin.route('/shoko/images/validate_all')
def images_validate_all():
    kodi_models.images_validate_all()
    xbmc.executebuiltin('Notification(%s / %s, %s, 7500, %s)' % (plugin_addon.getLocalizedString(30371),
                                                                   plugin_addon.getLocalizedString(30389),
                                                                   plugin_addon.getLocalizedString(30392),
                                                                    plugin_addon.getAddonInfo('icon')))


@plugin.route('/shoko/trakt')
def show_shoko_trakt_directory():
    # Trakt                         (Folder)
    #     - Sync Trakt collection   (item)
    #     - Update all info         (item)

    # kodi_models.set_content('tvshows')
    # set category to ' .. / Shoko / Trakt'
    kodi_models.set_category(f'{plugin_addon.getLocalizedString(30115)} / {plugin_addon.getLocalizedString(30372)}')

    list_item_art = {
        'poster': f'{kodi_models.plugin_img_path}/icons/command.png',
        'icon': f'{kodi_models.plugin_img_path}/icons/command.png'
    }

    sync_trakt_collection_li = xbmcgui.ListItem(label=plugin_addon.getLocalizedString(30390))
    sync_trakt_collection_li.setArt(list_item_art)
    sync_trakt_collection_li.setInfo(type="video", infoLabels={"plot": plugin_addon.getLocalizedString(30410)}) # setting 'description'
    update_all_info_li = xbmcgui.ListItem(label=plugin_addon.getLocalizedString(30391))
    update_all_info_li.setArt(list_item_art)
    update_all_info_li.setInfo(type="video", infoLabels={"plot": plugin_addon.getLocalizedString(30411)}) # setting 'description'

    directory_items = [
        # Sync Trakt collection (url, ListItem, isFolder)
        (plugin.url_for(trakt_sync_trakt_collection), sync_trakt_collection_li, False),
        # Update all info (url, ListItem, isFolder)
        (plugin.url_for(trakt_update_all_info), update_all_info_li, False)
    ]
    # add items to 'Trakt' directory 
    addDirectoryItems(handle=plugin.handle, items=directory_items, totalItems=directory_items.__len__())
    endOfDirectory(handle=plugin.handle, cacheToDisc=False)


@plugin.route('/shoko/trakt/sync_trakt_collection')
def trakt_sync_trakt_collection():
    kodi_models.trakt_sync_trakt_collection()
    xbmc.executebuiltin('Notification(%s / %s, %s, 7500, %s)' % (plugin_addon.getLocalizedString(30372),
                                                                   plugin_addon.getLocalizedString(30390),
                                                                   plugin_addon.getLocalizedString(30392),
                                                                    plugin_addon.getAddonInfo('icon')))


@plugin.route('/shoko/trakt/update_all_info')
def trakt_update_all_info():
    kodi_models.trakt_update_all_info()
    xbmc.executebuiltin('Notification(%s / %s, %s, 7500, %s)' % (plugin_addon.getLocalizedString(30372),
                                                                   plugin_addon.getLocalizedString(30391),
                                                                   plugin_addon.getLocalizedString(30392),
                                                                    plugin_addon.getAddonInfo('icon')))


@plugin.route('/settings')
def show_settings():
    xbmc.executebuiltin('Addon.OpenSettings(plugin.video.nakamori)')


@plugin.route('/recent')
def show_recent():
    list_of_li = kodi_models.list_all_recent_series_and_episodes()
    list_count = len(list_of_li)
    for o_id, o_type, li in list_of_li:
        if o_type == ThisType.series:
            addDirectoryItem(plugin.handle, plugin.url_for(open_series_by_series_id_and_filter_id, 0, o_id), li, True, totalItems=list_count)
        elif o_type == ThisType.episodes:
            addDirectoryItem(plugin.handle, plugin.url_for(open_episode, 0, 0, o_id), li, False, totalItems=list_count)
        elif o_type == ThisType.raw:
            addDirectoryItem(plugin.handle, plugin.url_for(open_rawfile, o_id), li, False, totalItems=list_count)
    endOfDirectory(plugin.handle, cacheToDisc=False)


@plugin.route('/calendar')
def show_calendar():
    lib.windows.ac_calendar.open_calendar()
    pass


@plugin.route('/dialog/series/<series_id>/watched')
def watched_series(series_id):
    kodi_models.set_watch_mark(ThisType.series, series_id, True)


@plugin.route('/dialog/series/<series_id>/unwatched')
def unwatched_series(series_id):
    kodi_models.set_watch_mark(ThisType.series, series_id, False)


@plugin.route('/dialog/episode/<ep_id>/watched')
def watched_episode(ep_id):
    kodi_models.set_watch_mark(ThisType.episodes, ep_id, True)


@plugin.route('/dialog/episode/<ep_id>/unwatched')
def unwatched_episode(ep_id):
    kodi_models.set_watch_mark(ThisType.episodes, ep_id, False)


@plugin.route('/dialog/move_to/<position>')
def move_to(position: int):
    kodi_utils.move_to(int(position))


def main():
    # if we need to change/save ip/apikey we need to 'close' plugin so kodi can flush changes into file/memory.
    # if we dont do that, kodi will 'read' old setting file while we already configure proper one to use.

    # stage 0 - everything before connecting
    kodi_utils.get_device_id()

    # stage 1 - check connection
    if not shoko_utils.can_connect():
        if xbmcgui.Dialog().yesno(plugin_addon.getLocalizedString(30197), plugin_addon.getLocalizedString(30237)):
            # go back to avoid loops
            xbmc.executebuiltin("Action(Back,%s)" % xbmcgui.getCurrentWindowId())
            xbmc.executebuiltin("Dialog.Close(all, true)")
            wiz_cancel, ip, port = wizard.open_connection_wizard()
            return False
    # stage 2 - Check server startup status
    if not shoko_utils.get_server_status():
        return False

    # stage 3 - auth
    auth = shoko_utils.auth()
    if not auth:
        kodi_utils.message_box(plugin_addon.getLocalizedString(30194), plugin_addon.getLocalizedString(30157))
        xbmc.executebuiltin("Action(Back,%s)" % xbmcgui.getCurrentWindowId())
        xbmc.executebuiltin("Dialog.Close(all, true)")
        status, apikey = wizard.open_login_wizard()
        auth = shoko_utils.auth(new_apikey=apikey)
        return False
    else:
        return True


if __name__ == '__main__':
    kodi_utils.debug('===========================')
    kodi_utils.debug(f'======= {argv}')
    kodi_utils.debug('===========================')

    if main():
        # let's support scripts ('/dialog/') without remixing routing lib
        if len(argv) > 1:
            if argv[0] == 'nakamoriplugin.py' or argv[1].startswith('/dialog/'):
                url = plugin.url_for_path(argv[1])
                plugin.run(argv=[url])
            else:
                plugin.run(argv)
        else:
            plugin.run(argv)
