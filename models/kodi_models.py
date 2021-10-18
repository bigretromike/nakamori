# -*- coding: utf-8 -*-
from api.shoko.v2 import api2, api2models
import xbmc
import xbmcaddon
from xbmcgui import ListItem
from lib.kodi_utils import bold
from typing import List, Tuple
from lib.naka_utils import ThisType, map_episodetype_to_thistype, map_filter_group_to_thistype

plugin_addon = xbmcaddon.Addon('plugin.video.nakamori')

api = api2.Client(address=plugin_addon.getSetting('ipaddress'),
                  port=plugin_addon.getSettingInt('port'),
                  apikey=plugin_addon.getSetting('apikey'),
                  timeout=plugin_addon.getSettingInt('timeout'))


def get_infolabels(x: api2models.Filter):
    return {'Title': x.name, 'Plot': x.name}


def set_art(li: ListItem, art: api2models.ArtCollection):
    http = "http://" + plugin_addon.getSetting('ipaddress') + ":" + str(plugin_addon.getSettingInt('port')) + "{}"
    if len(art.fanart) > 0:
        li.setArt({'fanart': http.format(art.fanart[0].url), 'clearart': http.format(art.fanart[0].url)})
    if len(art.thumb) > 0:
        li.setArt({'thumb': http.format(art.thumb[0].url)})
        li.setArt({'poster': http.format(art.thumb[0].url)})
        li.setArt({'icon': http.format(art.thumb[0].url)})
    if len(art.banner) > 0:
        li.setArt({'banner': http.format(art.banner[0].url)})


def get_listitem_from_filter(x: api2models.Filter) -> ListItem:
    url = f'/filter/{x.id}'
    name = x.name
    name = bold(name)
    li = ListItem(name, path=url)
    li.setPath(url)
    infolabels = get_infolabels(x)
    #li.set_watched_flags(infolabels, self.is_watched())
    li.setInfo(type='video', infoLabels=infolabels)

    if x.art is not None:
        set_art(li, x.art)
    #context = self.get_context_menu_items()
    #if context is not None and len(context) > 0:
    #    li.addContextMenuItems(context)
    return li


def get_listitem_from_group(x: api2models.Group) -> ListItem:
    url = f'/group/{x.id}'
    name = x.name
    name = bold(name)
    li = ListItem(name, path=url)
    li.setPath(url)
    infolabels = get_infolabels(x)
    #li.set_watched_flags(infolabels, self.is_watched())
    li.setInfo(type='video', infoLabels=infolabels)
    if x.art is not None:
        set_art(li, x.art)
    #context = self.get_context_menu_items()
    #if context is not None and len(context) > 0:
    #    li.addContextMenuItems(context)
    return li


def get_listitem_from_serie(x: api2models.Serie) -> ListItem:
    url = f'/group/{x.id}'
    name = x.name
    name = bold(name)
    li = ListItem(name, path=url)
    li.setPath(url)
    infolabels = get_infolabels(x)
    # li.set_watched_flags(infolabels, self.is_watched())
    li.setInfo(type='video', infoLabels=infolabels)
    if x.art is not None:
        set_art(li, x.art)
    # context = self.get_context_menu_items()
    # if context is not None and len(context) > 0:
    #    li.addContextMenuItems(context)
    return li


def get_listitem_from_episode(x: api2models.Episode) -> ListItem:
    url = f'/ep/{x.eid}'
    name = x.name
    li = ListItem(name, path=url)
    li.setPath(url)
    infolabels = get_infolabels(x)
    # li.set_watched_flags(infolabels, self.is_watched())
    li.setInfo(type='video', infoLabels=infolabels)
    if x.art is not None:
        set_art(li, x.art)
    # context = self.get_context_menu_items()
    # if context is not None and len(context) > 0:
    #    li.addContextMenuItems(context)
    return li


def list_all_filters() -> List[Tuple[int, ThisType, ListItem]]:
    """
    Get All Filters for current User
    :return: List[(int, ListItem)]
    """
    list_of_listitems = []
    q = api2.QueryOptions()
    # get images
    q.allpics = 1
    x = api.filter(q)

    for f in x.filters:
        d = api2models.Filter.Decoder(f)
        list_of_listitems.append((d.id, map_filter_group_to_thistype(d.type), get_listitem_from_filter(d)))

    return list_of_listitems


def list_all_filter_by_filters_id(id: int) -> List[Tuple[int, ThisType, ListItem]]:
    list_of_li = []
    q = api2.QueryOptions()
    q.id = id
    q.level = 2
    x = api.filter(q)

    for f in x.filters:
        list_of_li.append((f.id, map_filter_group_to_thistype(f.type), get_listitem_from_filter(f)))

    return list_of_li


def list_all_groups_by_filter_id(id: int) -> List[Tuple[int, ThisType, ListItem]]:
    list_of_listitems = []
    q = api2.QueryOptions()
    q.id = id
    q.level = 3
    x = api.filter(q)

    for g in x.groups:
        # we dont want to show empty groups, for now ?options?
        if len(g.series) > 0:
            if len(g.series) == 1:
                list_of_listitems.append((g.series[0].id, ThisType.series, get_listitem_from_serie(g.series[0])))
            else:
                list_of_listitems.append((g.id, ThisType.group, get_listitem_from_group(g)))

    return list_of_listitems


def list_all_series_by_filter_id(id: int) -> List[Tuple[int, ListItem]]:
    list_of_listitems = []
    q = api2.QueryOptions()
    q.id = id
    q.level = 3
    x = api.filter(q)

    for g in x.groups:
        s = api2models.Serie.Decoder(g)
        list_of_listitems.append((s.id, get_listitem_from_serie(s)))

    return list_of_listitems


def list_episodes_for_series_by_series_id(id: int) -> List[Tuple[int, ThisType, ListItem]]:
    list_of_li = []
    q = api2.QueryOptions()
    q.allpics = 1
    q.id = id
    q.level = 1
    x = api.series_get_by_id(q)

    for ep in x.eps:
        list_of_li.append((ep.id, map_episodetype_to_thistype(ep.eptype), get_listitem_from_episode(ep)))

    return list_of_li


def get_file_id_from_ep_id(ep_id: int) -> List[api2models.RawFile]:
    q = api2.QueryOptions()
    q.id = ep_id
    q.level = 1
    x = api.episode_get(q)
    return x.files
