# -*- coding: utf-8 -*-

from lib import kodi_utils
from lib import shoko_utils
from lib import naka_player
from lib.naka_utils import ThisType
from models import kodi_models

import routing
from lib.windows import wizard
import xbmc
import xbmcgui
from xbmcgui import ListItem
import xbmcaddon
from xbmcplugin import addDirectoryItem, endOfDirectory
import sys
import lib.search as search
import lib.favorite as favorite
from operator import itemgetter

plugin_addon = xbmcaddon.Addon(id='plugin.video.nakamori')
plugin = routing.Plugin()

# TODO  this is setthing inside Shoko that will Group Series into parent Groups (ex. Monogatari-Series)
setting_from_shoko_that_we_need_to_fetch_later_use_series_grouping = False
do_we_want_to_make_eptype_setting = True


@plugin.route('/')
def list_all_filters():
    """
    List all Filters for current User
    :return: Draw ListItem's Collection of Filters
    """
    xbmc.log('/', xbmc.LOGINFO)
    kodi_models.set_sorting_method(ThisType.filter)
    y = kodi_models.list_all_filters()
    x = kodi_models.main_menu_items()
    for extra in x:
        y.append((0, ThisType.menu, extra, kodi_models.remove_markdown(extra.getLabel())))
    y_count = len(y)
    # sort them by name
    y.sort(key=itemgetter(3))

    for filter_id, f_type, li, label in y:
        if f_type == ThisType.filter:
            addDirectoryItem(plugin.handle, plugin.url_for(list_groups_by_filter_id, filter_id), li, True, totalItems=y_count)
        elif f_type == ThisType.filters:
            addDirectoryItem(plugin.handle, plugin.url_for(list_filter_by_filters_id, filter_id), li, True, totalItems=y_count)
        elif f_type == ThisType.menu:
            addDirectoryItem(plugin.handle, li.getPath(), li, True, totalItems=y_count)

    endOfDirectory(plugin.handle)


@plugin.route('/fs-<filters_id>')
def list_filter_by_filters_id(filters_id: int):
    xbmc.log(f'/fs-{filters_id}', xbmc.LOGINFO)
    kodi_models.set_sorting_method(ThisType.filter)
    y = kodi_models.list_all_filter_by_filters_id(filters_id)
    y_count = len(y)
    for obj_id, obj_type, li in y:
        if obj_type == ThisType.filter:
            addDirectoryItem(plugin.handle, plugin.url_for(list_groups_by_filter_id, obj_id), li, True, totalItems=y_count)
        if obj_type == ThisType.filters:
            addDirectoryItem(plugin.handle, plugin.url_for(list_filter_by_filters_id, obj_id), li, True, totalItems=y_count)

    endOfDirectory(plugin.handle)


@plugin.route('/f-<filter_id>')
def list_groups_by_filter_id(filter_id: int):
    """
    List all Groups for current User in Filter
    :param filter_id: ID of Filter that we want list content of
    :return: Draw ListItem's Collection of Group
    """
    xbmc.log(f'/f-{filter_id}', xbmc.LOGINFO)
    kodi_models.set_sorting_method(ThisType.series)
    y = kodi_models.list_all_groups_by_filter_id(filter_id)
    y_count = len(y)
    for obj_id, obj_type, li in y:
        if obj_type == ThisType.group:
            addDirectoryItem(plugin.handle, plugin.url_for(open_group_by_group_id_and_filter_id, filter_id, obj_id), li, True, totalItems=y_count)
        if obj_type == ThisType.series:
            addDirectoryItem(plugin.handle, plugin.url_for(open_series_by_series_id_and_filter_id, filter_id, obj_id), li, True, totalItems=y_count)

    endOfDirectory(plugin.handle)


@plugin.route('/f-<filter_id>/g-<group_id>')
def open_group_by_group_id_and_filter_id(filter_id: int, group_id: int):
    xbmc.log(f'/f-{filter_id}/g-{group_id}', xbmc.LOGINFO)
    kodi_models.set_sorting_method(ThisType.series)
    pass


@plugin.route('/f-<filter_id>/s-<series_id>')
def open_series_by_series_id_and_filter_id(filter_id: int, series_id: int):
    xbmc.log(f'/f-{filter_id}/s-{series_id}', xbmc.LOGINFO)
    kodi_models.set_sorting_method(ThisType.episode)
    list_of_ep_types = []
    list_of_eps = []

    for e in kodi_models.list_episodes_for_series_by_series_id(series_id):
        list_of_eps.append(e)

    for ep_id, ep_type, li in list_of_eps:
        if do_we_want_to_make_eptype_setting:
            if ep_type not in list_of_ep_types:
                list_of_ep_types.append(ep_type)
        else:
            addDirectoryItem(plugin.handle, plugin.url_for(open_episode, filter_id, series_id, ep_id), li, False, totalItems=len(list_of_eps))

    if do_we_want_to_make_eptype_setting:
        if len(list_of_ep_types) > 1:
            for ep_type in list_of_ep_types:
                li = xbmcgui.ListItem(str(ep_type))
                addDirectoryItem(plugin.handle, plugin.url_for(open_eptype_by_eptype_by_series_id_and_filter_id, filter_id, series_id, int(ep_type)), li, True, totalItems=len(list_of_ep_types))
        else:
            for ep_id, ep_type, li in list_of_eps:
                addDirectoryItem(plugin.handle, plugin.url_for(open_episode, filter_id, series_id, ep_id), li, False, totalItems=len(list_of_eps))
    endOfDirectory(plugin.handle)


@plugin.route('/f-<filter_id>/s-<series_id>/et-<eptype_id>')
def open_eptype_by_eptype_by_series_id_and_filter_id(filter_id: int, series_id: int, eptype_id: int):
    xbmc.log(f'/f-{filter_id}/s-{series_id}/et-{eptype_id}', xbmc.LOGINFO)
    kodi_models.set_sorting_method(ThisType.episode)
    y = kodi_models.list_episodes_for_series_by_series_id(series_id)
    y_count = len(y)
    for ep_id, ep_type, li in y:
        if int(ep_type) == int(eptype_id):
            li.setLabel("e" + li.getLabel())  # temporary
            addDirectoryItem(plugin.handle, plugin.url_for(open_episode, filter_id, series_id, ep_id), li, False, totalItems=y_count)
    endOfDirectory(plugin.handle)


@plugin.route('/f-<filter_id>/s-<series_id>/e-<ep_id>-play')
def open_episode(filter_id: int, series_id: int, ep_id: int):
    xbmc.log(f'/f-{filter_id}/s-{series_id}/e-{ep_id}-play', xbmc.LOGINFO)
    raw_files_list = kodi_models.get_file_id_from_ep_id(ep_id)
    file_id = 0
    if len(raw_files_list) == 1:
        file_id = raw_files_list[0].id
    if file_id != 0:
        play = naka_player.play_video(file_id=file_id, ep_id=ep_id, s_id=series_id, force_direct_play=True)


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

    # a-z search (no keyboard)
    # li = ListItem(label=kodi_models.bold('A-Z'), offscreen=True)
    # kodi_models.set_art(li, None, 'search.png')
    # addDirectoryItem(plugin.handle, plugin.url_for(az_search), li, True)

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

    endOfDirectory(plugin.handle)


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


@plugin.route('/menu-search/<query>-<fuzzy>-<tag>/')
def search_for(query: str, fuzzy: bool, tag: bool):
    kodi_models.set_content('tvshows')
    kodi_models.set_category(query)

    fuzziness = 1 if str(fuzzy).lower() == 'true' else 0
    taginess = 1 if str(tag).lower() == 'true' else 0
    if len(query) > 0:
        list_of_s = kodi_models.show_search_result_menu(query, fuzziness, taginess)
        list_count = len(list_of_s)
        for s in list_of_s:
            addDirectoryItem(plugin.handle, plugin.url_for(open_series_by_series_id_and_filter_id, 0, s.id),
                             kodi_models.get_listitem_from_serie(s), True, totalItems=list_count)

        endOfDirectory(plugin.handle)


@plugin.route('/search/az')
def az_search():
    pass


@plugin.route('/dialog/search/clear')
def url_clear_search_terms():
    search.clear_search_history()
    xbmc.executebuiltin('Container.Refresh')


@plugin.route('/dialog/search/<query>-<fuzzy>-<tag>/remove')
def url_remove_search_term(query, fuzzy, tag):
    search.remove_search_history(query, fuzzy, tag)
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
    endOfDirectory(plugin.handle)


@plugin.route('/dialog/favorites/<sid>/remove')
def remove_favorite(sid):
    favorite.remove_favorite(sid)
    xbmc.executebuiltin('Container.Refresh')


@plugin.route('/dialog/favorites/<sid>/add')
def add_favorite(sid):
    favorite.add_favorite(sid)
    kodi_utils.message_box(plugin_addon.getLocalizedString(30211), plugin_addon.getLocalizedString(30212))


@plugin.route('/shoko')
def show_shoko():
    pass


@plugin.route('/settings')
def show_settings():
    xbmc.executebuiltin('Addon.OpenSettings(plugin.video.nakamori)')


@plugin.route('/recent')
def show_recent():
    pass


@plugin.route('/calendar')
def show_calendar():
    pass


@plugin.route('/calendar_classic')
def show_calendar_classic():
    pass


def main():
    # stage 0 - everything before connecting
    kodi_utils.get_device_id()

    # stage 1 - check connection
    if not shoko_utils.can_connect():
        if xbmcgui.Dialog().yesno(plugin_addon.getLocalizedString(30197), plugin_addon.getLocalizedString(30000)):
            # go back to avoid loops
            xbmc.executebuiltin("Action(Back,%s)" % xbmcgui.getCurrentWindowId())
            xbmc.executebuiltin("Dialog.Close(all, true)")

            if wizard.open_connection_wizard():
                return False
        else:
            pass
        if not shoko_utils.can_connect():
            kodi_utils.message_box("exit", "exit")
            return False

    # stage 2 - Check server startup status
    if not shoko_utils.get_server_status():
        pass

    # stage 3 - auth
    auth = shoko_utils.auth()
    if not auth:
        kodi_utils.message_box(plugin_addon.getLocalizedString(30194), plugin_addon.getLocalizedString(30157))
        xbmc.executebuiltin("Action(Back,%s)" % xbmcgui.getCurrentWindowId())
        xbmc.executebuiltin("Dialog.Close(all, true)")
        status, apikey = wizard.open_login_wizard()
        auth = shoko_utils.auth(new_apikey=apikey)
        if not auth:
            raise RuntimeError("try again with other settings")
    else:
        return True


if __name__ == '__main__':
    xbmc.log('===========================', xbmc.LOGINFO)
    xbmc.log(f'======= {sys.argv[0]}', xbmc.LOGINFO)
    xbmc.log(f'======= {sys.argv[1]}', xbmc.LOGINFO)
    if main():
        # let's support scripts without hacking like we used to
        if sys.argv[1].startswith('/dialog/'):
            plugin.run(argv=[sys.argv[1]])
        else:
            plugin.run()
