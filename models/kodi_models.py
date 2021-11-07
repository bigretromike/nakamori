# -*- coding: utf-8 -*-
from api.shoko.v2 import api2, api2models
import xbmc
import xbmcaddon
import xbmcgui
from xbmcgui import ListItem
import xbmcplugin
import re
import routing

from lib.kodi_utils import bold
from lib.shoko_utils import get_tag_setting_flag
from typing import List, Tuple
from lib.naka_utils import ThisType, WatchedStatus, map_episodetype_to_thistype, map_filter_group_to_thistype, map_thitype_to_eptype
import os
import lib.favorite as favorite
import lib.cache as cache

plugin = routing.Plugin()
plugin_addon = xbmcaddon.Addon('plugin.video.nakamori')

plugin_img_path = os.path.join(xbmcaddon.Addon(id='plugin.video.nakamori').getAddonInfo('path'), 'resources', 'media')
if xbmc.getCondVisibility(f'System.HasAddon({plugin_addon.getSetting("icon_pack")})'):
    plugin_img_path = os.path.join(xbmcaddon.Addon(plugin_addon.getSetting('icon_pack')).getAddonInfo('path'), 'resources', 'media')

http = "http://" + plugin_addon.getSetting('ipaddress') + ":" + str(plugin_addon.getSettingInt('port')) + "%s"

api = api2.Client(address=plugin_addon.getSetting('ipaddress'),
                  port=plugin_addon.getSettingInt('port'),
                  apikey=plugin_addon.getSetting('apikey'),
                  timeout=plugin_addon.getSettingInt('timeout'))
xbmc.log(f'=== enabling cache: {plugin_addon.getSettingBool("enableCache")} ===', xbmc.LOGDEBUG)
api.set_cache(plugin_addon.getSettingBool('enableCache'))


def spoiler_control_unwatched_ep_title(title: str, hide: bool, this_type: ThisType) -> str:
    spoiler = 'spoiler'
    if hide and not plugin_addon.getSetting('hide_title').lower() == 'never':
        if plugin_addon.getSetting('hide_title').lower() == 'both':
            return spoiler
        elif plugin_addon.getSetting('hide_title').lower() == map_thitype_to_eptype(this_type):
            return spoiler
    return title


def spoiler_control_ratings(rating, hide: bool, this_type: ThisType):
    hidden_rating = 0
    if hide and not plugin_addon.getSetting('hide_rating').lower() == 'never':
        if plugin_addon.getSetting('hide_rating').lower() == "both":
            return hidden_rating
        elif plugin_addon.getSetting('hide_rating').lower() == map_thitype_to_eptype(this_type):
            return hidden_rating
    return rating


def spoiler_control_images(art: api2models.ArtCollection, hide: bool) -> api2models.ArtCollection:
    if hide and plugin_addon.getSettingBool('hide_images'):
        return api2models.ArtCollection(thumb=[api2models.Art(index=0, url=os.path.join(plugin_img_path, 'icons', 'hidden.png'))])
    return art


def spoiler_control_plot(plot: str, hide: bool) -> str:
    if hide and plugin_addon.getSettingBool('hide_plot'):
        plot = 'No spoilers...'
    return plot


def get_listitem_from_filter(x: api2models.Filter) -> ListItem:
    name = x.name
    if plugin_addon.getSettingBool('bold_filters'):
        name = bold(name)
    li = ListItem(name)

    if x.art is not None:
        set_art(li, x.art)
    set_folder(li, True)

    set_info_for_filter(li, x)

    #add_context_menu(li, {})  # TODO
    set_property(li, 'IsPlayable', False)
    # set_path(li, url)  # TODO

    return li


def get_listitem_from_serie(x: api2models.Serie, forced_title: str = None) -> ListItem:
    name = x.name
    li = ListItem(label=name, offscreen=True)

    if x.art is not None:
        set_art(li, x.art)
    set_folder(li, True)
    set_unieque_ids(li, x.aid)
    rating = x.rating if x.rating is not None else 0
    votes = int(x.votes) if x.votes is not None else 0
    set_rating(li, rate_type='anidb', rate_value=float(rating), votes=int(votes), default=True)
    # add_season(li, season_name='__season__', season_number=1)
    was_watched = is_series_watched(x)
    set_info_for_series(li, x, was_watched, forced_title)
    set_cast(li, get_cast(x.roles))

    add_context_menu_for_series(li, x, was_watched)

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

    # set_path(li, url)  # TODO

    return li


def get_listitem_from_group(x: api2models.Group) -> ListItem:
    name = x.name
    name = bold(name)
    li = ListItem(name, offscreen=True)

    if x.art is not None:
        set_art(li, x.art)
    set_folder(li, True)

    rating = x.rating if x.rating is not None else 0
    votes = x.votes if x.votes is not None else 0
    set_rating(li, rate_type='anidb', rate_value=float(rating), votes=int(votes), default=True)
    # add_season(li, season_name='__season__', season_number=1)
    set_info_for_group(li, x)
    set_cast(li, get_cast(x.roles))
    # add_context_menu(li, {})  # TODO
    set_property(li, 'IsPlayable', False)
    #set_path(li, url)  # TODO

    return li


def get_listitem_from_episode(x: api2models.Episode, series_title: str = '', cast: List[api2models.Role] = None, series_id: int = -1) -> ListItem:
    is_resume_enabled = plugin_addon.getSettingBool('file_resume')
    name = x.name
    li = ListItem(name, offscreen=True)

    set_category(series_title)

    hide_spoiler = False
    if x.view is None or x.view == 0:
        hide_spoiler = True

    if x.art is not None:
        set_art(li, spoiler_control_images(x.art, hide_spoiler))
    set_folder(li, False)
    set_unieque_ids(li, x.aid)
    # set_rating(li, rate_type='anidb', rate_value=float(x.rating), votes=int(x.votes), default=True)
    #add_season(li, season_name='__season__', season_number=1)
    set_info_for_episode(li, x, series_title)
    if cast is not None:
        set_cast(li, get_cast(cast))

    add_context_menu_for_episode(li, x, series_id)
    set_property(li, 'IsPlayable', True)
    set_property(li, 'TotalTime', 1000000)
    if is_resume_enabled:
        time_to_start = 0
        if x.files is not None:
            if len(x.files) > 0:
                time_to_start = x.files[0].offset if x.files[0].offset is not None else 0
        set_property(li, 'ResumeTime', time_to_start)
    # set_property(li, 'startoffset', str(100))

    #xbmc.log(f'----------- resume support?: {resume}', xbmc.LOGINFO)
    #if resume:
    #    resume = f.offset if f.offset is not None else 0
    #    item.setProperty('ResumeTime', str(resume))
    #    item.setProperty('StartOffset', str(resume))
    #    xbmc.log(f'----------- STARTOFFSET: {resume}', xbmc.LOGINFO)
    #else:
    #    item.setProperty('ResumeTime', '0')
    #    item.setProperty('StartOffset', '0')


    #self.setProperty('ResumeTime', str(resume_time))
    #set_path(li, url)  # TODO

    return li


def get_listitem_from_rawfile(x: api2models.RawFile) -> ListItem:
    name = get_file_name(x.filename)
    li = ListItem(name, path=x.url, offscreen=True)

    set_folder(li, True)
    set_info_for_rawfile(li, x)
    set_stream_info(li, x)
    # add_context_menu(li, [])  #TODO scan etc
    set_property(li, 'IsPlayable', True)
    return li


def get_listitem_from_episodetype(x: ThisType, art: api2models.ArtCollection) -> ListItem:
    name = map_thitype_to_eptype(x)
    li = ListItem(label=name, offscreen=True)
    if plugin_addon.getSettingBool('eptypes_series_art'):
        set_art(li, art)
    else:
        set_art(li, None, f'%s.png' % map_thitype_to_eptype(x))
    set_folder(li, True)
    set_property(li, 'IsPlayable', False)
    return li


def get_cast(c: List[api2models.Role]) -> List[dict]:
    roles = []
    use_seiyuu = plugin_addon.getSettingBool('use_seiyuu_pic')
    for role in c:
        pic = role.character_image
        if use_seiyuu:
            pic = role.staff_image
        roles.append({"name": role.staff, "role": role.character, "thumbnail": set_pic_url(pic)})
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


def get_proper_title(s: api2models.Serie, forced_title: str = None) -> Tuple[str, str]:
    t = forced_title
    if forced_title is None:
        use_server_title = plugin_addon.getSettingBool("use_server_title")
        this_type = plugin_addon.getSetting("title_type").lower()
        this_lang = plugin_addon.getSetting("displaylang").lower()

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
    if type(s) == api2models.Serie:
        is_movie = True if s.ismovie is not None and s.ismovie == 1 else False
    else:
        is_movie = False
    return title_coloring(t, s.local_sizes.Episodes, s.total_sizes.Episodes, s.local_sizes.Specials, s.total_sizes.Specials, False, is_movie=is_movie), t


def set_category(category: str):
    xbmcplugin.setPluginCategory(plugin.handle, category)


def set_content(content_type: str = ''):
    # files, movies, videos, tvshows, episodes, artists ... undocumented: seasons ?
    xbmcplugin.setContent(plugin.handle, content_type)


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
    local_only = plugin_addon.getSettingBool('local_total')
    no_specials = plugin_addon.getSettingBool('ignore_specials_watched')
    sizes = s.watched_sizes
    if sizes is None:
        return WatchedStatus.UNWATCHED

    local_episodes = sizes.Episodes if sizes.Episodes is not None else 0
    local_special = sizes.Specials if sizes.Specials is not None else 0

    all_local_episodes = s.local_sizes.Episodes if s.local_sizes.Episodes is not None else 0
    all_local_specials = s.local_sizes.Specials if s.local_sizes.Specials is not None else 0

    total_episodes = s.total_sizes.Episodes if s.total_sizes.Episodes is not None else 0
    total_specials = s.total_sizes.Specials if s.total_sizes.Specials is not None else 0

    # count only local episodes
    if local_only and no_specials:
        # 0 is unwatched
        if s.viewed == 0:
            return WatchedStatus.UNWATCHED
        # Should never be greater, but meh
        if local_episodes >= all_local_episodes:
            return WatchedStatus.WATCHED
        # if it's between 0 and total, then it's partial
        return WatchedStatus.PARTIAL

    # count local episodes and specials
    if local_only:
        # 0 is unwatched
        if (local_episodes + local_special) == 0:
            return WatchedStatus.UNWATCHED
        # Should never be greater, but meh
        if (local_episodes + local_special) >= (all_local_episodes + all_local_specials):
            return WatchedStatus.WATCHED
        # if it's between 0 and total, then it's partial
        return WatchedStatus.PARTIAL

    # count episodes, including ones we don't have
    if no_specials:
        # 0 is unwatched
        if sizes.Episodes == 0:
            return WatchedStatus.UNWATCHED
        # Should never be greater, but meh
        if sizes.Episodes >= total_episodes:
            return WatchedStatus.WATCHED
        # if it's between 0 and total, then it's partial
        return WatchedStatus.PARTIAL

    # count episodes and specials, including ones we don't have
    # 0 is unwatched
    if (local_episodes + local_special) == 0:
        return WatchedStatus.UNWATCHED
    # Should never be greater, but meh
    if (local_episodes + local_special) >= (total_episodes + total_specials):
        return WatchedStatus.WATCHED
    # if it's between 0 and total, then it's partial
    return WatchedStatus.PARTIAL


def set_watch_mark(mark_type: ThisType = ThisType.episodes, mark_id: int = 0, watched: bool = True):
    if plugin_addon.getSettingBool('syncwatched'):
        if watched:
            if mark_type == ThisType.episodes:
                api.episode_watch(mark_id)
            elif mark_type == ThisType.series:
                api.serie_watch(mark_id)
        else:
            if mark_type == ThisType.episodes:
                api.episode_unwatch(mark_id)
            elif mark_type == ThisType.series:
                api.serie_unwatch(mark_id)

        if plugin_addon.getSetting('watchedbox') == 'true':
            msg = plugin_addon.getLocalizedString(30201) + ' ' + (plugin_addon.getLocalizedString(30202) if watched else plugin_addon.getLocalizedString(30203))
            xbmc.executebuiltin('Notification(' + plugin_addon.getLocalizedString(30200) + ', ' + msg + ', 2000, ' + plugin_addon.getAddonInfo('icon') + ')')

        if plugin_addon.getSettingBool('enableCache'):
            url = cache.get_last()
            xbmc.log(f'=== clear cache for watch mark: {url}', xbmc.LOGINFO)
            cache.remove_cache(url)
        xbmc.executebuiltin('Container.Refresh')


def get_infolabels(x: api2models.Filter):
    return {'Title': x.name, 'Plot': x.name}


def set_pic_url(input: str) -> str:
    if input.__contains__('/'):  # /api/v3/images/...
        return http % input
    elif input.__contains__('\\'):  # C:\\image\\kodi\\...
        return input
    else:  # hidden.jpg
        return http.format(input)


def set_art(li: ListItem, art: api2models.ArtCollection, overwrite_image: str = None):
    # thumb, poster, banner, fanart, clearart, clearlogo, landscape, icon

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
            li.setArt({'fanart': set_pic_url(art.fanart[0].url), 'clearart': set_pic_url(art.fanart[0].url)})
        if len(art.thumb) > 0:
            li.setArt({'thumb': set_pic_url(art.thumb[0].url)})
            li.setArt({'icon': set_pic_url(art.thumb[0].url)})
            li.setArt({'poster': set_pic_url(art.thumb[0].url)})
        if len(art.banner) > 0:
            li.setArt({'banner': set_pic_url(art.banner[0].url)})

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


def set_info_for_rawfile(li: ListItem, x: api2models.RawFile):
    video = {'aired': x.air,
             'year': x.year,
             'plot': x.summary,
             'title': x.filename,
             'originaltitle': x.filename,
             'sorttitle': x.filename,
             'mediatype': 'file',
             'playcount': 0
             }
    li.setInfo('video', video)


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

    spoiler_hide_this = False
    if x.view is None or x.view == 0:
        spoiler_hide_this = True

    ep_type = map_episodetype_to_thistype(x.eptype)
    title = spoiler_control_unwatched_ep_title(x.name, spoiler_hide_this, ep_type)
    sort_title = title
    if plugin_addon.getSettingBool('addepnumber'):
        title = f'{x.epnumber:02d}. {title}'
        sort_title = f'{x.epnumber:04d} {title}'

        if ep_type == ThisType.episodes:
            pass
        elif ep_type == ThisType.specials:
            title = 's' + title
            sort_title = 's' + sort_title
        elif ep_type == ThisType.credits:
            title = 'c' + title
            sort_title = 'c' + sort_title
        elif ep_type == ThisType.parodies:
            title = 'p' + title
            sort_title = 'p' + sort_title
        elif ep_type == ThisType.trailers:
            title = 't' + title
            sort_title = 't' + sort_title
        elif ep_type == ThisType.ova:
            title = 'o' + title
            sort_title = 'o' + sort_title
        elif ep_type == ThisType.webclips:
            title = 'w' + title
            sort_title = 'w' + sort_title
        else:
            title = '*' + title
            sort_title = '*' + sort_title

    video = {'aired': x.air,
             'year': x.year,
             'episode': int(x.epnumber),
             'sortepisode': int(x.epnumber),
             'plot': spoiler_control_plot(x.summary, spoiler_hide_this),
             'title': title,
             'originaltitle': title,
             'sorttitle': sort_title,
             'tvshowtitle': series_title,
             'mediatype': 'episode',
             'season': 1,
             'sortseason': 1,
             'rating': float(spoiler_control_ratings(x.rating, spoiler_hide_this, ThisType.episodes)),
             'votes': str(spoiler_control_ratings(x.votes, spoiler_hide_this, ThisType.episodes)),
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
    title, non_color_title = get_proper_title(x)
    summary = make_text_nice(x.summary)
    video = {'aired': x.air,
             'year': x.year,
             'plot': summary,
             'plotoutline': " ".join(summary.split(".", 3)[:2]),
             'title': title,
             'originaltitle': title,
             'sorttitle': non_color_title,
             'tvshowtitle': title,
             'mediatype': 'tvshow',
             'rating': float(x.rating),
             'premiered': x.air,
             'tag': get_tags(x.tags),
             'votes': str(x.votes)}
    if x.userrating is not None:
        video['userrating'] = int(x.userrating)
    li.setInfo('video', video)


def set_info_for_series(li: ListItem, x: api2models.Serie, is_watched: WatchedStatus, forced_title: str = None):
    # Kodi 20 speed improvment: https://github.com/xbmc/xbmc/pull/19459
    title, non_color_title = get_proper_title(x, forced_title)
    summary = make_text_nice(x.summary)
    video = {'aired': x.air,
             'year': x.year,
             'plot': summary,
             'plotoutline': " ".join(summary.split(".", 3)[:2]),
             'title': title,
             'originaltitle': title,
             'sorttitle': non_color_title,
             'tvshowtitle': title,
             'mediatype': 'tvshow',
             'rating': float(spoiler_control_ratings(x.rating, x.viewed == 0, ThisType.series)),
             'premiered': x.air,
             'tag': get_tags(x.tags),
             'votes': str(spoiler_control_ratings(x.votes, x.viewed == 0, ThisType.series))
             }
    if x.userrating is not None:
        video['userrating'] = int(x.userrating)
    video['mediatype'] = 'tvshow'
    if x.ismovie == 1:
        video['mediatype'] = 'movie'
    li.setLabel(title)
    set_watched_flags(li=li, infolabels=video, flag=is_watched, resume_time=0)
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


def add_context_menu_for_series(li: ListItem, s: api2models.Serie, was_watched: WatchedStatus):
    _menu: List[Tuple[str, str]] = []

    if plugin_addon.getSettingBool('show_favorites'):
        add_fav = (plugin_addon.getLocalizedString(30212), f'RunScript(plugin.video.nakamori, /dialog/favorites/{s.id}/add)')
        if favorite.check_in_database(s.id):
            add_fav = (plugin_addon.getLocalizedString(30213), f'RunScript(plugin.video.nakamori, /dialog/favorites/{s.id}/remove)')
        _menu.append(add_fav)

    if plugin_addon.getSettingBool('context_show_vote_Series'):
        userrate = ''
        if s.userrating is not None and int(s.userrating) > 0:
            userrate = f' ({s.userrating})'
        vote = (plugin_addon.getLocalizedString(30124) + userrate, f'RunScript(plugin.video.nakamori, /dialog/series/{s.id}/vote)')
        _menu.append(vote)

    viewed = (plugin_addon.getLocalizedString(30126), f'RunScript(plugin.video.nakamori, /dialog/series/{s.id}/watched)')
    if was_watched == WatchedStatus.WATCHED:
        viewed = (plugin_addon.getLocalizedString(30127), f'RunScript(plugin.video.nakamori, /dialog/series/{s.id}/unwatched)')
    _menu.append(viewed)

    if plugin_addon.getSettingBool('context_show_info'):
        _menu.append((plugin_addon.getLocalizedString(30123), 'Action(Info)'))

    if plugin_addon.getSettingBool('context_refresh'):
        _menu.append((plugin_addon.getLocalizedString(30131), 'RunScript(plugin.video.nakamori, /dialog/refresh)'))

    # seperate our menu from kodi
    _menu.append(('', ''))
    _menu.append(('', ''))
    _menu.append(('', ''))
    _menu.append((plugin_addon.getLocalizedString(30147), ''))
    li.addContextMenuItems(_menu)


def add_context_menu_for_episode(li: ListItem, e: api2models.Episode, s_id: int):
    # s = get_series_id_from_ep_id(e.id)
    _menu: List[Tuple[str, str]] = []
    if plugin_addon.getSettingBool('context_show_play'):
        _menu.append((plugin_addon.getLocalizedString(30065), f'RunScript(plugin.video.nakamori, /f-0/s-{s_id}/e-{e.id}-play)'))
    if plugin_addon.getSettingBool('context_show_play_no_watch'):
        _menu.append((plugin_addon.getLocalizedString(30132), f'RunScript(plugin.video.nakamori, /f-0/s-{s_id}/e-{e.id}-play/dontmark)'))
    # if plugin_addon.getSettingBool('context_show_force_transcode'):
    # if plugin_addon.getSettingBool('context_show_directplay'):
    # if plugin_addon.getSettingBool('context_show_probe'):
    if plugin_addon.getSettingBool('context_pick_file'):
        _menu.append((plugin_addon.getLocalizedString(30133), f'RunScript(plugin.video.nakamori, /f-0/s-{s_id}/e-{e.id}-pick'))
    # if plugin_addon.getSettingBool('context_playlist'):
    if plugin_addon.getSettingBool('context_show_vote_Episode'):
        userrate = ''
        if e.userrating is not None and int(e.userrating) > 0:
            userrate = f' ({e.userrating})'
        vote = (plugin_addon.getLocalizedString(30125) + userrate, f'RunScript(plugin.video.nakamori, /dialog/episode/{e.id}/vote)')
        # TODO https://github.com/bigretromike/nakamori/issues/464
        # _menu.append(vote)
    if plugin_addon.getSettingBool('context_show_vote_Series'):
        vote = (plugin_addon.getLocalizedString(30124), f'RunScript(plugin.video.nakamori, /dialog/series/{s_id}/vote)')
        _menu.append(vote)

    # watched/unwatched
    viewed = (plugin_addon.getLocalizedString(30128), f'RunScript(plugin.video.nakamori, /dialog/episode/{e.id}/watched)')
    if e.view == 1:
        viewed = (plugin_addon.getLocalizedString(30129), f'RunScript(plugin.video.nakamori, /dialog/episode/{e.id}/unwatched)')
    _menu.append(viewed)

    if plugin_addon.getSettingBool('context_show_info'):
        _menu.append((plugin_addon.getLocalizedString(30123), 'Action(Info)'))

    if plugin_addon.getSettingBool('context_refresh'):
        _menu.append((plugin_addon.getLocalizedString(30131), 'RunScript(plugin.video.nakamori, /dialog/refresh)'))

    # seperate our menu from kodi
    _menu.append(('', ''))
    _menu.append(('', ''))
    _menu.append(('', ''))
    _menu.append((plugin_addon.getLocalizedString(30147), ''))
    li.addContextMenuItems(_menu)


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


def show_search_result_menu(query: str, fuzzy: bool, tag: bool) -> List[api2models.Serie]:
    list_of_series = []
    q = api2models.QueryOptions()
    q.query = query
    if tag:
        q.tags = 1
    q.limit = plugin_addon.getSettingInt('search_maxlimit')
    q.level = 0  # no need for eps
    q.allpics = 1
    q.fuzzy = 0
    if fuzzy:
        q.fuzzy = 1
    f = api.search(q)

    for g in f.groups:
        for s in g.series:
            list_of_series.append(s)
    return list_of_series


def show_az_search_results(query: str) -> List[api2models.Serie]:
    list_of_series = []
    q = api2models.QueryOptions()
    q.query = query
    q.limit = plugin_addon.getSettingInt('search_maxlimit')
    q.level = 0
    q.allpics = 1
    q.fuzzy = 0
    f = api.serie_startswith(q)

    for g in f.groups:
        for s in g.series:
            list_of_series.append(s)
    return list_of_series


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
    #    name = kodi_utils.color(plugin_addon.getLocalizedString(30211), plugin_addon.getSetting('color_favorites'), color)
    #    item = CustomItem(plugin_addon.getLocalizedString(30223), 'airing.png', url_for(show_airing_today_menu))
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


def list_all_filters() -> List[Tuple[int, ThisType, ListItem, str]]:
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

    show_unsort = plugin_addon.getSettingBool('show_unsort')

    for d in x.filters:
        if d.name == "Unsort":
            if not show_unsort:
                continue
            else:
                d.name = color(d.name, plugin_addon.getSetting('color_unsort'))
                if plugin_addon.getSettingBool('bold_unsort'):
                    d.name = bold(d.name)
        elif d.name == "Continue Watching (SYSTEM)":
            d.name = "Continue Watching"
        elif d.name == "TvDB/MovieDB Link Missing":
            continue
        list_of_listitems.append((d.id, map_filter_group_to_thistype(d.type), get_listitem_from_filter(d), d.name))

    return list_of_listitems


def list_all_filter_by_filters_id(id: int) -> List[Tuple[int, ThisType, ListItem]]:
    list_of_li = []
    q = api2.QueryOptions()
    q.id = id
    q.level = 1
    q.tagfilter = get_tag_setting_flag()
    x = api.filter(q)
    set_category(x.name)

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


def list_all_series_by_group_id(gid: int) -> List[Tuple[int, ListItem]]:
    list_of_listitems = []
    q = api2.QueryOptions()
    q.id = gid
    q.level = 1
    q.tagfilter = get_tag_setting_flag()
    x = api.group(q)

    for s in x.series:
        list_of_listitems.append((s.id, get_listitem_from_serie(s)))

    return list_of_listitems


def list_episodes_for_series_by_series_id(s_id: int) -> Tuple[List[Tuple[int, ThisType, ListItem]], api2models.Serie]:
    list_of_li = []
    q = api2.QueryOptions()
    q.allpics = 1
    q.id = s_id
    q.level = 1
    if plugin_addon.getSettingBool('file_resume'):
        q.level = 2  # we need eps-offset if we want resume
    q.tagfilter = get_tag_setting_flag()
    x = api.series_get_by_id(q)

    series_title, non_color_title = get_proper_title(x)

    for ep in x.eps:
        list_of_li.append((ep.id, map_episodetype_to_thistype(ep.eptype), get_listitem_from_episode(ep, series_title, x.roles, x.id)))

    return list_of_li, x


def list_all_recent_series_and_episodes() -> List[Tuple[int, ThisType, ListItem]]:
    list_of_li = []
    q = api2models.QueryOptions()
    q.allpics = 1
    q.level = 1
    s = api.series_get_recent(q)
    for ss in s:
        list_of_li.append((ss.id, ThisType.series, get_listitem_from_serie(ss)))
    e = api.episodes_get_recent(q)
    for ee in e:
        list_of_li.append((ee.id, ThisType.episodes, get_listitem_from_episode(ee, '', None, s.id)))
    f = api.file_recent()
    for ff in f:
        list_of_li.append((ff.id, ThisType.raw, get_listitem_from_rawfile(ff)))
    return list_of_li


def get_file_id_from_ep_id(ep_id: int) -> List[api2models.RawFile]:
    q = api2.QueryOptions()
    q.id = ep_id
    q.level = 1
    q.tagfilter = get_tag_setting_flag()
    x = api.episode_get(q)
    return x.files


def list_all_unsorted() -> List[Tuple[int, ListItem]]:
    list_of_listitems = []
    unsort_limit = plugin_addon.getSettingInt('unsort_limit')
    x = api.file_unsort(level=1, limit=unsort_limit)

    for r in x:
        list_of_listitems.append((r.id, get_listitem_from_rawfile(r)))

    return list_of_listitems


def set_sorting_method(x: ThisType):
    if x == ThisType.episodes:
        xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_UNSORTED)
        xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_EPISODE)
        xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_TITLE)
        xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
        xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_VIDEO_RATING)
        xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_LABEL)
        xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_DATE)
    elif x == ThisType.series or x == ThisType.filter or x == ThisType.group:
        xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_UNSORTED)
        xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE_IGNORE_THE)
        xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_DATE)
        xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
        xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_VIDEO_RATING)
    else:
        xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_NONE)


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


def remove_markdown(data=''):
    p = re.compile(r'\[.*?\]')
    return p.sub('', data)


def did_you_rate_every_episode(series_id: int) -> Tuple[bool, str]:
    q = api2models.QueryOptions()
    q.id = series_id
    q.notag = 1
    q.nocast = 1
    q.level = 1
    q.allpics = 0

    all_rated: bool = True
    suggest_rating_based_on_episode_rating = []
    suggest_rating = 0

    s = api.series_get_by_id(q)
    for ep in s.eps:
        if ep.userrating is None or (int(ep.userrating) == 0 and map_episodetype_to_thistype(ep.eptype) == ThisType.episodes):
            all_rated = False
            suggest_rating_based_on_episode_rating.append(int(ep.userrating))
    for uservote in suggest_rating_based_on_episode_rating:
        suggest_rating += uservote
    suggest_rating = float(suggest_rating/len(suggest_rating_based_on_episode_rating))
    return all_rated, '%s' % suggest_rating


def vote_for_series(series_id: int):
    suggest_rating = ''
    if plugin_addon.getSettingBool('suggest_series_vote'):
        all_eps_rated, suggested_rating = did_you_rate_every_episode(series_id)
        if plugin_addon.getSettingBool('suggest_series_vote_all_eps'):
            if not all_eps_rated:
                xbmcgui.Dialog().ok(plugin_addon.getLocalizedString(30321), plugin_addon.getLocalizedString(30353))
                return
        suggest_rating = ' [ %s ]' % suggested_rating

    vote_list = ['Don\'t Vote' + suggest_rating, '10', '9', '8', '7', '6', '5', '4', '3', '2', '1']
    my_vote = xbmcgui.Dialog().select(plugin_addon.getLocalizedString(30321), vote_list)
    if my_vote < 1:
        return
    my_vote = int(vote_list[my_vote])
    if my_vote < 1:
        return
    xbmc.executebuiltin('Notification(%s, %s %s, 7500, %s)' % (plugin_addon.getLocalizedString(30321),
                                                               plugin_addon.getLocalizedString(30322),
                                                               str(my_vote), plugin_addon.getAddonInfo('icon')))
    api.serie_vote(id=series_id, score=my_vote)


def vote_for_episode(ep_id: int):
    vote_list = ['Don\'t Vote', '10', '9', '8', '7', '6', '5', '4', '3', '2', '1']
    my_vote = xbmcgui.Dialog().select(plugin_addon.getLocalizedString(30323), vote_list)
    if my_vote < 1:
        return
    my_vote = int(vote_list[my_vote])
    if my_vote < 1:
        return
    xbmc.executebuiltin('Notification(%s, %s %s, 7500, %s)' % (plugin_addon.getLocalizedString(30323),
                                                               plugin_addon.getLocalizedString(30322),
                                                               str(my_vote), plugin_addon.getAddonInfo('icon')))
    api.episode_vote(id=ep_id, score=my_vote)
    if plugin_addon.getSettingBool('enableCache'):
        url = cache.get_last()
        xbmc.log(f'=== clear cache for watch mark: {url}', xbmc.LOGINFO)
        cache.remove_cache(url)


def get_file_name(filename):
    name = filename
    name_split = filename.split('\\')
    if len(name_split) > 1:
        name = name_split[len(name_split) - 1]
    return name


def add_continue_item(series: api2models.Serie, episode_type: ThisType) -> ListItem:
    if not plugin_addon.getSettingBool('show_continue'):
        return None
    #continue_url = script(script_utils.url_move_to_item(watched_index))
    continue_url = '/'

    continue_text = plugin_addon.getLocalizedString(30238)
    if plugin_addon.getSettingBool('replace_continue'):
        if episode_type == ThisType.specials:
            eps = series.watched_sizes.Specials if series.watched_sizes.Specials is not None else 0
            total = series.total_sizes.Specials if series.total_sizes.Specials is not None else 0
            if plugin_addon.getSettingBool('local_total'):
                total = series.local_sizes.Specials if series.local_sizes.Specials is not None else 0
        else:
            eps = series.watched_sizes.Episodes if series.watched_sizes.Episodes is not None else 0
            total = series.total_sizes.Episodes if series.total_sizes.Episodes is not None else 0
            if plugin_addon.getSettingBool('local_total'):
                total = series.local_sizes.Episodes if series.local_sizes.Episodes is not None else 0

        continue_text = '[ %s: %s/%s ]' % (map_thitype_to_eptype(episode_type), eps, total)

    continue_item = ListItem(label=continue_text, path=continue_url, offscreen=True)
    return continue_item


def get_series_id_from_ep_id(ep_id: int) -> api2models.Serie:
    q = api2models.QueryOptions()
    q.id = ep_id
    x = api.series_from_ep(q)
    return x
