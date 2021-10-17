# -*- coding: utf-8 -*-
from api.shoko.v2 import api2, api2models
import xbmc
import xbmcaddon
from xbmcgui import ListItem
from lib.kodi_utils import bold
from typing import List

plugin_addon = xbmcaddon.Addon('plugin.video.nakamori')

api = api2.Client(address=plugin_addon.getSetting('ipaddress'),
                  port=plugin_addon.getSettingInt('port'),
                  apikey=plugin_addon.getSetting('apikey'),
                  timeout=plugin_addon.getSettingInt('timeout'))


def get_infolabels(x: api2models.Filter):
    return {'Title': x.name, 'Plot': x.name}


def get_listitem(x: api2models.Filter) -> ListItem:
    url = f'/filter/{x.id}'
    name = x.name
    name = bold(name)
    li = ListItem(name, path=url)
    li.setPath(url)
    infolabels = get_infolabels(x)
    #li.set_watched_flags(infolabels, self.is_watched())
    li.setInfo(type='video', infoLabels=infolabels)
    #li.set_art(self)
    #context = self.get_context_menu_items()
    #if context is not None and len(context) > 0:
    #    li.addContextMenuItems(context)
    return li


def ListAllFilters() -> List[ListItem]:
    list_of_listitems = []
    x = api.filter()
    xbmc.log('---------->', xbmc.LOGINFO)
    xbmc.log(f'----------> {x}', xbmc.LOGINFO)

    for f in x:
        list_of_listitems.append(get_listitem(f))
    return list_of_listitems
