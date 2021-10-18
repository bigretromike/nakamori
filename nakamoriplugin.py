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
import xbmcaddon
from xbmcplugin import addDirectoryItem, endOfDirectory

plugin_addon = xbmcaddon.Addon(id='plugin.video.nakamori')
plugin = routing.Plugin()

# TODO  this is setthing inside Shoko that will Group Series into parent Groups (ex. Monogatari-Series)
setting_from_shoko_that_we_need_to_fetch_later_use_series_grouping = False
do_we_want_to_make_eptype_setting = True


@plugin.route('/')
@plugin.route('/f')
def list_all_filters():
    """
    List all Filters for current User
    :return: Draw ListItem's Collection of Filters
    """
    xbmc.log('/', xbmc.LOGINFO)
    for filter_id, f_type, li in kodi_models.list_all_filters():
        if f_type == ThisType.filter:
            li.setLabel("f" + li.getLabel())  # temporary
            addDirectoryItem(plugin.handle, plugin.url_for(list_groups_by_filter_id, filter_id), li, True)
        elif f_type == ThisType.filters:
            li.setLabel("fs" + li.getLabel())  # temporary
            addDirectoryItem(plugin.handle, plugin.url_for(list_filter_by_filters_id, filter_id), li, True)
    endOfDirectory(plugin.handle)


@plugin.route('/f/<filters_id>/filter')
def list_filter_by_filters_id(filters_id: int):
    xbmc.log(f'/f/{filters_id}/filter', xbmc.LOGINFO)
    for obj_id, obj_type, li in kodi_models.list_all_filter_by_filters_id(filters_id):
        if obj_type == ThisType.filter:
            li.setLabel("f" + li.getLabel())  # temporary
            addDirectoryItem(plugin.handle, plugin.url_for(list_groups_by_filter_id, obj_id), li, True)
        if obj_type == ThisType.filters:
            li.setLabel("fs" + li.getLabel())  # temporary
            addDirectoryItem(plugin.handle, plugin.url_for(list_filter_by_filters_id, obj_id), li, True)

    endOfDirectory(plugin.handle)


@plugin.route('/f/<filter_id>/group')
def list_groups_by_filter_id(filter_id: int):
    """
    List all Groups for current User in Filter
    :param filter_id: ID of Filter that we want list content of
    :return: Draw ListItem's Collection of Group
    """
    xbmc.log(f'/f/{filter_id}/group', xbmc.LOGINFO)
    for obj_id, obj_type, li in kodi_models.list_all_groups_by_filter_id(filter_id):
        if obj_type == ThisType.group:
            li.setLabel("g" + li.getLabel())  # temporary
            addDirectoryItem(plugin.handle, plugin.url_for(open_group_by_group_id_and_filter_id, filter_id, obj_id), li, True)
        if obj_type == ThisType.series:
            li.setLabel("s" + li.getLabel())  # temporary
            addDirectoryItem(plugin.handle, plugin.url_for(open_series_by_series_id_and_filter_id, filter_id, obj_id), li, True)

    endOfDirectory(plugin.handle)


@plugin.route('/f/<filter_id>/g/<group_id>')
def open_group_by_group_id_and_filter_id(filter_id: int, group_id: int):
    xbmc.log(f'/f/{filter_id}/g/{group_id}', xbmc.LOGINFO)
    pass


@plugin.route('/f/<filter_id>/s/<series_id>/ep')
def open_series_by_series_id_and_filter_id(filter_id: int, series_id: int):
    xbmc.log(f'/f/{filter_id}/s/{series_id}/ep', xbmc.LOGINFO)

    list_of_ep_types = []
    list_of_eps = []

    for e in kodi_models.list_episodes_for_series_by_series_id(series_id):
        list_of_eps.append(e)

    for ep_id, ep_type, li in list_of_eps:
        if do_we_want_to_make_eptype_setting:
            if ep_type not in list_of_ep_types:
                list_of_ep_types.append(ep_type)
        else:
            li.setLabel("e" + li.getLabel())  # temporary
            addDirectoryItem(plugin.handle, plugin.url_for(open_episode, filter_id, series_id, ep_id), li, False)

    if do_we_want_to_make_eptype_setting:
        if len(list_of_ep_types) > 1:
            for ep_type in list_of_ep_types:
                li = xbmcgui.ListItem(str(ep_type))
                li.setLabel("et" + li.getLabel())  # temporary
                addDirectoryItem(plugin.handle, plugin.url_for(open_eptype_by_eptype_by_series_id_and_filter_id, filter_id, series_id, int(ep_type)), li, True)
        else:
            for ep_id, ep_type, li in list_of_eps:
                li.setLabel("e" + li.getLabel())  # temporary
                addDirectoryItem(plugin.handle, plugin.url_for(open_episode, filter_id, series_id, ep_id), li, False)
    endOfDirectory(plugin.handle)


@plugin.route('/f/<filter_id>/s/<series_id>/et/<eptype_id>')
def open_eptype_by_eptype_by_series_id_and_filter_id(filter_id: int, series_id: int, eptype_id: int):
    xbmc.log(f'/f/{filter_id}/s/{series_id}/et/{eptype_id}', xbmc.LOGINFO)
    for ep_id, ep_type, li in kodi_models.list_episodes_for_series_by_series_id(series_id):
        if int(ep_type) == int(eptype_id):
            li.setLabel("e" + li.getLabel())  # temporary
            addDirectoryItem(plugin.handle, plugin.url_for(open_episode, filter_id, series_id, ep_id), li, False)
    endOfDirectory(plugin.handle)


@plugin.route('/f/<filter_id>/s/<series_id>/e/<ep_id>/play')
def open_episode(filter_id: int, series_id: int, ep_id: int):
    xbmc.log(f'/f/<{filter_id}>/s/<{series_id}>/e/<{ep_id}>/play', xbmc.LOGINFO)
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


def main():
    # stage 0 - everything before connecting
    kodi_utils.get_device_id()

    # stage 1 - check connection
    if not shoko_utils.can_connect():
        kodi_utils.message_box(plugin_addon.getLocalizedString(30197), plugin_addon.getLocalizedString(30197))
        xbmc.executebuiltin("Dialog.Close(all, true)")
        if wizard.open_connection_wizard():
            pass
        if not shoko_utils.can_connect():
            raise RuntimeError("try again with other settings")

    # stage 2 - Check server startup status
    if not shoko_utils.get_server_status():
        pass

    # stage 3 - auth
    auth = shoko_utils.auth()
    if not auth:
        kodi_utils.message_box(plugin_addon.getLocalizedString(30194), plugin_addon.getLocalizedString(30157))
        xbmc.executebuiltin("Dialog.Close(all, true)")
        status, apikey = wizard.open_login_wizard()
        auth = shoko_utils.auth(new_apikey=apikey)
        if not auth:
            raise RuntimeError("try again with other settings")
    else:
        return True


if __name__ == '__main__':
    if main():
        plugin.run()
