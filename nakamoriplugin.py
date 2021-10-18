# -*- coding: utf-8 -*-

from lib import kodi_utils
from lib import shoko_utils
from lib.naka_utils import ThisType
from models import kodi_models

import routing
from lib.windows import wizard
import xbmc
from xbmcplugin import addDirectoryItem, endOfDirectory

plugin = routing.Plugin()

# TODO  this is setthing inside Shoko that will Group Series into parent Groups (ex. Monogatari-Series)
setting_from_shoko_that_we_need_to_fetch_later_use_series_grouping = False
do_we_want_to_make_eptype_setting = True


@plugin.route('/')
@plugin.route('/filter')
def list_all_filters():
    """
    List all Filters for current User
    :return: Draw ListItem's Collection of Filters
    """
    xbmc.log('/', xbmc.LOGINFO)
    for filter_id, li in kodi_models.list_all_filters():
        li.setLabel("f" + li.getLabel())  # temporary
        addDirectoryItem(plugin.handle, plugin.url_for(list_groups_by_filter_id, filter_id), li, True)
    endOfDirectory(plugin.handle)


@plugin.route('/filter/<filter_id>/group')
def list_groups_by_filter_id(filter_id: int):
    """
    List all Groups for current User in Filter
    :param filter_id: ID of Filter that we want list content of
    :return: Draw ListItem's Collection of Group
    """
    xbmc.log(f'/filter/{filter_id}/group', xbmc.LOGINFO)
    for obj_id, obj_type, li in kodi_models.list_all_groups_by_filter_id(filter_id):
        if obj_type == ThisType.group:
            li.setLabel("g" + li.getLabel())  # temporary
            addDirectoryItem(plugin.handle, plugin.url_for(open_group_by_group_id_and_filter_id, filter_id, obj_id), li, True)
        if obj_type == ThisType.series:
            li.setLabel("s" + li.getLabel())  # temporary
            addDirectoryItem(plugin.handle, plugin.url_for(open_series_by_series_id_and_filter_id, filter_id, obj_id), li, True)

    endOfDirectory(plugin.handle)


@plugin.route('/filter/<filter_id>/group/<group_id>')
def open_group_by_group_id_and_filter_id(filter_id: int, group_id: int):
    xbmc.log(f'/filter/{filter_id}/group/{group_id}', xbmc.LOGINFO)
    pass


@plugin.route('/filter/<filter_id>/series/<series_id>/ep')
def open_series_by_series_id_and_filter_id(filter_id: int, series_id: int):
    xbmc.log(f'/filter/{filter_id}/series/{series_id}/ep', xbmc.LOGINFO)

    list_of_ep_types = []
    for ep_id, ep_type, li in kodi_models.list_episodes_for_series_by_series_id(series_id):
        if do_we_want_to_make_eptype_setting:
            if ep_type not in list_of_ep_types:
                list_of_ep_types.append(ep_type)
        else:
            li.setLabel("e" + li.getLabel())  # temporary
            addDirectoryItem(plugin.handle, plugin.url_for(open_episode, filter_id, series_id, ep_id), li, False)

    if do_we_want_to_make_eptype_setting:
        for ep_type in list_of_ep_types:
            import xbmcgui
            li = xbmcgui.ListItem(str(ep_type))
            li.setLabel("et" + li.getLabel())  # temporary
            addDirectoryItem(plugin.handle, plugin.url_for(open_eptype_by_eptype_by_series_id_and_filter_id, filter_id, series_id, int(ep_type)), li, True)
    endOfDirectory(plugin.handle)


@plugin.route('/filter/<filter_id>/series/<series_id>/ep/<eptype_id>')
def open_eptype_by_eptype_by_series_id_and_filter_id(filter_id: int, series_id: int, eptype_id: int):
    xbmc.log(f'/filter/{filter_id}/series/{series_id}/ep/{eptype_id}', xbmc.LOGINFO)
    for ep_id, ep_type, li in kodi_models.list_episodes_for_series_by_series_id(series_id):
        if int(ep_type) == int(eptype_id):
            li.setLabel("e" + li.getLabel())  # temporary
            addDirectoryItem(plugin.handle, plugin.url_for(open_episode, filter_id, series_id, ep_id), li, False)
    endOfDirectory(plugin.handle)


@plugin.route('/filter/<filter_id>/series/<series_id>/ep/<ep_id>')
def open_episode(filter_id: int, series_id: int, ep_id: int):
    xbmc.log('/', xbmc.LOGINFO)
    pass


def main():
    # stage 0 - everything before connecting
    kodi_utils.get_device_id()

    # stage 1 - check connection
    if not shoko_utils.can_connect():
        kodi_utils.message_box("not connect", 'cannot connect')
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
        kodi_utils.message_box("auth", "error")
        xbmc.executebuiltin("Dialog.Close(all, true)")
        if wizard.open_login_wizard():
            pass
        auth = shoko_utils.auth()
        if not auth:
            raise RuntimeError("try again with other settings")
    else:
        return True


if __name__ == '__main__':
    if main():
        plugin.run()
