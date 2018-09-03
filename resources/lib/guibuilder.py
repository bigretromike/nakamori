# -*- coding: utf-8 -*-
"""
here are functions needed to create dirs/files
"""

from resources.lib import ModelUtils
from resources.lib import KodiUtils

import resources.lib.search as search

import xbmcaddon
import xbmcgui
import xbmc
import xbmcplugin
import sys
import os
import datetime
import time
from collections import defaultdict
# noinspection PyUnresolvedReferences
import nakamoritools as nt

list_items = []
handle = int(sys.argv[1])
busy = xbmcgui.DialogProgress()

_img = os.path.join(xbmcaddon.Addon(nt.addon.getSetting('icon_pack')).getAddonInfo('path'), 'resources', 'media')


def add_gui_item(gui_url, details, extra_data, context=None, folder=True, index=0, force_select=False):
    """Adds an item to the menu and populates its info labels
    :param gui_url:The URL of the menu or file this item links to
    :param details:Data such as info labels
    :param extra_data:Data such as stream info
    :param context:The context menu
    :param folder:Is it a folder or file
    :param index:Index in the list
    :param force_select: select after adding
    :type gui_url:str
    :type details:Union[str,object]
    :type extra_data:Union[str,object]
    :type context:
    :type folder:bool
    :type index:int
    :rtype:bool
    :return: Did the item successfully add
    """
    try:
        tbi = ""
        tp = 'video'
        link_url = ""

        # do this before so it'll log
        # use the year as a fallback in case the date is unavailable
        if details.get('date', '') == '':
            if details.get('aired', '') != '':
                f_data = str(details['aired']).split('-')  # aired y-m-d
                if len(f_data) == 3:
                    if len(f_data[2]) == 1:
                        f_data[2] = '0' + f_data[2]
                    if len(f_data[1]) == 1:
                        f_data[1] = '0' + f_data[1]
                    details['date'] = f_data[2] + '.' + f_data[1] + '.' + f_data[0]  # date d.m.y
                    details['aired'] = f_data[0] + '-' + f_data[1] + '-' + f_data[2]  # aired y-m-d
            elif details.get('year', '') != '' and details.get('year', '0') != 0:
                details['date'] = '01.01.' + str(details['year'])  # date d.m.y
                f_data = str(details['date']).split('.')
                details['aired'] = f_data[2] + '-' + f_data[1] + '-' + f_data[0]  # aired y-m-d

        if nt.addon.getSetting("spamLog") == 'true':
            xbmc.log("add_gui_item - url: " + gui_url, xbmc.LOGWARNING)
            nt.dump_dictionary(details, 'details')
            nt.dump_dictionary(extra_data, 'extra data')

        if extra_data is not None and len(extra_data) > 0:
            if extra_data.get('parameters'):
                for argument, value in extra_data.get('parameters').items():
                    link_url = "%s&%s=%s" % (link_url, argument, nt.quote(value))
            tbi = extra_data.get('thumb', '')
            tp = extra_data.get('type', 'Video')

        liz = xbmcgui.ListItem(details.get('title', 'Unknown'))
        if tbi is not None and len(tbi) > 0:
            liz.setArt({'thumb': tbi, 'icon': tbi, 'poster': tbi})

        if details.get('rating', 0) != '':
            liz.setRating('anidb', float(int(details.get('rating', 0))), int(details.get('votes', 0)), True)

        if extra_data is not None and len(extra_data) > 0:
            liz.setUniqueIDs({'anidb': extra_data.get('serie_id', 0)})
            actors = extra_data.get('actors', None)
            if actors is not None:
                if len(actors) > 0:
                    try:
                        liz.setCast(actors)
                        details.pop('cast', None)
                        details.pop('castandrole', None)
                    except:
                        pass
        # Set the properties of the item, such as summary, name, season, etc
        liz.setInfo(type=tp, infoLabels=details)

        # TODO Refactor this out into the above method
        # For all video items
        if not folder:
            # remove most of default context menu items but break viewing
            # folder = True
            # liz.setProperty('IsPlayable', 'true')
            liz.setProperty('sorttitle', details.get('sorttitle', details.get('title', 'Unknown')))
            if extra_data and len(extra_data) > 0:
                if extra_data.get('type', 'video').lower() == "video":
                    liz.setProperty('TotalTime', str(extra_data['VideoStreams'][0].get('duration', 0)))
                    if nt.addon.getSetting("file_resume") == "true":
                        liz.setProperty('ResumeTime', str(extra_data.get('resume')))

                    video_codec = extra_data.get('VideoStreams', {})
                    if len(video_codec) > 0:
                        video_codec = video_codec[0]
                        liz.addStreamInfo('video', video_codec)
                        liz.setProperty('VideoResolution', str(video_codec.get('xVideoResolution', '')))
                        liz.setProperty('VideoCodec', video_codec.get('xVideoCodec', ''))
                        liz.setProperty('VideoAspect', str(video_codec.get('aspect', '')))

                    if len(extra_data.get('AudioStreams', {})) > 0:
                        audio = extra_data.get('AudioStreams')
                        liz.setProperty('AudioCodec', audio.get('xAudioCodec', ''))
                        liz.setProperty('AudioChannels', str(audio.get('xAudioChannels', '')))
                        for stream in extra_data['AudioStreams']:
                            if not isinstance(extra_data['AudioStreams'][stream], dict):
                                continue
                            liz.setProperty('AudioCodec.' + str(stream), str(extra_data['AudioStreams'][stream]
                                                                             ['AudioCodec']))
                            liz.setProperty('AudioChannels.' + str(stream), str(extra_data['AudioStreams'][stream]
                                                                                ['AudioChannels']))
                            audio_codec = dict()
                            audio_codec['codec'] = str(extra_data['AudioStreams'][stream]['AudioCodec'])
                            audio_codec['channels'] = int(extra_data['AudioStreams'][stream]['AudioChannels'])
                            audio_codec['language'] = str(extra_data['AudioStreams'][stream]['AudioLanguage'])
                            liz.addStreamInfo('audio', audio_codec)

                    if len(extra_data.get('SubStreams', {})) > 0:
                        for stream2 in extra_data['SubStreams']:
                            liz.setProperty('SubtitleLanguage.' + str(stream2), str(extra_data['SubStreams'][stream2]
                                                                                    ['SubtitleLanguage']))
                            subtitle_codec = dict()
                            subtitle_codec['language'] = str(extra_data['SubStreams'][stream2]['SubtitleLanguage'])
                            liz.addStreamInfo('subtitle', subtitle_codec)

            # UMS/PSM Jumpy plugin require 'path' to play video
            key_file = str(extra_data.get('key', 'empty'))
            liz.setProperty('path', key_file)
            liz.setPath(key_file)

        # For series/groups
        if extra_data and len(extra_data) > 0:
            if extra_data.get('source') == 'serie' or extra_data.get('source') == 'group':
                # Then set the number of watched and unwatched, which will be displayed per season
                liz.setProperty('TotalEpisodes', str(extra_data['TotalEpisodes']))
                liz.setProperty('WatchedEpisodes', str(extra_data['WatchedEpisodes']))
                liz.setProperty('UnWatchedEpisodes', str(extra_data['UnWatchedEpisodes']))

                if extra_data.get('partialTV') == 1:
                    total = str(extra_data['TotalEpisodes'])
                    watched = str(extra_data['WatchedEpisodes'])
                    if nt.python_two:
                        # noinspection PyCompatibility
                        if unicode(total).isnumeric() and unicode(watched).isnumeric():
                            liz.setProperty('TotalTime', total)
                            liz.setProperty('ResumeTime', watched)
                        else:
                            liz.setProperty('TotalTime', '100')
                            liz.setProperty('ResumeTime', '50')
                    else:
                        # noinspection PyUnresolvedReferences
                        if total.isnumeric() and watched.isnumeric():
                            liz.setProperty('TotalTime', total)
                            liz.setProperty('ResumeTime', watched)
                        else:
                            liz.setProperty('TotalTime', '100')
                            liz.setProperty('ResumeTime', '50')

            if extra_data.get('thumb'):
                liz.setArt({"thumb": extra_data.get('thumb', '')})
                liz.setArt({"icon": extra_data.get('thumb', '')})
                liz.setArt({"poster": extra_data.get('thumb', '')})
            if extra_data.get('fanart_image'):
                liz.setArt({"fanart": extra_data.get('fanart_image', '')})
                liz.setArt({"clearart": extra_data.get('fanart_image', '')})
            if extra_data.get('banner'):
                liz.setArt({'banner': extra_data.get('banner', '')})
            if extra_data.get('season_thumb'):
                liz.setArt({'seasonThumb': extra_data.get('season_thumb', '')})

        if context is None:
            if extra_data and len(extra_data) > 0:
                context = []
                url_peep_base = sys.argv[0]

                # menu for episode
                if extra_data.get('source', 'none') == 'ep':
                    series_id = extra_data.get('serie_id', 0)
                    ep_id = extra_data.get('ep_id', 0)
                    file_id = extra_data.get('file_id', 0)
                    url_peep = url_peep_base
                    url_peep = nt.set_parameter(url_peep, 'mode', 1)
                    url_peep = nt.set_parameter(url_peep, 'serie_id', str(series_id))
                    url_peep = nt.set_parameter(url_peep, 'ep_id', str(ep_id))
                    url_peep = nt.set_parameter(url_peep, 'ui_index', str(index))
                    url_peep = nt.set_parameter(url_peep, 'file_id', str(file_id))

                    # Play
                    context.append((nt.addon.getLocalizedString(30065), 'Action(Select)'))

                    # Resume
                    if 'resume' in extra_data:
                        if nt.addon.getSetting("file_resume") == "true":
                            if str(extra_data.get('resume')) != "0":
                                liz.setProperty('ResumeTime', str(extra_data.get('resume')))
                                context.append((nt.addon.getLocalizedString(30141) + ' (%s)' %
                                                time.strftime('%H:%M:%S', time.gmtime(int(extra_data.get('resume')))),
                                                'RunPlugin(%s&cmd=resume)' % url_peep))

                    # Play (No Scrobble)
                    if nt.addon.getSetting('context_show_play_no_watch') == 'true':
                        context.append((nt.addon.getLocalizedString(30132),
                                        'RunPlugin(%s&cmd=no_mark)' % url_peep))

                    # Inspect
                    if nt.addon.getSetting('context_pick_file') == 'true':
                        context.append((nt.addon.getLocalizedString(30133),
                                        'RunPlugin(%s&cmd=pickFile)' % url_peep))

                    # Mark as watched/unwatched
                    if extra_data.get('jmmepisodeid') != '':
                        if nt.addon.getSetting('context_krypton_watched') == 'true':
                            if details.get('playcount', 0) == 0:
                                context.append((nt.addon.getLocalizedString(30128),
                                                'RunPlugin(%s&cmd=watched)' % url_peep))
                            else:
                                context.append((nt.addon.getLocalizedString(30129),
                                                'RunPlugin(%s&cmd=unwatched)' % url_peep))
                        else:
                            context.append((nt.addon.getLocalizedString(30128),
                                            'RunPlugin(%s&cmd=watched)' % url_peep))
                            context.append((nt.addon.getLocalizedString(30129),
                                            'RunPlugin(%s&cmd=unwatched)' % url_peep))

                    # Playlist Mode
                    if nt.addon.getSetting('context_playlist') == 'true':
                        context.append((nt.addon.getLocalizedString(30130),
                                        'RunPlugin(%s&cmd=createPlaylist)' % url_peep))

                    # Vote Episode
                    if nt.addon.getSetting('context_show_vote_Episode') == 'true' and ep_id != '':
                        context.append((nt.addon.getLocalizedString(30125),
                                        'RunPlugin(%s&cmd=voteEp)' % url_peep))

                    # Vote Series
                    if nt.addon.getSetting('context_show_vote_Series') == 'true' and series_id != '':
                        context.append((nt.addon.getLocalizedString(30124),
                                        'RunPlugin(%s&cmd=voteSer)' % url_peep))

                    # Metadata
                    if nt.addon.getSetting('context_show_info') == 'true':
                        context.append((nt.addon.getLocalizedString(30123),
                                        'Action(Info)'))

                    if nt.addon.getSetting('context_view_cast') == 'true':
                        if series_id != '':
                            context.append((nt.addon.getLocalizedString(30134),
                                            'ActivateWindow(Videos, %s&cmd=viewCast)' % url_peep))

                    if nt.addon.getSetting('context_refresh') == 'true':
                        context.append((nt.addon.getLocalizedString(30131),
                                        'RunPlugin(%s&cmd=refresh)' % url_peep))

                    context.append(('  ', 'empty'))
                    context.append((nt.addon.getLocalizedString(30147), 'empty'))
                    context.append((nt.addon.getLocalizedString(30148), 'empty'))

        liz.addContextMenuItems(context)
        liz.select(force_select)
        list_items.append((gui_url, liz, folder))
        return liz
    except Exception as e:
        nt.error("util.error during add_gui_item", str(e))


def end_of_directory(cache=True, force_sort=-1, place='filter'):
    """
    Leave this in nakamori.py! It needs to be here to access listitems properly
    Adds all items to the list in batch, and then finalizes it
    """
    xbmcplugin.addDirectoryItems(handle, list_items, len(list_items))

    if force_sort == -1:
        nt.set_user_sort_method(place)
    else:
        nt.set_sort_method(str(force_sort))

    xbmcplugin.endOfDirectory(handle, cacheToDisc=cache)


def add_raw_files(node):
    """
    adding raw_file item to listitem of kodi
    :param node: node containing raw_file
    :return: add item to listitem
    """
    try:
        name = nt.decode(node.get("filename", ''))
        file_id = node["id"]
        key = node["url"]
        raw_url = nt.server + "/api/file?id=" + str(file_id)
        title = nt.os.path.split(str(name))[1]
        thumb = os.path.join(_img, 'thumb', 'other.png')
        fanart = os.path.join(_img, 'fanart', 'other.png')
        banner = os.path.join(_img, 'banner', 'other.png')
        poster = os.path.join(_img, 'poster', 'other.png')
        liz = xbmcgui.ListItem(label=title, label2=title, path=raw_url)
        liz.setArt({'thumb': thumb, 'poster': poster, 'icon': 'DefaultVideo.png', 'fanart': fanart, 'banner': banner})
        liz.setInfo(type="Video", infoLabels={"Title": title, "Plot": title})
        u = sys.argv[0]
        u = nt.set_parameter(u, 'url', raw_url)
        u = nt.set_parameter(u, 'mode', 1)
        u = nt.set_parameter(u, 'name', nt.quote_plus(title))
        u = nt.set_parameter(u, 'raw_id', file_id)
        u = nt.set_parameter(u, 'type', "raw")
        u = nt.set_parameter(u, 'file', key)
        u = nt.set_parameter(u, 'ep_id', '0')
        u = nt.set_parameter(u, 'vl', node["import_folder_id"])
        context = [(nt.addon.getLocalizedString(30120), 'RunPlugin(%s&cmd=rescan)' % u),
                   (nt.addon.getLocalizedString(30121), 'RunPlugin(%s&cmd=rehash)' % u),
                   (nt.addon.getLocalizedString(30122), 'RunPlugin(%s&cmd=missing)' % u)]
        liz.addContextMenuItems(context)
        list_items.append((u, liz, False))
    except:  # Sometimes a file is deleted or invalid, but we should just skip it
        pass


def add_content_typ_dir(name, serie_id):
    """
    Adding directories for given types of content inside series (ex. episodes, credits)
    :param name: name of directory
    :param serie_id: id that the content belong too
    :return: add new directory
    """
    dir_url = nt.server + "/api/serie"
    dir_url = nt.set_parameter(dir_url, 'id', str(serie_id))
    dir_url = nt.set_parameter(dir_url, 'level', 4)
    title = str(name)

    if title == "Credit":
        image_name = 'credits.png'
    elif title == "Movie":
        image_name = "movie.png"
    elif title == "Ova":
        image_name = "ova.png"
    elif title == "Other":
        image_name = "other.png"
    elif title == "Episode":
        image_name = "episodes.png"
    elif title == "TV Episode":
        image_name = "tvepisodes.png"
    elif title == "Web Clip":
        image_name = "webclips.png"
    elif title == "Parody":
        image_name = "parody.png"
    elif title == "Special":
        image_name = "specials.png"
    elif title == "Trailer":
        image_name = "trailers.png"
    elif title == "Misc":
        image_name = "misc.png"
    else:
        image_name = "other.png"

    thumb = os.path.join(_img, 'thumb', image_name)
    fanart = os.path.join(_img, 'fanart', image_name)
    banner = os.path.join(_img, 'banner', image_name)
    poster = os.path.join(_img, 'poster', image_name)

    liz = xbmcgui.ListItem(label=title, label2=title, path=dir_url)
    liz.setArt({'thumb': thumb, 'poster': poster, 'icon': 'DefaultVideo.png', 'fanart': fanart, 'banner': banner})
    liz.setInfo(type="Video", infoLabels={"Title": title, "Plot": title})
    u = sys.argv[0]
    u = nt.set_parameter(u, 'url', dir_url)
    u = nt.set_parameter(u, 'mode', str(6))
    u = nt.set_parameter(u, 'name', nt.quote_plus(title))
    u = nt.set_parameter(u, 'type', name)
    list_items.append((u, liz, True))


def add_serie_item(node, parent_title, destination_playlist=False):
    """
    Processing serie/content_directory 'node' into episode list
    :param node:
    :param parent_title:
    :param destination_playlist:
    :return:
    """
    # xbmcgui.Dialog().ok('series', 'series')
    temp_genre = ''
    if 'tags' in node:
        temp_genre = ModelUtils.get_tags(node.get("tags", {}))

    watched_sizes = node.get("watched_sizes", {})
    if len(watched_sizes) > 0:
        watched = nt.safe_int(watched_sizes.get("Episodes", 0))
        if not nt.get_kodi_setting_bool("ignore_specials_watched"):
            watched += nt.safe_int(watched_sizes.get("Specials", 0))
    else:
        watched = nt.safe_int(node.get("watchedsize", ''))
    _watched = watched
    list_cast = []
    list_cast_and_role = []
    actors = []
    if len(list_cast) == 0 and 'roles' in node:
        cast_nodes = node.get("roles", {})
        if len(cast_nodes) > 0:
            if cast_nodes[0].get("character", "") != "":
                result_list = ModelUtils.get_cast_and_role_new(cast_nodes)
            else:
                result_list = ModelUtils.get_cast_and_role(cast_nodes)
            actors = result_list
            if result_list is not None:
                result_list = ModelUtils.convert_cast_and_role_to_legacy(result_list)
                list_cast = result_list[0]
                list_cast_and_role = result_list[1]

    if nt.addon.getSetting("local_total") == "true":
        local_sizes = node.get("local_sizes", {})
        if len(local_sizes) > 0:
            total = nt.safe_int(local_sizes.get("Episodes", 0)) + nt.safe_int(local_sizes.get("Specials", 0))
        else:
            total = nt.safe_int(node.get("localsize", ''))
    else:
        sizes = node.get("total_sizes", {})
        if len(sizes) > 0:
            total = nt.safe_int(sizes.get("Episodes", 0)) + nt.safe_int(sizes.get("Specials", 0))
        else:
            total = nt.safe_int(node.get("localsize", ''))

    if watched > total:
        watched = total

    title = ModelUtils.get_title(node)
    if "userrating" in node:
        userrating = str(node.get("userrating", '0')).replace(',', '.')
    else:
        userrating = 0.0

    # filter out invalid date
    air = node.get('air', '')
    if air != '':
        # air=0001-01-01
        if air == '0001-01-01' or air == '01-01-0001':
            air = ''

    details = {
        'mediatype':        'episode',
        'title':            title,
        'parenttitle':      nt.decode(parent_title),
        'genre':            temp_genre,
        'year':             node.get("year", ''),
        'episode':          total,
        'season':           nt.safe_int(node.get("season", '1')),
        # 'count'        : count,
        'size':             total,
        'rating':           float(str(node.get("rating", '0')).replace(',', '.')),
        'userrating':       float(userrating),
        'playcount':        watched,
        'cast':             list_cast,  # cast : list (Michal C. Hall,
        'castandrole':      list_cast_and_role,
        # director       : string (Dagur Kari,
        # 'mpaa':             directory.get('contentRating', ''),
        'plot':             nt.remove_anidb_links(nt.decode(node.get("summary", '...'))),
        # 'plotoutline'  : plotoutline,
        'originaltitle':    title,
        'sorttitle':        title,
        # 'Duration'     : duration,
        # 'Studio'       : studio, < ---
        # 'Tagline'      : tagline,
        # 'Writer'       : writer,
        # 'tvshowtitle'  : tvshowtitle,
        'tvshowname':       title,
        # 'premiered'    : premiered,
        # 'Status'       : status,
        # code           : string (tt0110293, - IMDb code
        'aired':            str(air),
        # credits        : string (Andy Kaufman, - writing credits
        # 'Lastplayed'   : lastplayed,
        'votes':            node.get('votes', 0),
        # trailer        : string (/home/user/trailer.avi,
        'dateadded':        node.get('added', '')
    }

    if nt.addon.getSetting('hide_rating') == 'Always':
        if nt.addon.getSetting('hide_rating_type') != 'Episodes':  # Series|Both
            details['rating'] = ''
    elif nt.addon.getSetting('hide_rating') == 'Unwatched':
        if nt.addon.getSetting('hide_rating_type') != 'Episodes' and watched < total:  # Series|Both
            details['rating'] = ''

    directory_type = str(node.get('type', ''))
    key_id = str(node.get('id', ''))
    key = nt.server + "/api/serie"
    key = nt.set_parameter(key, 'id', key_id)
    key = nt.set_parameter(key, 'level', 2)
    key = nt.set_parameter(key, 'tagfilter', ModelUtils.__tagSettingFlags__)
    if nt.addon.getSetting('request_nocast') == 'true':
        key = nt.set_parameter(key, 'nocast', 1)

    thumb = ''
    if len(node["art"]["thumb"]) > 0:
        thumb = node["art"]["thumb"][0]["url"]
        if thumb is not None and ":" not in thumb:
            thumb = nt.server + thumb
    fanart = ''
    if len(node["art"]["fanart"]) > 0:
        fanart = node["art"]["fanart"][0]["url"]
        if fanart is not None and ":" not in fanart:
            fanart = nt.server + fanart
    banner = ''
    if len(node["art"]["banner"]) > 0:
        banner = node["art"]["banner"][0]["url"]
        if banner is not None and ":" not in banner:
            banner = nt.server + banner

    extra_data = {
        'type':                 'video',
        'source':               directory_type,
        'UnWatchedEpisodes':    int(total) - watched,
        'WatchedEpisodes':      watched,
        'TotalEpisodes':        total,
        'thumb':                thumb,
        'fanart_image':         fanart,
        'banner':               banner,
        'key':                  key,
        'actors':               actors,
        'serie_id':             key_id
    }

    serie_url = key
    ModelUtils.set_watch_flag(extra_data, details)
    use_mode = 5
    if key_id == '-1' or key_id == '0':
        use_mode = 0

    u = sys.argv[0]
    u = nt.set_parameter(u, 'url', serie_url)
    u = nt.set_parameter(u, 'mode', use_mode)
    u = nt.set_parameter(u, 'movie', node.get('ismovie', '0'))

    context = []
    url_peep = sys.argv[0]
    url_peep = nt.set_parameter(url_peep, 'mode', 1)
    url_peep = nt.set_parameter(url_peep, 'serie_id', key_id)

    # Watch
    context.append((nt.addon.getLocalizedString(30126), 'RunPlugin(%s&cmd=watched)' % url_peep))
    context.append((nt.addon.getLocalizedString(30127), 'RunPlugin(%s&cmd=unwatched)' % url_peep))

    # Vote
    if nt.addon.getSetting('context_show_vote_Series') == 'true':
        context.append((nt.addon.getLocalizedString(30124), 'RunPlugin(%s&cmd=voteSer)' % url_peep))

    # Metadata
    if nt.addon.getSetting('context_show_info') == 'true':
        context.append((nt.addon.getLocalizedString(30123), 'Action(Info)'))

    if nt.addon.getSetting('context_view_cast') == 'true':
        context.append((nt.addon.getLocalizedString(30134), 'ActivateWindow(Videos, %s&cmd=viewCast)' % url_peep))

    if nt.addon.getSetting('context_refresh') == 'true':
        context.append((nt.addon.getLocalizedString(30131), 'RunPlugin(%s&cmd=refresh)' % url_peep))

    if destination_playlist:
        return details
    else:
        add_gui_item(u, details, extra_data, context)


def add_group_item(node, parent_title, filter_id, is_filter=False):
    """
    Processing group 'node' into series (serie grouping)
    :param node:
    :param parent_title:
    :param filter_id:
    :param is_filter:
    :return:
    """

    temp_genre = ModelUtils.get_tags(node.get("tags", {}))
    title = ModelUtils.get_title(node)

    watched_sizes = node.get("watched_sizes", {})
    if len(watched_sizes) > 0:
        watched = nt.safe_int(watched_sizes.get("Episodes", 0))
        if not nt.get_kodi_setting_bool("ignore_specials_watched"):
            watched += nt.safe_int(watched_sizes.get("Specials", 0))
    else:
        watched = nt.safe_int(node.get("watchedsize", ''))

    if nt.addon.getSetting("local_total") == "true":
        local_sizes = node.get("local_sizes", {})
        if len(local_sizes) > 0:
            total = nt.safe_int(local_sizes.get("Episodes", 0)) + nt.safe_int(local_sizes.get("Specials", 0))
        else:
            total = nt.safe_int(node.get("localsize", ''))
    else:
        sizes = node.get("total_sizes", {})
        if len(sizes) > 0:
            total = nt.safe_int(sizes.get("Episodes", 0)) + nt.safe_int(sizes.get("Specials", 0))
        else:
            total = nt.safe_int(node.get("localsize", ''))

    if node.get("type", '') == 'filter':
        total = node.get("size", 0)

    if watched > total:
        watched = total

    content_type = node.get("type", '') if not is_filter else "filter"

    # filter out invalid date
    air = node.get('air', '')
    if air != '':
        # air=0001-01-01
        if air == '0001-01-01' or air == '01-01-0001':
            air = ''

    details = {
        'mediatype':        'tvshow',
        'title':            title,
        'parenttitle':      nt.decode(parent_title),
        'genre':            temp_genre,
        'year':             node.get('year', ''),
        'episode':          total,
        'season':           nt.safe_int(node.get('season', '1')),
        'size':             total,
        'rating':           float(str(node.get('rating', '0')).replace(',', '.')),
        'userrating':       float(str(node.get('userrating', '0')).replace(',', '.')),
        'playcount':        watched,
        'plot':             nt.remove_anidb_links(nt.decode(node.get('summary', '...'))),
        'originaltitle':    title,
        'sorttitle':        title,
        'tvshowname':       title,
        'dateadded':        node.get('added', ''),
        'aired':            str(air),
    }

    if nt.addon.getSetting('hide_rating') == 'Always':
        if nt.addon.getSetting('hide_rating_type') != 'Episodes':  # Series|Both
            details['rating'] = ''
    elif nt.addon.getSetting('hide_rating') == 'Unwatched':
        if nt.addon.getSetting('hide_rating_type') != 'Episodes' and watched < total:  # Series|Both
            details['rating'] = ''

    key_id = str(node.get("id", ''))
    if is_filter:
        key = nt.server + "/api/filter"
    else:
        key = nt.server + "/api/group"
    key = nt.set_parameter(key, 'id', key_id)
    key = nt.set_parameter(key, 'filter', filter_id)
    key = nt.set_parameter(key, 'level', 1)
    key = nt.set_parameter(key, 'tagfilter', ModelUtils.__tagSettingFlags__)
    if nt.addon.getSetting('request_nocast') == 'true':
        key = nt.set_parameter(key, 'nocast', 1)

    thumb = ''
    if len(node["art"]["thumb"]) > 0:
        thumb = node["art"]["thumb"][0]["url"]
        if thumb is not None and ":" not in thumb:
            thumb = nt.server + thumb
    fanart = ''
    if len(node["art"]["fanart"]) > 0:
        fanart = node["art"]["fanart"][0]["url"]
        if fanart is not None and ":" not in fanart:
            fanart = nt.server + fanart
    banner = ''
    if len(node["art"]["banner"]) > 0:
        banner = node["art"]["banner"][0]["url"]
        if banner is not None and ":" not in banner:
            banner = nt.server + banner

    extra_data = {
        'type':                 'video',
        'source':               content_type,
        'thumb':                thumb,
        'fanart_image':         fanart,
        'banner':               banner,
        'key':                  key,
        'group_id':             key_id,
        'WatchedEpisodes':      watched,
        'TotalEpisodes':        total,
        'UnWatchedEpisodes':    total - watched
    }

    group_url = key
    ModelUtils.set_watch_flag(extra_data, details)
    use_mode = 4 if not is_filter else 4
    if key_id == '-1' or key_id == '0':
        use_mode = 0

    u = sys.argv[0]
    u = nt.set_parameter(u, 'url', group_url)
    u = nt.set_parameter(u, 'mode', str(use_mode))
    if filter_id != '':
        u = nt.set_parameter(u, 'filter', filter_id)
    else:
        u = nt.set_parameter(u, 'filter', None)

    url_peep = sys.argv[0]
    url_peep = nt.set_parameter(url_peep, 'mode', 1)
    url_peep = nt.set_parameter(url_peep, 'group_id', key_id)

    context = [(nt.addon.getLocalizedString(30126), 'RunPlugin(%s&cmd=watched)' % url_peep),
               (nt.addon.getLocalizedString(30127), 'RunPlugin(%s&cmd=unwatched)' % url_peep)]
    # Watch

    # Metadata
    if nt.addon.getSetting('context_show_info') == 'true' and not is_filter:
        context.append((nt.addon.getLocalizedString(30123), 'Action(Info)'))

    if nt.addon.getSetting('context_refresh') == 'true':
        context.append((nt.addon.getLocalizedString(30131), 'RunPlugin(%s&cmd=refresh)' % url_peep))

    add_gui_item(u, details, extra_data, context)


def add_filter_item(menu):
    """
    adds a filter item from json
    :param menu: json tree
    """
    use_mode = 4
    key = menu["url"]
    size = nt.safe_int(menu.get("size"))
    title = menu['name']

    if title == 'Continue Watching (SYSTEM)':
        title = 'Continue Watching'
    elif title == 'Unsort':
        title = 'Unsorted'
        use_mode = 8

    if nt.addon.getSetting("spamLog") == "true":
        xbmc.log("build_filters_menu - key = " + key, xbmc.LOGWARNING)

    if nt.addon.getSetting('request_nocast') == 'true' and title != 'Unsorted':
        key = nt.set_parameter(key, 'nocast', 1)
    key = nt.set_parameter(key, 'level', 2)
    if title == "Airing Today":
        key = nt.set_parameter(key, 'level', 0)
    key = nt.set_parameter(key, 'tagfilter', ModelUtils.__tagSettingFlags__)
    filter_url = key

    thumb = ''
    try:
        if len(menu["art"]["thumb"]) > 0:
            thumb = menu["art"]["thumb"][0]["url"]
            if ":" not in thumb:
                thumb = nt.server + thumb
    except:
        pass

    fanart = ''
    try:
        if len(menu["art"]["fanart"]) > 0:
            fanart = menu["art"]["fanart"][0]["url"]
            if ":" not in fanart:
                fanart = nt.server + fanart
    except:
        pass
    banner = ''
    try:
        if len(menu["art"]["banner"]) > 0:
            banner = menu["art"]["banner"][0]["url"]
            if ":" not in banner:
                banner = nt.server + banner
    except:
        pass

    u = sys.argv[0]
    u = nt.set_parameter(u, 'url', filter_url)
    u = nt.set_parameter(u, 'mode', use_mode)
    u = nt.set_parameter(u, 'name', nt.quote_plus(title))
    u = nt.set_parameter(u, 'filter_id', menu.get("id", ""))

    liz = xbmcgui.ListItem(label=title, label2=title, path=filter_url)
    liz.setArt({
        'icon': thumb,
        'thumb': thumb,
        'fanart': fanart,
        'poster': thumb,
        'banner': banner,
        'clearart': fanart
    })
    if thumb == '':
        liz.setIconImage('DefaultVideo.png')
    liz.setInfo(type="Video", infoLabels={"Title": title, "Plot": title, "count": size})
    list_items.append((u, liz, True))


def build_filters_menu():
    """
    Builds the list of items (filters) in the Main Menu
    """
    xbmcplugin.setContent(handle, 'tvshows')
    xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_EPISODE)
    xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_DATE)
    xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_TITLE_IGNORE_THE)

    try:
        filters_key = nt.server + "/api/filter"
        filters_key = nt.set_parameter(filters_key, "level", 0)
        retrieved_json = nt.get_json(filters_key)
        if retrieved_json is not None:
            json_menu = nt.json.loads(retrieved_json)
            KodiUtils.set_window_heading(json_menu['name'])
            try:
                menu_append = []
                for menu in json_menu["filters"]:
                    title = menu['name']
                    if title == 'Seasons':
                        airing = dict({
                            "name": nt.addon.getLocalizedString(30223),
                            "url": nt.server + "/api/serie/today",
                        })
                        airing['art'] = {}
                        airing['art']['fanart'] = []
                        airing['art']['thumb'] = []
                        airing['art']['fanart'].append({'url': os.path.join(_img, 'backgrounds', 'airing.jpg')})
                        airing['art']['thumb'].append({'url': os.path.join(_img, 'icons', 'airing.png')})
                        if nt.get_version(nt.addon.getSetting("ipaddress"),
                                          nt.addon.getSetting("port")) >= nt.LooseVersion("3.8.0.0"):
                            menu_append.append(airing)
                        menu['art'] = {}
                        menu['art']['fanart'] = []
                        menu['art']['thumb'] = []
                        menu['art']['fanart'].append({'url': os.path.join(_img, 'backgrounds', 'seasons.jpg')})
                        menu['art']['thumb'].append({'url': os.path.join(_img, 'icons', 'seasons.png')})
                        menu_append.append(menu)
                    elif title == 'Tags':
                        menu['art'] = {}
                        menu['art']['fanart'] = []
                        menu['art']['thumb'] = []
                        menu['art']['fanart'].append({'url': os.path.join(_img, 'backgrounds', 'tags.jpg')})
                        menu['art']['thumb'].append({'url': os.path.join(_img, 'icons', 'tags.png')})
                        menu_append.append(menu)
                    elif title == 'Unsort':
                        if nt.addon.getSetting("show_unsort") == "true":
                            menu['art'] = {}
                            menu['art']['fanart'] = []
                            menu['art']['thumb'] = []
                            menu['art']['fanart'].append({'url': os.path.join(_img, 'backgrounds', 'unsort.jpg')})
                            menu['art']['thumb'].append({'url': os.path.join(_img, 'icons', 'unsort.png')})
                            menu_append.append(menu)
                    elif title == 'Years':
                        menu['art'] = {}
                        menu['art']['fanart'] = []
                        menu['art']['thumb'] = []
                        menu['art']['fanart'].append({'url': os.path.join(_img, 'backgrounds', 'years.jpg')})
                        menu['art']['thumb'].append({'url': os.path.join(_img, 'icons', 'years.png')})
                        menu_append.append(menu)
                for menu in json_menu["filters"]:
                    title = menu['name']
                    if title == 'Unsort':
                        continue
                    elif title == 'Tags':
                        continue
                    elif title == 'Seasons':
                        continue
                    elif title == 'Years':
                        continue
                    add_filter_item(menu)

                for menu in menu_append:
                    add_filter_item(menu)

                # region Calendar
                if nt.addon.getSetting("show_calendar") == "true":
                    soon_url = nt.server + "/api/serie/soon"
                    title = nt.addon.getLocalizedString(30222)
                    liz = xbmcgui.ListItem(label=title, label2=title, path=soon_url)
                    liz.setArt({"icon": os.path.join(_img, 'icons', 'calendar.png'),
                                "fanart": os.path.join(_img, 'backgrounds', 'calendar.jpg')})
                    liz.setInfo(type="Video", infoLabels={"Title": title, "Plot": title})
                    u = sys.argv[0]
                    u = nt.set_parameter(u, 'url', soon_url)
                    u = nt.set_parameter(u, 'mode', str(9))
                    u = nt.set_parameter(u, 'name', nt.quote_plus(title))
                    list_items.append((u, liz, True))
                # endregion

                # region Search
                if nt.addon.getSetting("show_search") == "true":
                    search_url = nt.server + "/api/search"
                    title = nt.addon.getLocalizedString(30221)
                    liz = xbmcgui.ListItem(label=title, label2=title, path=search_url)
                    liz.setArt({"icon": os.path.join(_img, 'icons', 'search.png'),
                                "fanart": os.path.join(_img, 'backgrounds', 'search.jpg')})
                    liz.setInfo(type="Video", infoLabels={"Title": title, "Plot": title})
                    u = sys.argv[0]
                    u = nt.set_parameter(u, 'url', search_url)
                    u = nt.set_parameter(u, 'mode', str(3))
                    u = nt.set_parameter(u, 'name', nt.quote_plus(title))
                    list_items.append((u, liz, True))
                # endregion

                # region Settings
                if nt.addon.getSetting("show_settings") == "true":
                    title = nt.addon.getLocalizedString(30107)
                    liz = xbmcgui.ListItem(label=title, label2=title)
                    liz.setArt({"icon": os.path.join(_img, 'icons', 'settings.png'),
                                "fanart": os.path.join(_img, 'backgrounds', 'settings.jpg')})
                    liz.setInfo(type="Video", infoLabels={"Title": title, "Plot": title})
                    u = sys.argv[0]
                    u = nt.set_parameter(u, 'url', '')
                    u = nt.set_parameter(u, 'mode', str(11))
                    u = nt.set_parameter(u, 'name', nt.quote_plus(title))
                    list_items.append((u, liz, True))
                # endregion

                # region Shoko
                if nt.addon.getSetting("show_shoko") == "true":
                    title = nt.addon.getLocalizedString(30115)
                    liz = xbmcgui.ListItem(label=title, label2=title)
                    liz.setArt({"icon": os.path.join(_img, 'icons', 'settings.png'),
                                "fanart": os.path.join(_img, 'backgrounds', 'settings.jpg')})
                    liz.setInfo(type="Video", infoLabels={"Title": title, "Plot": title})
                    u = sys.argv[0]
                    u = nt.set_parameter(u, 'url', '')
                    u = nt.set_parameter(u, 'mode', str(12))
                    u = nt.set_parameter(u, 'name', nt.quote_plus(title))
                    list_items.append((u, liz, True))
                # endregion

                # region Experiment
                if nt.addon.getSetting("onepunchmen") == "true":
                    title = 'Experiment'
                    liz = xbmcgui.ListItem(label=title, label2=title)
                    liz.setArt({"icon": os.path.join(_img, 'icons', 'settings.png'),
                                "fanart": os.path.join(_img, 'backgrounds', 'settings.jpg')})
                    liz.setInfo(type="Video", infoLabels={"Title": title, "Plot": title})
                    u = sys.argv[0]
                    u = nt.set_parameter(u, 'url', '')
                    u = nt.set_parameter(u, 'mode', str(13))
                    u = nt.set_parameter(u, 'name', nt.quote_plus(title))
                    list_items.append((u, liz, True))
                # endregion

            except Exception as e:
                nt.error("util.error during build_filters_menu", str(e))

            end_of_directory(False, force_sort=0)

        else:
            xbmc.log('---> retrived_json = None, Network Error, wizard = 0', xbmc.LOGERROR)
            nt.addon.setSetting(id='wizard', value='0')
            build_network_menu()

    except Exception as e:
        nt.error("Invalid JSON Received in build_filters_menu", str(e))


def build_groups_menu(params, json_body=None):
    """
    Builds the list of items for Filters and Groups
    Args:
        params:
        json_body: parsing json_file directly, this will skip loading remote url from params
    Returns:

    """
    xbmcplugin.setContent(handle, 'tvshows')

    # https://codedocs.xyz/AlwinEsch/kodi/group__python__xbmcplugin.html
    xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_TITLE_IGNORE_THE)
    xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_DATE)
    xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_VIDEO_RATING)
    xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_VIDEO_YEAR)

    try:
        busy.create(nt.addon.getLocalizedString(30160), nt.addon.getLocalizedString(30161))
        parent_title = ''
        if 'name' in params:
            parent_title = params['name']
        elif 'query' in params:
            parent_title = params['query']
        xbmcplugin.setPluginCategory(handle, parent_title.replace('+', ' '))
        if json_body is None:
            busy.update(10)
            temp_url = params['url']
            temp_url = nt.set_parameter(temp_url, 'nocast', 1)
            temp_url = nt.set_parameter(temp_url, 'notag', 1)
            temp_url = nt.set_parameter(temp_url, 'level', 0)
            busy.update(20)
            html = nt.get_json(temp_url)
            busy.update(50, nt.addon.getLocalizedString(30162))
            if nt.addon.getSetting("spamLog") == "true":
                xbmc.log(params['url'], xbmc.LOGWARNING)
                xbmc.log(html, xbmc.LOGWARNING)
            html_body = nt.json.loads(html)
            busy.update(70)
            directory_type = html_body['type']
            if directory_type != "filters":
                # level 2 will fill group and series (for filter)
                temp_url = params['url']
                temp_url = nt.set_parameter(temp_url, 'level', 2)
                html = nt.get_json(temp_url)
                body = nt.json.loads(html)
            else:
                # level 1 will fill group and series (for filter)
                temp_url = params['url']
                temp_url = nt.set_parameter(temp_url, 'level', 1)
                html = nt.get_json(temp_url)
                body = nt.json.loads(html)
        else:
            body = json_body
        busy.update(100)
        busy.close()

        # check if this is maybe filter-inception
        try:
            KodiUtils.set_window_heading(body.get('name', ''))
        except:
            try:  # this might not be a filter
                # it isn't single filter)
                for nest_filter in body:
                    add_group_item(nest_filter, '', body.get('id', ''), True)
                end_of_directory(place='filter')
                return
            except:
                pass

        try:
            item_count = 0
            parent_title = body.get('name', '')
            directory_type = body.get('type', '')
            filter_id = ''

            if directory_type != 'ep' and directory_type != 'serie':
                if 'filter' in params:
                    filter_id = params['filter']
                    if directory_type == 'filter':
                        filter_id = body.get('id', '')

            if directory_type == 'filter':
                for grp in body["groups"]:
                    if len(grp["series"]) > 0:
                        if len(grp["series"]) == 1:
                            add_serie_item(grp["series"][0], parent_title)
                        else:
                            if json_body is not None:
                                for srg in grp["series"]:
                                    add_serie_item(srg, parent_title)
                            else:
                                add_group_item(grp, parent_title, filter_id)
                    item_count += 1
            elif directory_type == 'filters':
                for flt in body["filters"]:
                    add_group_item(flt, parent_title, filter_id, True)
                    item_count += 1
            elif directory_type == 'group':
                for sers in body['series']:
                    add_serie_item(sers, parent_title)
                    item_count += 1

        except Exception as e:
            nt.error("util.error during build_groups_menu", str(e))
    except Exception as e:
        nt.error("Invalid JSON Received in build_groups_menu", str(e))
    if params['name'] == 'Seasons':  # TODO make this language neutral
        end_of_directory(force_sort=0)
    else:
        end_of_directory(place='group')


def build_serie_episodes_types(params):
    """
    Builds list items for The Types Menu, or optionally subgroups
    Args:
        params:

    Returns:
    """

    try:
        html = nt.get_json(params['url'])
        if nt.addon.getSetting("spamLog") == "true":
            xbmc.log(html, xbmc.LOGWARNING)
        body = nt.json.loads(html)

        try:
            parent_title = ''
            try:
                parent_title = body.get('name', '')
            except Exception as exc:
                nt.error("Unable to get parent title in buildTVSeasons", str(exc))

            content_type = dict()
            if "eps" in body:
                if len(body.get("eps", {})) >= 1:
                    for ep in body["eps"]:
                        if ep["eptype"] not in content_type.keys():
                            content_type[ep["eptype"]] = ep["art"]["thumb"][0]["url"] if len(ep["art"]["thumb"]) > 0 \
                                else ''
            # no matter what type is its only one type, flat directory
            if len(content_type) == 1:
                build_serie_episodes(params)
                return
            else:
                xbmcplugin.setPluginCategory(handle, parent_title)
                xbmcplugin.setContent(handle, 'seasons')
                KodiUtils.set_window_heading('Types')

                xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_UNSORTED)
                xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
                xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_TITLE_IGNORE_THE)
                xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_DATE)
                xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_VIDEO_RATING)

                for content in content_type:
                    add_content_typ_dir(content, body.get("id", ''))
                end_of_directory(place='group')
                return

        except Exception as exs:
            nt.error("util.error during build_serie_episodes_types", str(exs))
    except Exception as exc:
        nt.error("Invalid JSON Received in build_serie_episodes_types", str(exc))
    end_of_directory(place='group')


def build_serie_episodes(params):
    """
    Load episode information from api, parse them one by one and add to listitem
    :param params:
    :return:
    """

    xbmcplugin.setContent(handle, 'episodes')  # episodes

    # value to hold position of not seen episode
    next_episode = -1
    episode_count = 0
    is_fake = 0

    busy.create(nt.addon.getLocalizedString(30160), nt.addon.getLocalizedString(30163))
    try:
        if 'fake' in params:
            is_fake = params['fake']
        item_count = 0
        html = nt.get_json(params['url'])
        busy.update(50, nt.addon.getLocalizedString(30162))
        body = nt.json.loads(html)
        if nt.addon.getSetting("spamLog") == "true":
            xbmc.log(html, xbmc.LOGWARNING)

        try:
            parent_title = ''
            try:
                parent_title = body.get('name', '')
                KodiUtils.set_window_heading(parent_title)
            except Exception as exc:
                nt.error("Unable to get parent title in buildTVEpisodes", str(exc))

            xbmcplugin.setPluginCategory(handle, parent_title)

            xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_UNSORTED)
            xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_EPISODE)
            xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_DATE)
            xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_TITLE_IGNORE_THE)
            xbmcplugin.addSortMethod(handle, 19)  # date added
            xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_VIDEO_RATING)
            xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
            xbmcplugin.addSortMethod(handle, 29)  # runtime
            xbmcplugin.addSortMethod(handle, 28)  # by MPAA

            # keep this init out of the loop, as we only provide this once
            list_cast = []
            list_cast_and_role = []
            actors = []

            if len(list_cast) == 0:
                cast_nodes = body.get('roles', {})
                if len(cast_nodes) > 0:
                    if cast_nodes[0].get("character", "") != "":
                        result_list = ModelUtils.get_cast_and_role_new(cast_nodes)
                    else:
                        result_list = ModelUtils.get_cast_and_role(cast_nodes)
                    actors = result_list
                    if result_list is not None:
                        result_list = ModelUtils.convert_cast_and_role_to_legacy(result_list)
                        list_cast = result_list[0]
                        list_cast_and_role = result_list[1]

            short_tag = nt.addon.getSetting("short_tag_list") == "true"
            temp_genre = ModelUtils.get_tags(body.get('tags', {}))
            if short_tag:
                temp_genre = temp_genre[:50]
            parent_key = body.get('id', '')
            grandparent_title = nt.decode(body.get('name', ''))

            if len(body.get('eps', {})) <= 0:
                # TODO: When there is eps {} = 0
                if is_fake == 0:
                    nt.error("No episodes in list")
                else:
                    thumb = ''
                    if len(body["art"]["thumb"]) > 0:
                        thumb = body["art"]["thumb"][0]["url"]
                        if thumb is not None and ":" not in thumb:
                            thumb = nt.server + thumb
                    details = {
                        'mediatype': 'episode',
                        'plot': nt.remove_anidb_links(nt.decode(body['summary'])),
                        'title': body['name'],
                        'rating': float(str(body.get('rating', '0')).replace(',', '.')),
                        'castandrole': list_cast_and_role,
                        'cast': list_cast,
                        'aired': body['air'],
                        'tvshowtitle': body['name'],
                        'size': nt.safe_int(body.get('size', '0')),
                        'genre': temp_genre,
                        'tagline': temp_genre
                    }
                    # it's fake, so no rating

                    extra_data = {
                        'source': 'ep',
                        'VideoStreams': defaultdict(dict),
                        'thumb': thumb,
                    }

                    # This sets a default duration of 0, just in case
                    extra_data['VideoStreams'][0]['duration'] = 0
                    u = sys.argv[0]
                    add_gui_item(u, details, extra_data, folder=False, index=int(episode_count - 1))
                    busy.close()
                    end_of_directory()

                    win_id = xbmcgui.getCurrentWindowId()
                    wind = xbmcgui.Window(win_id)
                    xbmc.sleep(1000)
                    control_id = wind.getFocusId()
                    control_list = wind.getControl(control_id)
                    # noinspection PyUnresolvedReferences
                    control_list.selectItem(1)

            elif len(body.get('eps', {})) > 0:
                # add item to move to next not played item (not marked as watched)
                if nt.addon.getSetting("show_continue") == "true":
                    if nt.decode(parent_title).lower() != "unsort":
                        nt.add_dir("-continue-", '', '7', os.path.join(_img, 'thumb', 'other.png'),
                                   "Next episode", os.path.join(_img, 'poster', 'other.png'), "4", str(next_episode))
                selected_list_item = False
                for video in body['eps']:
                    item_count += 1
                    # check if episode have files
                    episode_type = True
                    if "type" in params:
                        episode_type = True if str(video['eptype']) == str(params['type']) else False
                    if video['files'] is not None and episode_type:
                        if len(video['files']) > 0:
                            episode_count += 1
                            # Check for empty duration from MediaInfo check fail and handle it properly
                            tmp_duration = 1
                            try:
                                tmp_duration = video['files'][0]['duration']
                            except:
                                pass
                            if tmp_duration == 1:
                                duration = 1
                            else:
                                duration = int(tmp_duration) / 1000

                            if nt.addon.getSetting('kodi18') == 1:
                                duration = str(datetime.timedelta(seconds=duration))

                            # filter out invalid date
                            air = video.get('air', '')
                            if air != '':
                                # air=0001-01-01
                                if air == '0001-01-01' or air == '01-01-0001':
                                    air = ''
                            title = nt.decode(video.get('name', 'Parse util.error'))
                            if title is None:
                                title = 'Episode ' + str(video.get('epnumber', '??'))

                            watched = int(nt.safe_int(video.get("view", '0')))
                            # Required listItem entries for XBMC
                            details = {
                                # OFFICIAL General Values
                                # 'count': - can be used to store an id for later, or for sorting purposes
                                'size': nt.safe_int(video['files'][0].get('size', '0')),
                                # 'date': file date - coded below
                                # OFFICIAL Video Values
                                'genre': temp_genre,
                                # 'county':
                                'year': nt.safe_int(video.get('year', '')),
                                'episode': nt.safe_int(video.get('epnumber', '')),
                                #  'season' - coded below
                                #  'sortepisode'  # k18
                                #  'sortseason'  # k18
                                #  'episodeguide'  # k18
                                #  'showlink'  # k18
                                #  'top250'
                                #  'setid'
                                #  'tracknumber'
                                'rating': float(str(video.get('rating', '0')).replace(',', '.')),
                                'userrating': float(str(video.get('UserRating', '0')).replace(',', '.')),
                                #  'watched' - depreciated
                                #  'playcount' - coded below
                                #  'overlay' - cdeded below
                                'cast': list_cast,
                                'castandrole': list_cast_and_role,
                                #  'director': " / ".join(temp_dir),
                                #  'mpaa':          video.get('contentRating', ''), <--
                                'plot': nt.remove_anidb_links(nt.decode(video['summary'])),
                                #  'plotoutline':
                                'title': title,
                                'originaltitle': nt.decode(video.get('name', '')),
                                'sorttitle': str(video.get('epnumber', '')) + " " + title,
                                'duration': duration,
                                # 'studio'      : episode.get('studio',tree.get('studio','')), 'utf-8') ,
                                'tagline': temp_genre,  # short description of movie k18
                                # 'writer': " / ".join(temp_writer),
                                'tvshowtitle': grandparent_title,
                                'premiered': air,
                                #  'status': 'Continuing'
                                #  'set' -  name of the collection
                                #  'setoverview' - k18
                                'tag': temp_genre,  # k18
                                #  'imdbnumber'
                                #  'code' - production code
                                'aired': air,
                                #  'credits'
                                #  'lastplayed'
                                #  'album'
                                #  'artist'
                                'votes': nt.safe_int(video.get('votes', '')),
                                #  'path'
                                #  'trailes'
                                #  'dateadded'
                                'mediatype': 'episode',  # "video", "movie", "tvshow", "season", "episode", "musicvideo"
                                #  'dbid' - local kodi db id

                                # CUSTOM
                                'parenttitle':   nt.decode(parent_title)
                            }

                            if nt.addon.getSetting('hide_rating') == 'Always':
                                if nt.addon.getSetting('hide_rating_type') != 'Series':  # Episodes|Both
                                    details['rating'] = ''
                            elif nt.addon.getSetting('hide_rating') == 'Unwatched':
                                if nt.addon.getSetting(
                                        'hide_rating_type') != 'Series' and watched <= 0:  # Episodes|Both
                                    details['rating'] = ''

                            season = str(body.get('season', '1'))
                            try:
                                if season != '1':
                                    season = season.split('x')[0]
                            except Exception as w:
                                nt.error(w, season)
                            details['season'] = nt.safe_int(season)

                            temp_date = str(details['aired']).split('-')
                            if len(temp_date) == 3:  # format is 2016-01-24, we want it 24.01.2016
                                details['date'] = temp_date[1] + '.' + temp_date[2] + '.' + temp_date[0]

                            thumb = ''
                            if len(video["art"]["thumb"]) > 0:
                                thumb = video["art"]["thumb"][0]["url"]
                                if thumb is not None and ":" not in thumb:
                                    thumb = nt.server + thumb
                            fanart = ''
                            if len(video["art"]["fanart"]) > 0:
                                fanart = video["art"]["fanart"][0]["url"]
                                if fanart is not None and ":" not in fanart:
                                    fanart = nt.server + fanart
                            banner = ''
                            if len(video["art"]["banner"]) > 0:
                                banner = video["art"]["banner"][0]["url"]
                                if banner is not None and ":" not in banner:
                                    banner = nt.server + banner

                            key = video["files"][0]["url"]

                            # Extra data required to manage other properties
                            extra_data = {
                                'type':             'video',  # 'video'
                                'source':           'ep',
                                'thumb':            thumb,
                                'fanart_image':     fanart,
                                'banner':           banner,
                                'key':              key,
                                'resume':           int(int(video['files'][0].get('offset', '0')) / 1000),
                                'parentKey':        parent_key,
                                'jmmepisodeid':     nt.safe_int(body.get('id', '')),
                                'actors':           actors,
                                'VideoStreams':     defaultdict(dict),
                                'AudioStreams':     defaultdict(dict),
                                'SubStreams':       defaultdict(dict),
                                'ep_id':            nt.safe_int(video.get('id', '')),
                                'serie_id':         nt.safe_int(body.get('id', '')),
                                'file_id':          video['files'][0].get('offset', '0')
                            }

                            # Information about streams inside video file
                            if len(video["files"][0].get("media", {})) > 0:
                                ModelUtils.video_file_information(video['files'][0]['media'], extra_data)

                            # Determine what type of watched flag [overlay] to use
                            if watched > 0:
                                details['playcount'] = 1
                                details['overlay'] = 5
                                # details['lastplayed'] = '2010-10-10 11:00:00'
                            else:
                                details['playcount'] = 0
                                details['overlay'] = 4
                                if next_episode == -1:
                                    next_episode = episode_count - 1
                            select_this_item = False
                            if details['playcount'] == 0:
                                # if there was no other item select this on listitem
                                if not selected_list_item:
                                    select_this_item = True
                                    selected_list_item = True
                                # Hide plot and thumb for unwatched by kodi setting
                                if not nt.get_kodi_setting_bool("videolibrary.showunwatchedplots"):
                                    details['plot'] \
                                        = "Hidden due to user setting.\nCheck Show Plot" + \
                                          " for Unwatched Items in the Video Library Settings."
                                    extra_data['thumb'] = thumb
                                    extra_data['fanart_image'] = fanart

                            context = None

                            u = sys.argv[0]
                            u = nt.set_parameter(u, 'mode', 1)
                            u = nt.set_parameter(u, 'file_id', video["files"][0].get("id", 0))
                            u = nt.set_parameter(u, 'ep_id', video.get("id", ''))
                            u = nt.set_parameter(u, 'serie_id', body.get("id", ''))
                            u = nt.set_parameter(u, 'userrate', details["userrating"])
                            u = nt.set_parameter(u, 'ui_index', str(int(episode_count - 1)))

                            add_gui_item(u, details, extra_data, context,
                                         folder=False, index=int(episode_count - 1),
                                         force_select=select_this_item)

        except Exception as exc:
            nt.error("util.error during build_serie_episodes", str(exc))
    except Exception as exc:
        nt.error("Invalid JSON Received in build_serie_episodes", str(exc))
    if is_fake == 0:
        busy.close()
        end_of_directory(place='episode')
    # settings / media / videos / {advanced} / Select first unwatched tv show season,episode (always)
    if nt.get_kodi_setting_int('videolibrary.tvshowsselectfirstunwatcheditem') > 0 or \
            nt.addon.getSetting("select_unwatched") == "true":
        try:
            xbmc.sleep(150)
            new_window = xbmcgui.Window(xbmcgui.getCurrentWindowId())
            new_control = new_window.getControl(new_window.getFocusId())
            nt.move_position_on_list(new_control, next_episode)
        except:
            pass


def build_cast_menu(params):
    """
    Build the cast menu for 3.8.2+
    :param params:
    :return:
    """
    try:
        search_url = nt.server + "/api/cast/byseries"
        if params.get("serie_id", "") == "":
            return
        search_url = nt.set_parameter(search_url, 'id', params.get("serie_id", ""))
        search_url = nt.set_parameter(search_url, 'notag', 1)
        search_url = nt.set_parameter(search_url, 'level', 0)
        cast_nodes = nt.json.loads(nt.get_json(search_url))
        if nt.addon.getSetting("spamLog") == "true":
            nt.dump_dictionary(cast_nodes, "cast_nodes")

        base_search_url = nt.server + "/api/cast/search"
        base_search_url = nt.set_parameter(base_search_url, "fuzzy", 0)

        if len(cast_nodes) > 0:
            if cast_nodes[0].get("character", "") == "":
                return

            xbmcplugin.setContent(handle, 'tvshows')
            for cast in cast_nodes:
                character = cast.get(u"character", u"")
                character_image = nt.server + cast.get("character_image", "")
                character_description = cast.get("character_description")
                staff = cast.get("staff", "")
                staff_image = nt.server + cast.get("staff_image", "")

                liz = xbmcgui.ListItem(staff)
                new_search_url = nt.set_parameter(base_search_url, "query", staff)

                details = {
                    'mediatype': 'episode',
                    'title': staff,
                    'originaltitle': staff,
                    'sorttitle': staff,
                    'genre': character,

                }

                if character_description is not None:
                    character_description = nt.remove_anidb_links(character_description)
                    details['plot'] = character_description

                liz.setInfo(type="video", infoLabels=details)

                if staff_image != "":
                    liz.setArt({"thumb": staff_image,
                                "icon": staff_image,
                                "poster": staff_image})
                if character_image != "":
                    liz.setArt({"fanart": character_image})

                u = sys.argv[0]
                u = nt.set_parameter(u, 'mode', 1)
                u = nt.set_parameter(u, 'name', params.get('name', 'Cast'))
                u = nt.set_parameter(u, 'url', new_search_url)
                u = nt.set_parameter(u, 'cmd', 'searchCast')

                list_items.append((u, liz, True))

            end_of_directory(place='filter')
    except:
        nt.error("util.error in build_cast_menu")


def build_search_directory():
    """
    Build Search directory 'New Search' and read Search History
    :return:
    """
    items = [{
        "title": nt.addon.getLocalizedString(30224),
        "url": nt.server + "/api/serie",
        "mode": 3,
        "poster": "none",
        "icon": os.path.join(_img, 'icons', 'new-search.png'),
        "fanart": os.path.join(_img, 'backgrounds', 'new-search.jpg'),
        "type": "",
        "plot": "",
        "extras": "true-search"
    }, {
        "title": "[COLOR yellow]Clear Search Terms[/COLOR]",
        "url": "delete-all",
        "mode": 31,
        "poster": "none",
        "icon": os.path.join(_img, 'icons', 'clear-search.png'),
        "fanart": os.path.join(_img, 'backgrounds', 'clear-search.jpg'),
        "type": "",
        "plot": "",
        "extras": ""
    }]

    # read search history
    search_history = search.get_search_history()
    search_history.sort()
    for ss in search_history:
        try:
            if len(ss[0]) > 0:
                items.append({
                    "title": ss[0],
                    "url": nt.server + "/api/search",
                    "query": ss[0],
                    "mode": 3,
                    "poster": "none",
                    "icon": os.path.join(_img, 'icons', 'search.png'),
                    "fanart": os.path.join(_img, 'backgrounds', 'search.jpg'),
                    "type": "",
                    "plot": "",
                    "extras": "force-search",
                    "extras2": "db-search"
                })
        except:
            pass

    for detail in items:
        u = sys.argv[0]
        u = nt.set_parameter(u, 'url', detail['url'])
        u = nt.set_parameter(u, 'mode', detail['mode'])
        u = nt.set_parameter(u, 'name', nt.encode(detail['title']))
        u = nt.set_parameter(u, 'extras', detail['extras'])
        if 'query' in detail:
            u = nt.set_parameter(u, 'query', detail['query'])
        liz = xbmcgui.ListItem(nt.encode(detail['title']))
        liz.setArt({'thumb': detail['icon'],
                    'poster': detail['poster'],
                    'icon': detail['icon'],
                    'fanart': detail['fanart']})
        liz.setInfo(type=detail['type'], infoLabels={"Title": nt.encode(detail['title']), "Plot": detail['plot']})
        list_items.append((u, liz, True))
    end_of_directory(False)


def build_serie_soon(params):
    """
        Builds the list of items for Calendar via Directory and ListItems ( Basic Mode )
        Args:
            params:
        Returns:

        """
    xbmcplugin.setContent(handle, 'tvshows')
    xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_UNSORTED)

    try:
        busy.create(nt.addon.getLocalizedString(30160), nt.addon.getLocalizedString(30161))
        busy.update(20)
        temp_url = params['url']
        temp_url = nt.set_parameter(temp_url, 'level', 2)

        busy.update(10)
        temp_url = nt.set_parameter(temp_url, 'nocast', 0)
        temp_url = nt.set_parameter(temp_url, 'notag', 0)
        temp_url = nt.set_parameter(temp_url, 'level', 0)
        busy.update(20)
        html = nt.get_json(temp_url)
        busy.update(50, nt.addon.getLocalizedString(30162))
        if nt.addon.getSetting("spamLog") == "true":
            xbmc.log(params['url'], xbmc.LOGWARNING)
            xbmc.log(html, xbmc.LOGWARNING)
        busy.update(70)
        temp_url = params['url']
        temp_url = nt.set_parameter(temp_url, 'level', 2)
        html = nt.get_json(temp_url)
        body = nt.json.loads(html)
        busy.update(100)
        busy.close()

        # check if this is maybe filter-inception
        try:
            KodiUtils.set_window_heading(body.get('name', ''))
        except:
            KodiUtils.set_window_heading(nt.addon.getLocalizedString(30222))

        try:
            item_count = 0
            parent_title = body.get('name', '')
            used_dates = []
            for sers in body['series']:
                # region add_date
                if sers.get('air', '') in used_dates:
                    pass
                else:
                    used_dates.append(sers.get('air', ''))
                    soon_url = nt.server + "/api/serie/soon"
                    details = {'aired': sers.get('air', ''), 'title': sers.get('air', '')}
                    u = sys.argv[0]
                    u = nt.set_parameter(u, 'url', soon_url)
                    u = nt.set_parameter(u, 'mode', str(0))
                    u = nt.set_parameter(u, 'name', nt.quote_plus(details.get('title', '')))
                    extra_data = {'type': 'pictures'}
                    add_gui_item(u, details, extra_data)
                # endregion

                add_serie_item(sers, parent_title)
                item_count += 1

        except Exception as e:
            nt.error("util.error during build_serie_soon date_air", str(e))
    except Exception as e:
        nt.error("Invalid JSON Received in build_serie_soon", str(e))
    end_of_directory()


def build_raw_list(params):
    """
    Build list of RawFiles (ex. Unsort)
    :param params: json body with all files to draw
    :return:
    """
    xbmcplugin.setContent(handle, 'videos')
    KodiUtils.set_window_heading(nt.addon.getLocalizedString(30106))
    try:
        html = nt.get_json(params['url'])
        body = nt.json.loads(html)
        if nt.addon.getSetting("spamLog") == "true":
            xbmc.log(html, xbmc.LOGWARNING)

        try:
            for file_body in body:
                add_raw_files(file_body)
        except Exception as exc:
            nt.error("util.error during build_raw_list add_raw_files", str(exc))
    except Exception as exc:
        nt.error("util.error during build_raw_list", str(exc))

    end_of_directory(False)


def build_network_menu():
    """
    Build fake menu that will alert user about network util.error (unable to connect to api)
    """
    network_url = nt.server + "/api/version"
    title = nt.addon.getLocalizedString(30197)
    liz = xbmcgui.ListItem(label=title, label2=title, path=network_url)
    liz.setArt({"icon": os.path.join(_img, 'icons', 'settings.png'),
                "fanart": os.path.join(_img, 'backgrounds', 'settings.jpg')})
    liz.setInfo(type="Video", infoLabels={"Title": title, "Plot": title})
    u = sys.argv[0]
    u = nt.set_parameter(u, 'url', network_url)
    u = nt.set_parameter(u, 'name', nt.quote_plus(title))
    list_items.append((u, liz, True))
    end_of_directory(False)


def search_for(search_url):
    """
    Actually do the search and build the result
    :param search_url: search url with query
    """
    try:
        search_url = nt.set_parameter(search_url, 'tags', 2)
        search_url = nt.set_parameter(search_url, 'level', 1)
        search_url = nt.set_parameter(search_url, 'limit', nt.addon.getSetting('maxlimit'))
        search_url = nt.set_parameter(search_url, 'limit_tag', nt.addon.getSetting('maxlimit_tag'))
        json_body = nt.json.loads(nt.get_json(search_url))
        if json_body["groups"][0]["size"] == 0:
            xbmc.executebuiltin("XBMC.Notification(%s, %s %s, 7500, %s)" % (nt.addon.getLocalizedString(30180),
                                                                            nt.addon.getLocalizedString(30181),
                                                                            '!', nt.addon.getAddonInfo('icon')))
        else:
            search_url = nt.parse_parameters(search_url)
            build_groups_menu(search_url, json_body)
    except:
        nt.error("util.error in findVideo")


def execute_search_and_add_query():
    """
    Build a search query and if its not in Search History add it
    """
    find = nt.search_box()
    # check search history
    if find == '':
        build_search_directory()
        return
    if not search.check_in_database(find):
        # if its not add to history & refresh
        search.add_search_history(find)
        xbmc.executebuiltin('Container.Refresh')
    search_url = nt.server + "/api/search"
    search_url = nt.set_parameter(search_url, "query", find)
    search_for(search_url)


def create_playlist(serie_id):
    """
    Create playlist of all episodes that wasn't watched
    :param serie_id:
    :return:
    """
    serie_url = nt.server + "/api/serie?id=" + str(serie_id) + "&level=2&nocast=1&notag=1"
    serie_body = nt.json.loads(nt.get_json(serie_url))
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlist.clear()
    item_count = 0
    # TODO sort by epnumber and eptype so it wont get mixed
    if 'eps' in serie_body:
        if len(serie_body['eps']) > 0:
            for serie in serie_body['eps']:
                if len(serie['files']) > 0:
                    if 'view' in serie:
                        if serie['view'] == 1:
                            continue
                    video = serie['files'][0]['url']
                    details = add_serie_item(serie, serie_body['name'], True)
                    liz = xbmcgui.ListItem(details.get('title', 'Unknown'))
                    liz.setInfo(type='Video', infoLabels=details)
                    item_count += 1
                    playlist.add(url=video, listitem=liz, index=item_count)
    if item_count > 0:
        xbmc.Player().play(playlist)


def build_shoko_menu():
    """
    build menu with items to interact with shoko server via api
    :return:
    """
    xbmcplugin.setContent(handle, 'tvshows')
    KodiUtils.set_window_heading(nt.addon.getLocalizedString(30115))

    items = [{
        "title": nt.addon.getLocalizedString(30122),
        "cmd": "missing",
        "poster": "none",
        "icon": os.path.join(_img, 'icons', 'new-search.png'),
        "fanart": os.path.join(_img, 'backgrounds', 'new-search.jpg'),
        "type": "video",
        "plot": nt.addon.getLocalizedString(30135),
        "extras": ""
    }, {
        "title": nt.addon.getLocalizedString(30117),
        "cmd": "statsupdate",
        "poster": "none",
        "icon": os.path.join(_img, 'icons', 'new-search.png'),
        "fanart": os.path.join(_img, 'backgrounds', 'new-search.jpg'),
        "type": "video",
        "plot": nt.addon.getLocalizedString(30136),
        "extras": ""
    }, {
        "title": nt.addon.getLocalizedString(30118),
        "cmd": "mediainfo",
        "poster": "none",
        "icon": os.path.join(_img, 'icons', 'new-search.png'),
        "fanart": os.path.join(_img, 'backgrounds', 'new-search.jpg'),
        "type": "video",
        "plot": nt.addon.getLocalizedString(30137),
        "extras": ""
    }, {
        "title": nt.addon.getLocalizedString(30120),
        "cmd": "rescan",
        "poster": "none",
        "icon": os.path.join(_img, 'icons', 'new-search.png'),
        "fanart": os.path.join(_img, 'backgrounds', 'new-search.jpg'),
        "type": "video",
        "plot": nt.addon.getLocalizedString(30138),
        "extras": "",
        "vl": ""
    }, {
        "title": nt.addon.getLocalizedString(30121),
        "cmd": "rehash",
        "poster": "none",
        "icon": os.path.join(_img, 'icons', 'new-search.png'),
        "fanart": os.path.join(_img, 'backgrounds', 'new-search.jpg'),
        "type": "video",
        "plot": nt.addon.getLocalizedString(30139),
        "extras": "",
        "vl": ""
    }, {
        "title": nt.addon.getLocalizedString(30116),
        "cmd": "folderlist",
        "poster": "none",
        "icon": os.path.join(_img, 'icons', 'new-search.png'),
        "fanart": os.path.join(_img, 'backgrounds', 'new-search.jpg'),
        "type": "video",
        "plot": nt.addon.getLocalizedString(30140),
        "extras": "",
    }]

    for detail in items:
        u = sys.argv[0]
        if 'cmd' in detail:
            u = nt.set_parameter(u, 'cmd', detail['cmd'])
        if 'vl' in detail:
            u = nt.set_parameter(u, 'vl', detail['vl'])
        u = nt.set_parameter(u, 'name', nt.encode(detail['title']))
        u = nt.set_parameter(u, 'extras', detail['extras'])
        liz = xbmcgui.ListItem(nt.encode(detail['title']))
        liz.setArt({'thumb': detail['icon'],
                    'poster': detail['poster'],
                    'icon': detail['icon'],
                    'fanart': detail['fanart']})
        liz.setInfo(type=detail['type'], infoLabels={"Title": nt.encode(detail['title']), "Plot": detail['plot']})
        list_items.append((u, liz, True))
    end_of_directory(False)
