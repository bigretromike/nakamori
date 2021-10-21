# -*- coding: utf-8 -*-
from api.shoko.v2 import api2, api2models
import xbmc
import xbmcaddon
from xbmcgui import ListItem
import xbmcplugin
import sys
import re
import routing

from lib.kodi_utils import bold
from lib.shoko_utils import get_tag_setting_flag
from typing import List, Tuple
from lib.naka_utils import ThisType, WatchedStatus, map_episodetype_to_thistype, map_filter_group_to_thistype
import os
import lib.favorite as favorite

plugin = routing.Plugin()
plugin_addon = xbmcaddon.Addon('plugin.video.nakamori')
#plugin_img_path = os.path.join(xbmcaddon.Addon(id=plugin_addon.getSetting('icon_pack')).getAddonInfo('path'), 'resources', 'media')
plugin_img_path = os.path.join(xbmcaddon.Addon(id='plugin.video.nakamori').getAddonInfo('path'), 'resources', 'media')

http = f"http://{plugin_addon.getSetting('ipaddress')}:{plugin_addon.getSettingInt('port')}"

api = api2.Client(address=plugin_addon.getSetting('ipaddress'),
                  port=plugin_addon.getSettingInt('port'),
                  apikey=plugin_addon.getSetting('apikey'),
                  timeout=plugin_addon.getSettingInt('timeout'))


def get_listitem_from_filter(x: api2models.Filter) -> ListItem:
    url = f'/filter/{x.id}'
    name = x.name
    name = bold(name)
    li = ListItem(name, path=url)

    if x.art is not None:
        set_art(li, x.art)
    set_folder(li, True)

    set_info_for_filter(li, x)

    #add_context_menu(li, {})  # TODO
    set_property(li, 'IsPlayable', False)
    set_path(li, url)  # TODO

    return li


def get_listitem_from_serie(x: api2models.Serie) -> ListItem:
    url = f'/serie/{x.id}'
    name = x.name
    # name = bold(name)
    li = ListItem(label=name, offscreen=True)

    if x.art is not None:
        set_art(li, x.art)
    set_folder(li, True)
    set_unieque_ids(li, x.aid)
    votes = int(x.votes) if x.votes is not None else 0
    set_rating(li, rate_type='anidb', rate_value=float(x.rating), votes=int(votes), default=True)
    # add_season(li, season_name='__season__', season_number=1)
    set_info_for_series(li, x)
    set_cast(li, get_cast(x.roles))
    if not favorite.check_in_database(x.id):
        add_fav = (plugin_addon.getLocalizedString(30212), f'RunScript(plugin.video.nakamori, /dialog/favorites/{x.id}/add)')
    else:
        add_fav = (plugin_addon.getLocalizedString(30213), f'RunScript(plugin.video.nakamori, /dialog/favorites/{x.id}/remove)')
    add_context_menu(li, [add_fav])
    set_property(li, 'IsPlayable', False)
    watched = 0
    if x.watched_sizes.Episodes is not None:
        watched = x.watched_sizes.Episodes
    total = 0
    if x.total_sizes.Episodes is not None:
        total = x.total_sizes.Episodes
    set_property(li, 'TotalEpisodes', str(total))
    set_property(li, 'WatchedEpisodes', str(watched))
    set_property(li, 'UnWatchedEpisodes', str(total - watched))
    set_path(li, url)  # TODO

    return li


def get_listitem_from_group(x: api2models.Group) -> ListItem:
    url = f'/group/{x.id}'
    name = x.name
    name = bold(name)
    li = ListItem(name, path=url)

    if x.art is not None:
        set_art(li, x.art)
    set_folder(li, True)

    set_rating(li, rate_type='anidb', rate_value=float(x.rating), votes=int(x.votes), default=True)
    # add_season(li, season_name='__season__', season_number=1)
    set_info_for_group(li, x)
    set_cast(li, get_cast(x.roles))
    # add_context_menu(li, {})  # TODO
    set_property(li, 'IsPlayable', False)
    set_path(li, url)  # TODO

    return li


def get_listitem_from_episode(x: api2models.Episode, series_title: str = '', cast: List[api2models.Role] = None) -> ListItem:
    url = f'/ep/{x.eid}'
    name = x.name
    li = ListItem(name, path=url)

    set_category(series_title)
    set_content('episodes')
    if x.art is not None:
        set_art(li, x.art)
    set_folder(li, False)
    set_unieque_ids(li, x.aid)
    set_rating(li, rate_type='anidb', rate_value=float(x.rating), votes=int(x.votes), default=True)
    #add_season(li, season_name='__season__', season_number=1)
    set_info_for_episode(li, x, series_title)
    set_cast(li, get_cast(cast))
    # add_context_menu(li, {})  # TODO
    set_property(li, 'IsPlayable', True)
    set_path(li, url)  # TODO

    return li


def get_cast(c: List[api2models.Role]) -> List[dict]:
    roles = []
    use_seiyuu = plugin_addon.getSettingBool('use_seiyuu_pic')
    for role in c:
        pic = role.character_image
        if use_seiyuu:
            pic = role.staff_image
        #roles.append({"name": role.staff, "role": f'{role.character} ({role.role})', "thumbnail": http + pic})
        roles.append({"name": role.staff, "role": role.character, "thumbnail": http+pic})
    return roles


def get_tags(s: List[str]):
    if s is None:
        return ''
    if len(s) == 0:
        return ''
    short_tag = plugin_addon.getSetting('short_tag_list') == 'true'
    temp_genres = []
    current_length = 0
    # the '3' here is because the separator ' | ' is 3 chars
    for tag in s:
        if short_tag and current_length + len(tag) + 3 > 50:
            break
        temp_genres.append(tag)
        current_length += len(tag) + 3
    return temp_genres


def color(text_to_color: str, color_name: str):
    return ''.join(['[COLOR %s]' % color_name, text_to_color, '[/COLOR]'])


def title_coloring(title, episode_count, total_count, special_count, total_special_count, airing=False, is_movie=False):
    color_title = title
    if not plugin_addon.getSettingBool('color_title') or is_movie:  # skip movies (they like to have parts)
        return color_title

    color_format = '[COLOR %s]%s[/COLOR]'
    if airing:
        color_name = plugin_addon.getSetting('title_color_airing')
        color_special = plugin_addon.getSetting('title_color_airing_special')
        color_missing = plugin_addon.getSetting('title_color_airing_missing')
    else:
        color_name = plugin_addon.getSetting('title_color_finish')
        color_special = plugin_addon.getSetting('title_color_finish_special')
        color_missing = plugin_addon.getSetting('title_color_finish_missing')

    if episode_count is None:
        episode_count = 0
    if total_count is None:
        total_count = 0
    if special_count is None:
        special_count = 0
    if total_special_count is None:
        total_special_count = 0

    if episode_count == total_count:
        if total_special_count == 0:
            return color_format % (color_name, title)
        if special_count >= total_special_count:
            return color_format % (color_special, title)
        if special_count < total_special_count:
            return color_format % (color_name, title)
    elif episode_count < total_count:
        return color_format % (color_missing, title)

    return color_title


def get_proper_title(s: api2models.Serie) -> str:
    use_server_title = plugin_addon.getSettingBool("use_server_title")
    this_type = plugin_addon.getSetting("title_type").lower()
    this_lang = plugin_addon.getSetting("displaylang").lower()
    t = ''

    list_of_good_titles = []
    if not use_server_title:
        for tt in s.titles:
            if tt.Language.lower() == this_lang:
                list_of_good_titles.append(tt)
            if tt.Type.lower() == this_type:
                if tt not in list_of_good_titles:
                    list_of_good_titles.append(tt)
                else:
                    # if we added good langauge already and its in good type then we have a winner
                    break
        # no matter what pick first on the list
        t = list_of_good_titles[0].Title
    else:
        t = s.name
    # We need to assume not airing, as there is no end date provided in API
    return title_coloring(t, s.local_sizes.Episodes, s.total_sizes.Episodes, s.local_sizes.Specials, s.total_sizes.Specials, False, is_movie=True if s.ismovie == 1 else False)


def set_category(category: str):
    xbmcplugin.setPluginCategory(int(sys.argv[1]), category)


def set_content(content_type: str = ''):
    # files, movies, videos, tvshows, episodes, artists ...
    xbmcplugin.setContent(int(sys.argv[1]), content_type)


def set_watched_flags(li: ListItem, infolabels, flag: WatchedStatus, resume_time=0):
    if flag == WatchedStatus.UNWATCHED:
        infolabels['playcount'] = 0
        infolabels['overlay'] = 4
    elif flag == WatchedStatus.WATCHED:
        infolabels['playcount'] = 1
        infolabels['overlay'] = 5
    elif flag == WatchedStatus.PARTIAL and plugin_addon.getSetting('file_resume') == 'true':
        li.setProperty('ResumeTime', str(resume_time))


def resume(li: ListItem):
    resume = li.getProperty('ResumeTime')
    if resume is None or resume == '':
        return
    li.setProperty('StartOffset', resume)


def is_series_watched(s: api2models.Serie) -> WatchedStatus:
    local_only = plugin_addon.getSetting('local_total') == 'true'
    no_specials = plugin_addon.getSetting('ignore_specials_watched') == 'true'
    sizes = s.watched_sizes
    if sizes is None:
        return WatchedStatus.UNWATCHED
    # count only local episodes
    if local_only and no_specials:
        # 0 is unwatched
        if s.viewed == 0:
            return WatchedStatus.UNWATCHED
        # Should never be greater, but meh
        if sizes.Episodes >= s.local_sizes.Episodes:
            return WatchedStatus.WATCHED
        # if it's between 0 and total, then it's partial
        return WatchedStatus.PARTIAL

    # count local episodes and specials
    if local_only:
        # 0 is unwatched
        if (sizes.Episodes + sizes.Specials) == 0:
            return WatchedStatus.UNWATCHED
        # Should never be greater, but meh
        if (sizes.Episodes + sizes.Specials) >= (s.local_sizes.Episodes + s.local_sizes.Specials):
            return WatchedStatus.WATCHED
        # if it's between 0 and total, then it's partial
        return WatchedStatus.PARTIAL

    # count episodes, including ones we don't have
    if no_specials:
        # 0 is unwatched
        if sizes.Episodes == 0:
            return WatchedStatus.UNWATCHED
        # Should never be greater, but meh
        if sizes.Episodes >= s.total_sizes.Episodes:
            return WatchedStatus.WATCHED
        # if it's between 0 and total, then it's partial
        return WatchedStatus.PARTIAL

    # count episodes and specials, including ones we don't have
    # 0 is unwatched
    if (sizes.Episodes + sizes.Specials) == 0:
        return WatchedStatus.UNWATCHED
    # Should never be greater, but meh
    if (sizes.Episodes + sizes.Specials) >= (s.total_sizes.Episodes + s.total_sizes.Specials):
        return WatchedStatus.WATCHED
    # if it's between 0 and total, then it's partial
    return WatchedStatus.PARTIAL


def set_watch_mark(mark_type: ThisType = ThisType.episode, mark_id: int = 0, watched: bool = True):
    if plugin_addon.getSetting('watchedbox') == 'true':
        msg = plugin_addon.getLocalizedString(30201) + ' ' + (plugin_addon.getLocalizedString(30202) if watched else plugin_addon.getLocalizedString(30203))
        xbmc.executebuiltin('XBMC.Notification(' + plugin_addon.getLocalizedString(30200) + ', ' + msg + ', 2000, ' + plugin_addon.getAddonInfo('icon') + ')')


def get_infolabels(x: api2models.Filter):
    return {'Title': x.name, 'Plot': x.name}


def set_art(li: ListItem, art: api2models.ArtCollection, overwrite_image: str = None):
    # thumb, poster, banner, fanart, clearart, clearlogo, landscape, icon
    http = "http://" + plugin_addon.getSetting('ipaddress') + ":" + str(plugin_addon.getSettingInt('port')) + "{}"
    if art is None:
        art = api2models.ArtCollection()

    if overwrite_image is not None:
        if os.path.exists(os.path.join(plugin_img_path, 'thumb', overwrite_image)):
            li.setArt({'thumb': os.path.join(plugin_img_path, 'thumb', overwrite_image)})
        if os.path.exists(os.path.join(plugin_img_path, 'poster', overwrite_image)):
            li.setArt({'banner': os.path.join(plugin_img_path, 'poster', overwrite_image)})
        if os.path.exists(os.path.join(plugin_img_path, 'banners', overwrite_image)):
            li.setArt({'banner': os.path.join(plugin_img_path, 'banners', overwrite_image)})
        if os.path.exists(os.path.join(plugin_img_path, 'backgrounds', overwrite_image)):
            li.setArt({'fanart': os.path.join(plugin_img_path, 'backgrounds', overwrite_image)})
        if os.path.exists(os.path.join(plugin_img_path, 'clearart', overwrite_image)):
            li.setArt({'icon': os.path.join(plugin_img_path, 'clearart', overwrite_image)})
        if os.path.exists(os.path.join(plugin_img_path, 'clearlogo', overwrite_image)):
            li.setArt({'icon': os.path.join(plugin_img_path, 'clearlogo', overwrite_image)})
        if os.path.exists(os.path.join(plugin_img_path, 'icons', overwrite_image)):
            li.setArt({'icon': os.path.join(plugin_img_path, 'icons', overwrite_image)})

    else:
        if len(art.fanart) > 0:
            li.setArt({'fanart': http.format(art.fanart[0].url), 'clearart': http.format(art.fanart[0].url)})
        if len(art.thumb) > 0:
            li.setArt({'thumb': http.format(art.thumb[0].url)})
            li.setArt({'icon': http.format(art.thumb[0].url)})
            li.setArt({'poster': http.format(art.thumb[0].url)})
        if len(art.banner) > 0:
            li.setArt({'banner': http.format(art.banner[0].url)})

    # TODO need to play with this a little more
    # if kodi_utils.get_cond_visibility('System.HasAddon(resource.images.studios.white)') == 1:
    #    if hasattr(self, 'studio'):
    #        icon = 'resource://resource.images.studios.white/{studio}.png'.format(studio=self.studio)


def set_folder(li: ListItem, is_folder: bool = True):
    li.setIsFolder(is_folder)


def set_unieque_ids(li: ListItem, anidb_id=None):
    if anidb_id is not None:
        li.setUniqueIDs({'anidb': anidb_id})


def set_rating(li: ListItem, rate_type: str, rate_value: float, votes: int = 0, default: bool = False):
    # anidb, tmdb, tvdb, imdb
    li.setRating(rate_type, rate_value, votes, default)


def add_season(li: ListItem, season_name: str = '', season_number: int = 0):
    li.addSeason(season_number, season_name)


def set_as_selected(li: ListItem):
    li.select(True)


def is_this_selected(li: ListItem) -> bool:
    return li.isSelected()


def set_info_for_episode(li: ListItem, x: api2models.Episode, series_title: str):
    # 'general': count (counter), size (file), date (file)
    # ICONS
    # Value 0 - No overlay icon.
    # Value 1 - Compressed *.rar files.
    # Value 2 - Compressed *.zip files.
    # Value 3 - Locked files.
    # Value 4 - For not watched files.
    # Value 5 - For seen files.
    # Value 6 - Is on hard disk stored.
    # 'video': genre (str, list[str]), country (str, list[str]), year, episode, season, sortepisode, sortseason, setid, tracknumber
    # episodeguide (str), showlink (str), plot, plotoutline (short-plot), title, originaltitle, sorttitle, studio, tagline (short descipt)
    # rating (float), userrating (int), playcount, overlay 0-7, duration (sec)
    # cast (list[str] list[tuple(str,str)])
    # writer, tvshowtitle, premiered (yyyy-mm-dd), status (Continuing), set (name of collection ? group ? ), setoverview
    # tag (str, list[str]), dateadded (yyyy-mm-dd hh:mm:ss), lastplayed (yyyy-mm-dd hh:mm:ss)
    # imdbnumber (str), code, aired (yyyy-mm-dd), credits (str, list[str]), votes (12345 votes)
    # path (file/path.avi), trailer (file/path.traile.avi), dbid (int --- dont add this )
    # mediatype ("video", "movie", "tvshow", "season", "episode", "musicvideo")
    title = x.name
    if plugin_addon.getSettingBool('addepnumber'):
        title = f'{x.epnumber:02d}. {x.name}'
    video = {'aired': x.air,
             'year': x.year,
             'episode': int(x.epnumber),
             'sortepisode': int(x.epnumber),
             'plot': x.summary,
             'title': title,
             'originaltitle': title,
             'sorttitle': f'{x.epnumber:04d} {x.name}',
             'tvshowtitle': series_title,
             'mediatype': 'episode',
             'season': 1,
             'sortseason': 1,
             'rating': float(x.rating),
             'votes': str(x.votes),
             'lastplayed': str(x.view_date) + ' 00:00:00',
             'playcount': 0,
             'overlay': 4
             }
    if x.eptype.lower() != 'episode':
        # 0 - specials
        video['season'] = 0
        video['sortseason'] = 0
    if x.userrating is not None:
        video['userrating'] = int(x.userrating)
    if x.view == 1:
        video['playcount'] = 1
        video['overlay'] = 5
    li.setInfo('video', video)


def set_info_for_group(li: ListItem, x: api2models.Group):
    title = get_proper_title(x)
    summary = make_text_nice(x.summary)
    video = {'aired': x.air,
             'year': x.year,
             'plot': summary,
             'plotoutline': " ".join(summary.split(".", 3)[:2]),
             'title': title,
             'originaltitle': title,
             'sorttitle': title,
             'tvshowtitle': title,
             'mediatype': 'tvshow',
             #'season': '1',
             #'sortseason': '1',
             'rating': float(x.rating),
             'premiered': x.air,
             'tag': get_tags(x.tags),
             'votes': str(x.votes)}
    if x.userrating is not None:
        video['userrating'] = int(x.userrating)
    li.setInfo('video', video)


def set_info_for_series(li: ListItem, x: api2models.Serie):
    # Kodi 20 improvment: https://github.com/xbmc/xbmc/pull/19459
    title = get_proper_title(x)
    summary = make_text_nice(x.summary)
    video = {'aired': x.air,
             'year': x.year,
             'plot': summary,
             'plotoutline': " ".join(summary.split(".", 3)[:2]),
             'title': title,
             'originaltitle': title,
             'sorttitle': title,
             'tvshowtitle': title,
             'mediatype': 'tvshow',
             'rating': float(x.rating),
             'premiered': x.air,
             'tag': get_tags(x.tags),
             'votes': str(x.votes)}
    if x.userrating is not None:
        video['userrating'] = int(x.userrating)
    video['mediatype'] = 'tvshow'
    if x.ismovie == 1:
        video['mediatype'] = 'movie'

    li.setInfo('video', infoLabels=video)


def set_info_for_filter(li: ListItem, x: api2models.Filter):
    title = x.name
    video = {'title': title,
             'originaltitle': title,
             'sorttitle': title,
             'tvshowtitle': title,
             'mediatype': 'tvshow'}

    li.setInfo('video', video)


def set_cast(li: ListItem, actors: List[dict]):
    # actors = [{"name": "name", "role": "role", "thumbnail": "http://.jpg"}]
    li.setCast(actors)


def set_stream_info(li: ListItem, r: api2models.RawFile):
    for a in r.media.audios:
        audio = {'codec': a.Codec, 'language': a.Language, 'channels': a.Channels}
        li.addStreamInfo('audio', audio)
    for v in r.media.videos:
        video = {'codes': v.Codec, 'width': v.Width, 'heigh': v.Height, 'duration': v.Duration}
        li.addStreamInfo('video', video)
    for s in r.media.subtitles:
        subtitle = {'language': s.Language}
        li.addStreamInfo('subtitle', subtitle)


def add_context_menu(li: ListItem, menu: List[Tuple[str, str]]):
    li.addContextMenuItems(menu)


def set_property(li: ListItem, name, value):
    # IsPlayable  mandatory for playable items
    # ResumeTime  float
    # StartOffset (float) or StartPercent (float)
    # TotalTime (float)
    li.setProperty(name, str(value))
    # or li.setProperties({'key': 'value', 'key2': 'value2'})


def set_path(li: ListItem, path: str):
    li.setPath(path=path)


def search_box():
    """
    Shows a keyboard, and returns the text entered
    :return: the text that was entered
    """
    keyb = xbmc.Keyboard('', plugin_addon.getLocalizedString(30026))
    keyb.doModal()
    search_text = ''

    if keyb.isConfirmed():
        search_text = keyb.getText()
    return search_text


def show_search_result_menu(query: str) -> List[api2models.Serie]:
    list_of_series = []
    q = api2models.QueryOptions()
    q.query = query
    q.level = 0  # no need for eps
    q.allpics = 1
    f = api.search(q)

    for g in f.groups:
        for s in g.series:
            list_of_series.append(s)
    return list_of_series


@plugin.route('/recent')
def show_added_recently_menu():
    pass

@plugin.route('/calendar')
def show_calendar_menu():
    pass

@plugin.route('/calendar2')
def url_calendar():
    pass

@plugin.route('/settings')
def show_setting_menu():
    pass

@plugin.route('/shoko')
def show_shoko_menu():
    pass


def main_menu_items() -> List[ListItem]:
    # { 'Favorites', 'Added Recently v2': 0, 'Airing Today': 1, 'Calendar': 1, 'Seasons': 2, 'Years': 3, 'Tags': 4,
    # 'Unsort': 5, 'Settings' (both): 7, 'Shoko Menu': 8, 'Search': 9, Experiment: 99}

    items: List[ListItem] = []
    img = plugin_img_path + '/%s/%s'

    if plugin_addon.getSettingBool('show_favorites'):
        name = color(plugin_addon.getLocalizedString(30211), plugin_addon.getSetting('color_favorites'))
        if plugin_addon.getSettingBool('bold_favorites'):
            name = bold(name)
        item = ListItem(name, path='plugin://plugin.video.nakamori/favorites')
        img_name = 'airing.png'
        item.setArt({'fanart': img % ('backgrounds', img_name), 'banners': img % ('banners', img_name), 'poster': img % ('icons', img_name)})
        items.append(item)

    if plugin_addon.getSettingBool('show_recent2'):
        name = color(plugin_addon.getLocalizedString(30170), plugin_addon.getSetting('color_recent2'))
        if plugin_addon.getSettingBool('bold_recent2'):
            name = bold(name)
        item = ListItem(name, path='plugin://plugin.video.nakamori/recent')
        img_name = '/airing.png'
        item.setArt({'fanart': img % ('backgrounds', img_name), 'banners': img % ('banners', img_name), 'poster': img % ('icons', img_name)})
        items.append(item)

    # TODO airing today
    # if plugin_addon.getSetting('show_airing_today') == 'true':
    #    name = kodi_utils.color(plugin_localize(30211), plugin_addon.getSetting('color_favorites'), color)
    #    item = CustomItem(plugin_localize(30223), 'airing.png', url_for(show_airing_today_menu))
    #    item.sort_index = 1
    #    items.append(item)

    if plugin_addon.getSettingBool('show_calendar'):
        name = color(plugin_addon.getLocalizedString(30222), plugin_addon.getSetting('color_calendar'))

        if plugin_addon.getSettingBool('bold_calendar'):
            name = bold(name)
        if plugin_addon.getSettingBool('calendar_basic') == 'true':
            item = ListItem(name, path='plugin://plugin.video.nakamori/calendar_classic')
            # isfolter
        else:
            item = ListItem(name, path='plugin://plugin.video.nakamori/calendar')
        img_name = 'calendar.png'
        item.setArt({'fanart': img % ('backgrounds', img_name), 'banners': img % ('banners', img_name), 'poster': img % ('icons', img_name)})
        items.append(item)

    if plugin_addon.getSettingBool('show_settings'):
        name = color(plugin_addon.getLocalizedString(30107), plugin_addon.getSetting('color_settings'))
        if plugin_addon.getSettingBool('bold_settings'):
            name = bold(name)
        item = ListItem(name, path='plugin://plugin.video.nakamori/settings')
        img_name = 'settings.png'
        item.setArt({'fanart': img % ('backgrounds', img_name), 'banners': img % ('banners', img_name), 'poster': img % ('icons', img_name)})
        items.append(item)

    if plugin_addon.getSettingBool('show_shoko'):
        name = color(plugin_addon.getLocalizedString(30115), plugin_addon.getSetting('color_shoko'))
        if plugin_addon.getSettingBool('bold_shoko'):
            name = bold(name)
        item = ListItem(name, path='plugin://plugin.video.nakamori/shoko')
        img_name = 'settings.png'
        item.setArt({'fanart': img % ('backgrounds', img_name), 'banners': img % ('banners', img_name), 'poster': img % ('icons', img_name)})
        items.append(item)

    if plugin_addon.getSettingBool('show_search'):
        name = color(plugin_addon.getLocalizedString(30221), plugin_addon.getSetting('color_search'))
        if plugin_addon.getSettingBool('bold_search'):
            name = bold(name)
        item = ListItem(name, path='plugin://plugin.video.nakamori/search')
        img_name = 'search.png'
        item.setArt({'fanart': img % ('backgrounds', img_name), 'banners': img % ('banners', img_name), 'poster': img % ('icons', img_name)})
        items.append(item)

    return items


def list_all_favorites() -> List[Tuple[int, ListItem]]:
    list_of_li = []
    favorite_history = favorite.get_all_favorites()
    q = api2models.QueryOptions()
    q.level = 1
    q.allpics = 1
    for ss in favorite_history:
        q.id = ss[0]
        s = api.series_get_by_id(q)
        li = get_listitem_from_serie(s)
        remove_item = (plugin_addon.getLocalizedString(30213), f'RunScript(plugin.video.nakamori, /dialog/favorite/{q.id}/remove)')
        li.addContextMenuItems([remove_item])
        list_of_li.append((q.id, li))
    return list_of_li


def list_all_filters() -> List[Tuple[int, ThisType, ListItem]]:
    """
    Get All Filters for current User
    :return: List[(int, ListItem)]
    """
    list_of_listitems = []
    q = api2.QueryOptions()
    # get images
    q.allpics = 1
    q.level = 0
    q.tagfilter = get_tag_setting_flag()
    x = api.filter(q)
    set_category('')
    set_content('tvshows')

    show_unsort = plugin_addon.getSettingBool('show_unsort')

    for d in x.filters:
        if d.name == "Unsorted" and not show_unsort:
            continue
        elif d.name == "Continue Watching (SYSTEM)":
            d.name = "Continue Watching"
        elif d.name == "TvDB/MovieDB Link Missing":
            continue
        list_of_listitems.append((d.id, map_filter_group_to_thistype(d.type), get_listitem_from_filter(d)))

    return list_of_listitems


def list_all_filter_by_filters_id(id: int) -> List[Tuple[int, ThisType, ListItem]]:
    list_of_li = []
    q = api2.QueryOptions()
    q.id = id
    q.level = 1
    q.tagfilter = get_tag_setting_flag()
    x = api.filter(q)
    set_category(x.name)
    set_content('tvshows')

    for f in x.filters:
        list_of_li.append((f.id, map_filter_group_to_thistype(f.type), get_listitem_from_filter(f)))

    return list_of_li


def list_all_groups_by_filter_id(id: int) -> List[Tuple[int, ThisType, ListItem]]:
    list_of_listitems = []
    q = api2.QueryOptions()
    q.id = id
    q.level = 2  # 1 - empty series
    q.tagfilter = get_tag_setting_flag()
    x = api.filter(q)

    set_category(x.name)
    set_content('tvshows')

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
    q.level = 1
    q.tagfilter = get_tag_setting_flag()
    x = api.filter(q)

    for s in x.groups:
        list_of_listitems.append((s.id, get_listitem_from_group(s)))

    return list_of_listitems


def list_episodes_for_series_by_series_id(s_id: int) -> List[Tuple[int, ThisType, ListItem]]:
    list_of_li = []
    q = api2.QueryOptions()
    q.allpics = 1
    q.id = s_id
    q.level = 1
    q.tagfilter = get_tag_setting_flag()
    x = api.series_get_by_id(q)

    series_title = get_proper_title(x)

    for ep in x.eps:
        list_of_li.append((ep.id, map_episodetype_to_thistype(ep.eptype), get_listitem_from_episode(ep, series_title, x.roles)))

    return list_of_li


def get_file_id_from_ep_id(ep_id: int) -> List[api2models.RawFile]:
    q = api2.QueryOptions()
    q.id = ep_id
    q.level = 1
    q.tagfilter = get_tag_setting_flag()
    x = api.episode_get(q)
    return x.files


def set_sorting_method(x: ThisType):
    if x == ThisType.episode:
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_UNSORTED)
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_EPISODE)
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_TITLE)
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_YEAR)
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_RATING)
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_DATE)

        sort_episodes = plugin_addon.getSetting('default_sort_episodes')
        sort = 0
        if sort_episodes == 'Server':
            sort = int(xbmcplugin.SORT_METHOD_UNSORTED)
        if sort_episodes == 'Title':
            sort = int(xbmcplugin.SORT_METHOD_TITLE)
        if sort_episodes == 'Date':
            sort = int(xbmcplugin.SORT_METHOD_DATE)
        if sort_episodes == 'Rating':
            sort = int(xbmcplugin.SORT_METHOD_VIDEO_RATING)
        if sort_episodes == 'Year':
            sort = int(xbmcplugin.SORT_METHOD_VIDEO_YEAR)
        if sort_episodes == 'Episode':
            sort = int(xbmcplugin.SORT_METHOD_EPISODE)
        xbmc.executebuiltin(f'Container.SetSortMethod({sort})')

    elif x == ThisType.series or x == ThisType.filter or x == ThisType.group:
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_UNSORTED)
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE_IGNORE_THE)
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_YEAR)
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_RATING)
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_DATE)

        sort_series = plugin_addon.getSetting('default_sort_series')
        sort = 0
        if sort_series == 'Server':
            sort = int(xbmcplugin.SORT_METHOD_UNSORTED)
        if sort_series == 'Title':
            sort = int(xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE_IGNORE_THE)
        if sort_series == 'Date':
            sort = int(xbmcplugin.SORT_METHOD_DATE)
        if sort_series == 'Rating':
            sort = int(xbmcplugin.SORT_METHOD_VIDEO_RATING)
        if sort_series == 'Year':
            sort = int(xbmcplugin.SORT_METHOD_VIDEO_YEAR)
        xbmc.executebuiltin(f'Container.SetSortMethod({sort})')
    else:
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_NONE)


def make_text_nice(data: str = ''):
    """
    Make any anidb text look nice, clean and sleek by removing links, annotations, comments, empty lines
    :param data: text that is too ugly to be shown
    :return: text that is a bit nicer
    """
    data = remove_anidb_links(data)
    # the only one I could care to make settings if someone ask for
    data = remove_anidb_annotations(data)
    data = remove_anidb_comments(data)
    data = remove_multi_empty_lines(data)
    return data


def remove_anidb_links(data=''):
    """
    Remove anidb links from descriptions
    Args:
        data: the strong to remove links from
    Returns: new string without links
    """
    p = re.compile(r'(https?://anidb\.net/[0-9A-z/\-_.?=&]+[ ]*\[)([\S ]+?)(\])')
    return p.sub(r'\2', data)


def remove_anidb_comments(data=''):
    """
    Remove comments that topically start with *, --, ~ from description
    :param data: text to clean
    :return: text after clean
    """
    data = re.sub(r'^(\*|--|~) .*', "", data, flags=re.MULTILINE)
    return data.strip(" \n")


def remove_anidb_annotations(data=''):
    """
    Remove annotations containing Source, Note, Summary from description
    :param data: text to clean
    :return: text after clean
    """
    data = re.sub(r'\n(Source|Note|Summary):.*', "", data, flags=re.DOTALL)
    return data.strip(" \n")


def remove_multi_empty_lines(data=''):
    """
    Remove multiply empty lines to save some space
    :param data: text to clean
    :return: text after clean
    """
    data = re.sub(r'\n\n+', r'\n\n', data)
    return data.strip(" \n")
