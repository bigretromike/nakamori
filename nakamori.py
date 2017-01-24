#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import json

import resources.lib.TagBlacklist as TagFilter
import resources.lib.util as util

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

from resources.lib.util import *

from collections import defaultdict
from distutils.version import LooseVersion

try:
    import pydevd
except ImportError:
    pass

handle = int(sys.argv[1])

__addon__ = xbmcaddon.Addon(id='plugin.video.nakamori')
__addonversion__ = __addon__.getAddonInfo('version')
__addonid__ = __addon__.getAddonInfo('id')

_server_ = "http://" + __addon__.getSetting("ipaddress") + ":" + __addon__.getSetting("port")


def valid_user():
    """
    Logs into the server and stores the apikey, then checks if the userid is valid
    :return: bool True if all completes successfully
    """
    version = get_version()
    if version == 'legacy' or version == '3.6.1.0':
        error('Please upgrade Shoko', 'You are using unsupported version of Shoko.')
        return False

    # reset apikey if user enters new login info
    # if apikey is present login should be empty as its not needed anymore
    if __addon__.getSetting("apikey") != "" and __addon__.getSetting("login") == "":
        return True
    else:
        xbmc.log('-- apikey empty --')
        # password can be empty as JMM Default account have blank password
        try:
            if __addon__.getSetting("login") != "" and __addon__.getSetting("device") != "":
                body = '{"user":"' + __addon__.getSetting("login") + '",' + \
                       '"device":"' + __addon__.getSetting("device") + '",' + \
                       '"pass":"' + __addon__.getSetting("password") + '"}'
                post_body = post_data(_server_ + "/api/auth", body)
                auth = json.loads(post_body)
                if "apikey" in auth:
                    xbmc.log('-- save apikey and reset user credentials --')
                    __addon__.setSetting(id='apikey', value=str(auth["apikey"]))
                    __addon__.setSetting(id='login', value='')
                    __addon__.setSetting(id='password', value='')
                    return True
                else:
                    raise Exception('Error Getting apikey')
            else:
                xbmc.log('-- Login and Device Empty --')
                return False
        except Exception as exc:
            error('Error in Valid_User', str(exc))
            return False


# TODO: to-check
def refresh():
    """
    Refresh and re-request data from server
    """
    # refresh watch status as we now mark episode and refresh list so it show real status not kodi_cached
    xbmc.executebuiltin('Container.Refresh')
    # Allow time for the ui to reload (this may need to be tweaked, I am running on localhost)
    xbmc.sleep(int(__addon__.getSetting('refresh_wait')))


# TODO: to-check
# use episode number for position
def move_position_on_list(control_list, position=0):
    """
    Move to the position in a list
    Args:
        control_list: the list control
        position: the index of the item not including settings
    """
    if position < 0:
        position = 0
    if __addon__.getSetting('show_continue') == 'true':
        position = int(position + 1)

    if get_kodi_setting_bool("filelists.showparentdiritems"):
        position = int(position + 1)

    try:
        control_list.selectItem(position)
    except:
        try:
            control_list.selectItem(position - 1)
        except Exception as e:
            error('Unable to reselect item', str(e))
            xbmc.log('control_list: ' + str(control_list.getId()), xbmc.LOGWARNING)
            xbmc.log('position: ' + str(position), xbmc.LOGWARNING)


def set_window_heading(window_name):
    """
    Sets the window titles
    Args:
        window_name: name to put in titles
    """
    window_obj = xbmcgui.Window(xbmcgui.getCurrentWindowId())
    try:
        window_obj.setProperty("heading", str(window_name))
    except Exception as e:
        error('set_window_heading Exception', str(e))
        window_obj.clearProperty("heading")
    try:
        window_obj.setProperty("heading2", str(window_name))
    except Exception as e:
        error('set_window_heading2 Exception', str(e))
        window_obj.clearProperty("heading2")


def filter_gui_item_by_tag(title):
    """
    Remove list items from the tag group filter by the tag blacklist in settings
    Args:
        title: the title of the list item

    Returns: Whether or not to remove it (true is yes)
    :rtype: bool
    """
    str1 = [title]
    str1 = TagFilter.processTags(__addon__, str1)
    return len(str1) > 0


# TODO: only context menu need to be redone
def add_gui_item(url, details, extra_data, context=None, folder=True, index=0):
    """Adds an item to the menu and populates its info labels
    :param url:The URL of the menu or file this item links to
    :param details:Data such as info labels
    :param extra_data:Data such as stream info
    :param context:The context menu
    :param folder:Is it a folder or file
    :param index:Index in the list
    :type url:str
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
        tp = 'Video'
        link_url = ""

        # do this before so it'll log
        # use the year as a fallback in case the date is unavailable
        if details.get('date', '') == '':
            if details.get('year', '') != '' and details['year'] != 0:
                details['date'] = '01.01.' + str(details['year'])
                details['aired'] = details['date']

        if __addon__.getSetting("spamLog") == 'true':
            xbmc.log("add_gui_item - url: " + url, xbmc.LOGWARNING)
            if details is not None:
                xbmc.log("add_gui_item - details", xbmc.LOGWARNING)
                for i in details:
                    temp_log = ""
                    a = details.get(encode(i))
                    if a is None:
                        temp_log = "\'unset\'"
                    elif isinstance(a, list) or isinstance(a, dict):
                        for b in a:
                            temp_log = str(b) if temp_log == "" else temp_log + " | " + str(b)
                    else:
                        temp_log = str(a)
                    xbmc.log("-" + str(i) + "- " + temp_log, xbmc.LOGWARNING)
            if extra_data is not None:
                xbmc.log("add_gui_item - extra_data", xbmc.LOGWARNING)
                for i in extra_data:
                    temp_log = ""
                    a = extra_data.get(encode(i))
                    if a is None:
                        temp_log = "\'unset\'"
                    elif isinstance(a, list) or isinstance(a, dict):
                        for b in a:
                            temp_log = str(b) if temp_log == "" else temp_log + " | " + str(b)
                    else:
                        temp_log = str(a)
                    xbmc.log("-" + str(i) + "- " + temp_log, xbmc.LOGWARNING)

        if extra_data is not None and len(extra_data) > 0:
            if extra_data.get('parameters'):
                for argument, value in extra_data.get('parameters').items():
                    link_url = "%s&%s=%s" % (link_url, argument, urllib.quote(value))
            tbi = extra_data.get('thumb', '')
            tp = extra_data.get('type', 'Video')
        if details.get('parenttitle', '').lower() == 'tags':
            if not filter_gui_item_by_tag(details.get('title', '')):
                return

        liz = xbmcgui.ListItem(details.get('title', 'Unknown'))
        if tbi is not None and len(tbi) > 0:
            liz.setArt({'thumb': tbi})
            liz.setArt({'poster': tbi})

        if extra_data is not None and len(extra_data) > 0:
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

        # For all video items
        if not folder:
            liz.setProperty('IsPlayable', 'true')
            if extra_data and len(extra_data) > 0:
                if extra_data.get('type', 'video').lower() == "video":
                    liz.setProperty('TotalTime', str(extra_data.get('duration')))
                    liz.setProperty('ResumeTime', str(extra_data.get('resume')))

                    liz.setProperty('VideoResolution', str(extra_data.get('xVideoResolution', '')))
                    liz.setProperty('VideoCodec', extra_data.get('xVideoCodec', ''))
                    liz.setProperty('AudioCodec', extra_data.get('xAudioCodec', ''))
                    liz.setProperty('AudioChannels', str(extra_data.get('xAudioChannels', '')))
                    liz.setProperty('VideoAspect', str(extra_data.get('xVideoAspect', '')))

                    video_codec = {}
                    if extra_data.get('VideoCodec'):
                        video_codec['codec'] = extra_data.get('VideoCodec')
                    if extra_data.get('height'):
                        video_codec['height'] = int(extra_data.get('height'))
                    if extra_data.get('width'):
                        video_codec['width'] = int(extra_data.get('width'))
                    if extra_data.get('xVideoAspect'):
                        video_codec['aspect'] = float(extra_data.get('xVideoAspect'))
                    if extra_data.get('duration'):
                        video_codec['duration'] = extra_data.get('duration')

                    if __addon__.getSetting("spamLog") == 'true':
                        xbmc.log("add_gui_item - video codec", xbmc.LOGWARNING)
                        for i in video_codec:
                            temp_log = ""
                            a = video_codec.get(encode(i))
                            if a is None:
                                temp_log = "\'unset\'"
                            elif isinstance(a, list):
                                for b in a:
                                    temp_log = str(b) if temp_log == "" else temp_log + " | " + str(b)
                            else:
                                temp_log = str(a)
                            xbmc.log("-" + str(i) + "- " + temp_log, xbmc.LOGWARNING)
                    liz.addStreamInfo('video', video_codec)

                    if extra_data.get('AudioStreams'):
                        for stream in extra_data['AudioStreams']:
                            liz.setProperty('AudioCodec.' + str(stream), str(extra_data['AudioStreams'][stream]
                                                                             ['AudioCodec']))
                            liz.setProperty('AudioChannels.' + str(stream), str(extra_data['AudioStreams'][stream]
                                                                                ['AudioChannels']))
                            audio_codec = dict()
                            audio_codec['codec'] = str(extra_data['AudioStreams'][stream]['AudioCodec'])
                            audio_codec['channels'] = int(extra_data['AudioStreams'][stream]['AudioChannels'])
                            audio_codec['language'] = str(extra_data['AudioStreams'][stream]['AudioLanguage'])
                            if __addon__.getSetting("spamLog") == 'true':
                                xbmc.log("add_gui_item - audio codec", xbmc.LOGWARNING)
                                for i in audio_codec:
                                    temp_log = ""
                                    a = audio_codec.get(encode(i))
                                    if a is None:
                                        temp_log = "\'unset\'"
                                    elif isinstance(a, list):
                                        for b in a:
                                            temp_log = str(b) if temp_log == "" else temp_log + " | " + str(b)
                                    else:
                                        temp_log = str(a)
                                    xbmc.log("-" + str(i) + "- " + temp_log, xbmc.LOGWARNING)
                            liz.addStreamInfo('audio', audio_codec)
                    if extra_data.get('SubStreams'):
                        for stream2 in extra_data['SubStreams']:
                            liz.setProperty('SubtitleLanguage.' + str(stream2), str(extra_data['SubStreams'][stream2]
                                                                                    ['SubtitleLanguage']))
                            subtitle_codec = dict()
                            subtitle_codec['language'] = str(extra_data['SubStreams'][stream2]['SubtitleLanguage'])
                            liz.addStreamInfo('subtitle', subtitle_codec)

            # UMS/PSM Jumpy plugin require 'path' to play video
            partemp = util.parseParameters(input_string=url)
            liz.setProperty('path', str(partemp.get('file', 'empty')))

        # TODO: with source = type (filter, group, series, ep) this section need tweaks
        if extra_data and len(extra_data) > 0:
            if extra_data.get('source') == 'serie' or extra_data.get('source') == 'group':
                # Then set the number of watched and unwatched, which will be displayed per season
                liz.setProperty('TotalEpisodes', str(extra_data['TotalEpisodes']))
                liz.setProperty('WatchedEpisodes', str(extra_data['WatchedEpisodes']))
                liz.setProperty('UnWatchedEpisodes', str(extra_data['UnWatchedEpisodes']))
                # Hack to show partial flag for TV shows and seasons
                if extra_data.get('partialTV') == 1:
                    liz.setProperty('TotalTime', '100')
                    liz.setProperty('ResumeTime', '50')
                if extra_data.get('thumb'):
                    liz.setArt({"thumb": extra_data.get('thumb', '')})
                    liz.setArt({"poster": extra_data.get('thumb', '')})
                if extra_data.get('fanart_image'):
                    liz.setArt({"fanart": extra_data.get('fanart_image', '')})
                    liz.setArt({"clearart": extra_data.get('fanart_image', '')})
                if extra_data.get('banner'):
                    liz.setArt({'banner': extra_data.get('banner', '')})
                if extra_data.get('season_thumb'):
                    liz.setArt({'seasonThumb': extra_data.get('season_thumb', '')})

# TODO: This need to review
        if context is None:
            if extra_data and len(extra_data) > 0:
                if extra_data.get('type', 'video').lower() == "video":
                    context = []
                    url_peep_base = sys.argv[2]
                    my_len = len(_server_)

                    if extra_data.get('source', 'none') == 'AnimeSerie':
                        series_id = extra_data.get('key')[(my_len + 30):]
                        url_peep = url_peep_base + "&anime_id=" + series_id + "&cmd=voteSer"
                        if __addon__.getSetting('context_show_info') == 'true':
                            context.append(('More Info', 'Action(Info)'))
                        if __addon__.getSetting('context_show_vote_Series') == 'true':
                            context.append(('Vote (Shoko)', 'RunScript(plugin.video.nakamori, %s, %s)' %
                                            (sys.argv[1], url_peep)))
                        url_peep = url_peep_base + "&anime_id=" + series_id
                        context.append(('Mark as Watched (Shoko)',
                                        'RunScript(plugin.video.nakamori, %s, %s&cmd=watched)'
                                        % (sys.argv[1], url_peep)))
                        context.append(('Mark as Unwatched (Shoko)',
                                        'RunScript(plugin.video.nakamori, %s, %s&cmd=unwatched)'
                                        % (sys.argv[1], url_peep)))
                    elif extra_data.get('source', 'none') == 'AnimeGroup':
                        series_id = extra_data.get('key')[(my_len + 30):]
                        if __addon__.getSetting('context_show_info') == 'true':
                            context.append(('More Info', 'Action(Info)'))
                        url_peep = url_peep_base + "&group_id=" + series_id
                        context.append(('Mark as Watched (Shoko)',
                                        'RunScript(plugin.video.nakamori, %s, %s&cmd=watched)'
                                        % (sys.argv[1], url_peep)))
                        context.append(('Mark as Unwatched (Shoko)',
                                        'RunScript(plugin.video.nakamori, %s, %s&cmd=unwatched)'
                                        % (sys.argv[1], url_peep)))
                    elif extra_data.get('source', 'none') == 'tvepisodes':
                        #series_id = extra_data.get('parentKey')[(my_len + 30):] <----
                        series_id = "331122"
                        url_peep = url_peep_base + "&anime_id=" + str(series_id) + \
                            "&ep_id=" + str(extra_data.get('jmmepisodeid')) + '&ui_index=' + str(index)
                        if not extra_data.get('unsorted', False):
                            if __addon__.getSetting('context_show_play_no_watch') == 'true':
                                context.append(('Play (Do not Mark as Watched (Shoko))',
                                                'RunScript(plugin.video.nakamori, %s, %s&cmd=no_mark)'
                                                % (sys.argv[1], url_peep)))
                        if __addon__.getSetting('context_show_info') == 'true':
                            context.append(('More Info', 'Action(Info)'))
                        if __addon__.getSetting('context_show_vote_Series') == 'true' and not extra_data.get('unsorted',
                                                                                                             False):
                            if series_id != '':
                                context.append(
                                    ('Vote for Series (Shoko)',
                                     'RunScript(plugin.video.nakamori, %s, %s&cmd=voteSer)'
                                     % (sys.argv[1], url_peep)))
                        if __addon__.getSetting('context_show_vote_Episode') == 'true' and not extra_data.get(
                                'unsorted', False):
                            if extra_data.get('jmmepisodeid') != '':
                                context.append(
                                    ('Vote for Episode (Shoko)',
                                     'RunScript(plugin.video.nakamori, %s, %s&cmd=voteEp)'
                                     % (sys.argv[1], url_peep)))

                        if extra_data.get('jmmepisodeid') != '' and not extra_data.get('unsorted', False):
                            if __addon__.getSetting('context_krypton_watched') == 'true':
                                if details.get('playcount', 0) == 0:
                                    context.append(
                                        ('Mark as Watched (Shoko)',
                                         'RunScript(plugin.video.nakamori, %s, %s&cmd=watched)'
                                         % (sys.argv[1], url_peep)))
                                else:
                                    context.append(
                                        ('Mark as Unwatched (Shoko)',
                                         'RunScript(plugin.video.nakamori, %s, %s&cmd=unwatched)'
                                         % (sys.argv[1], url_peep)))
                            else:
                                context.append(
                                    ('Mark as Watched (Shoko)',
                                     'RunScript(plugin.video.nakamori, %s, %s&cmd=watched)'
                                     % (sys.argv[1], url_peep)))
                                context.append(
                                    ('Mark as Unwatched (Shoko)',
                                     'RunScript(plugin.video.nakamori, %s, %s&cmd=unwatched)'
                                     % (sys.argv[1], url_peep)))

                        if extra_data.get('unsorted', False):
                            context.append(
                                ('Rescan File',
                                 'RunScript(plugin.video.nakamori, %s, %s&cmd=rescan)'
                                 % (sys.argv[1], url_peep)))
                            context.append(
                                ('Rehash File',
                                 'RunScript(plugin.video.nakamori, %s, %s&cmd=rehash)'
                                 % (sys.argv[1], url_peep)))
                    liz.addContextMenuItems(context)
        return xbmcplugin.addDirectoryItem(handle, url, listitem=liz, isFolder=folder)
    except Exception as e:
        error("Error during add_gui_item", str(e))


def set_watch_flag(extra_data, details):
    """
    Set the flag icon for the list item to the desired state based on watched episodes
    Args:
        extra_data: the extra_data dict
        details: the details dict
    """
    # TODO: Real watch progress instead of 0,50,100%
    # Set up overlays for watched and unwatched episodes
    if extra_data['WatchedEpisodes'] == 0:
        details['playcount'] = 0
    elif extra_data['UnWatchedEpisodes'] == 0:
        details['playcount'] = 1
    else:
        extra_data['partialTV'] = 1


# TODO: to-check [if working correctly]
def get_title(data):
    """
    Get the new title
    Args:
        data: json xml node containing the title

    Returns: string of the desired title

    """
    try:
        if __addon__.getSetting('use_server_title') == 'true':
            return encode(data["title"])
        # xbmc.log(data.get('title', 'Unknown'))
        title = encode(data["title"].lower())
        if title == 'ova' or title == 'ovas' \
                or title == 'episode' or title == 'episodes' \
                or title == 'special' or title == 'specials' \
                or title == 'parody' or title == 'parodies' \
                or title == 'credit' or title == 'credits' \
                or title == 'trailer' or title == 'trailers' \
                or title == 'other' or title == 'others':
            return encode(data["title"])

        lang = __addon__.getSetting("displaylang")
        title_type = __addon__.getSetting("title_type")
        try:
            for titleTag in data["titles"]:
                if titleTag["Type"].lower() == title_type.lower():
                    if titleTag["Language"].lower() == lang.lower():
                        return encode(titleTag["Title"])
            # fallback on language any title
            for titleTag in data["titles"]:
                if titleTag["Type"].lower() != 'short':
                    if titleTag["Language"].lower() == lang.lower():
                        return encode(titleTag["Title"])
            # fallback on x-jat main title
            for titleTag in data["titles"]:
                if titleTag["Type"].lower() == 'main':
                    if titleTag["Language"].lower() == 'x-jat':
                        return encode(titleTag["Title"])
            # fallback on directory title
            return encode(data["title"])
        except Exception as expc:
            error('Error thrown on getting title', str(expc))
            return encode(data["title"])
    except Exception as exw:
        error("get_title Exception", str(exw))
        return 'Error'


def get_tags(tag_node):
    """
    Get the tags from the new style
    Args:
        tag_node: node containing group

    Returns: a string of all of the tags formatted

    """
    try:
        if len(tag_node) > 0:
            temp_genres = []
            for tag in tag_node:
                temp_genre = encode(tag["tag"]).strip()
                temp_genres.append(temp_genre)
                temp_genres = TagFilter.processTags(__addon__, temp_genres)
                temp_genre = " | ".join(temp_genres)
            return temp_genre
        else:
            return ''
    except Exception as exc:
        error('Error generating tags', str(exc))
        return ''


def get_cast_and_role(data):
    """
    Get cast from the json and arrange in the new setCast format
    Args:
        data: json node containing 'roles'

    Returns: a list of dictionaries for the cast
    """
    result_list = []
    if data is not None:
        for char in data:
            char_charname = char["role"]
            char_seiyuuname = char["name"]
            char_seiyuupic = char["rolepic"]

            # only add it if it has data
            # reorder these to match the convention (Actor is cast, character is role, in that order)
            if len(char_charname) != 0:
                actor = {
                    'name':         char_seiyuuname,
                    'role':         char_charname,
                    'thumbnail':    char_seiyuupic
                }
                result_list.append(actor)
        if len(result_list) == 0:
            return None
        return result_list
    return None


# TODO: legacy - do we need this, or is it proper function with bad name ?
def convert_cast_and_role_to_legacy(list_of_dicts):
    result_list = []
    list_cast = []
    list_cast_and_role = []
    if len(list_of_dicts) > 0:
        for actor in list_of_dicts:
            seiyuu = actor.get('name', '')
            role = actor.get('role', '')
            if len(role) != 0:
                list_cast.append(role)
                if len(seiyuu) != 0:
                    list_cast_and_role.append((seiyuu, role))
        result_list.append(list_cast)
        result_list.append(list_cast_and_role)
    return result_list


# Adding items to list/menu:


def add_content_typ_dir(name, serie_id, ep_type):
    """
    Adding directories for given types of content
    :param name: name of directory
    :param serie_id: id that the content belong too
    :param ep_type: type of content
    :return: add new directory
    """
    url = _server_ + "/api/serie?id=" + str(serie_id) + "&level=4"
    title = str(name)
    # TODO : add proper icon
    thumb = _server_ + "/image/support/plex_others.png"
    liz = xbmcgui.ListItem(label=title, label2=title, path=url)
    liz.setArt({'thumb': thumb, 'poster': thumb, 'icon': 'DefaultVideo.png'})
    liz.setInfo(type="Video", infoLabels={"Title": title, "Plot": title})
    u = sys.argv[0]
    u = set_parameter(u, 'url', url)
    u = set_parameter(u, 'mode', str(6))
    u = set_parameter(u, 'name', urllib.quote_plus(title))
    u = set_parameter(u, 'type', ep_type)
    xbmcplugin.addDirectoryItem(handle, url=u, listitem=liz, isFolder=True)


def add_serie_item(node, parent_title):
    #xbmcgui.Dialog().ok('series', 'series')
    temp_genre = get_tags(node["tags"])
    watched = int(node["viewed"])

    list_cast = []
    list_cast_and_role = []
    actors = []
    if len(list_cast) == 0:
        result_list = get_cast_and_role(node["roles"])
        actors = result_list
        # TODO: need this ?
        if result_list is not None:
            result_list = convert_cast_and_role_to_legacy(result_list)
            list_cast = result_list[0]
            list_cast_and_role = result_list[1]

    if __addon__.getSetting("local_total") == "true":
        total = safeInt(node["localsize"])
    else:
        total = safeInt(node["size"])
    title = get_title(node)
    if node["userrating"] is not None:
        userrating = str(node["userrating"]).replace(',', '.')
    else:
        userrating = 0.0

    details = {
        'title':            title,
        'parenttitle':      encode(parent_title),
        'genre':            temp_genre,
        'year':             safeInt(node["year"]),
        'episode':          total,
        'season':           safeInt(node["season"]),
        # 'count'        : count,
        'size':             total,
        'Date':             node["air"],
        'rating':           float(str(node["rating"]).replace(',', '.')),
        'userrating':       float(userrating),
        'playcount':        int(node["viewed"]),
        # overlay        : integer (2, - range is 0..8. See GUIListItem.h for values
        'cast':             list_cast,  # cast : list (Michal C. Hall,
        'castandrole':      list_cast_and_role,
        # director       : string (Dagur Kari,
        ### 'mpaa':             directory.get('contentRating', ''),
        'plot':             remove_anidb_links(encode(node["summary"])),
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
        'aired':            node["air"],
        # credits        : string (Andy Kaufman, - writing credits
        # 'Lastplayed'   : lastplayed,
        ### 'votes':            directory.get('votes'),
        # trailer        : string (/home/user/trailer.avi,
        ### 'dateadded':        directory.get('addedAt')
    }
    temp_date = str(node["air"]).split('-')
    if len(temp_date) == 3:  # format is 24-01-2016, we want it 24.01.2016
        details['date'] = temp_date[0] + '.' + temp_date[1] + '.' + temp_date[2]

    directory_type = str(node["type"])
    key_id = str(node["id"])
    key = _server_ + "/api/serie?id=" + key_id
    # TODO: filter_id onc again
    #directory_type = directory.get('AnimeType', '')
    #key = directory.get('key', '')
    #filterid = ''
    #if get_version() > LooseVersion(
    #        '3.6.1.0') and directory_type != 'AnimeType' and directory_type != 'AnimeSerie':
    #    if params.get('filterid', '') != '':
    #        filterid = params.get('filterid', '')
    #        if directory_type == 'AnimeGroupFilter':
    #            filterid = directory.get('GenericId', '')
    #        length = len(_server_
    #                     + "jmmserverkodi/getmetadata/" + __addon__.getSetting("userid") + "/") + 1
    #        key = key[length:]
    #        key = _server_ \
    #              + "/api/metadata/" + key + '/' + filterid

    thumb = ''
    if len(node["art"]["thumb"]) > 0:
        thumb = node["art"]["thumb"][0]["url"]
    fanart = ''
    if len(node["art"]["fanart"]) > 0:
        fanart = node["art"]["fanart"][0]["url"]
    banner = ''
    if len(node["art"]["banner"]) > 0:
        banner = node["art"]["banner"][0]["url"]

    extra_data = {
        'type':                 'video',
        'source':               directory_type,
        'UnWatchedEpisodes':    int(details['episode']) - watched,
        'WatchedEpisodes':      watched,
        'TotalEpisodes':        details['episode'],
        'thumb':                thumb,
        'fanart_image':         fanart,
        'banner':               banner,
        'key':                  key,
        'actors':               actors
    }
    if __addon__.getSetting('request_nocast') == 'true':
        key += '&nocast=1'

    url = key
    set_watch_flag(extra_data, details)
    use_mode = 5
    # TODO: re-check logic as data/1/2 is no longer
    if __addon__.getSetting("useSeasons") == "false":
        # this will help when users is using grouping option in jmm which results in node in node
        if "data/1/2/" in extra_data['key'].lower():
            use_mode = 4
    u = sys.argv[0]
    u = set_parameter(u, 'url', url)
    u = set_parameter(u, 'mode', str(use_mode))
    #if filterid != '':
    #    u = set_parameter(u, 'filterid', filterid)
    #else:
    u = set_parameter(u, 'filterid', None)

    context = None
    add_gui_item(u, details, extra_data, context)


def add_group_item(node, parent_title):
    # xbmcgui.Dialog().ok('group','group')
    temp_genre = get_tags(node["tags"])
    title = node["name"]
    size = node["size"]
    type = node["type"]
    details = {
        'title':            title,
        'parenttitle':      encode(parent_title),
        'genre':            temp_genre,
        'year':             safeInt(node["year"]),
        'episode':          size,
        'season':           safeInt(node["season"]),
        'size':             size,
        'rating':           float(str(node["rating"]).replace(',', '.')),
        'playcount':        int(node["viewed"]),
        'plot':             remove_anidb_links(encode(node["summary"])),
        'originaltitle':    title,
        'sorttitle':        title,
        'tvshowname':       title,
        'dateadded':        node["added"]
    }

    key_id = str(node["id"])
    key = _server_ + "/api/group?id=" + key_id

    thumb = ''
    if len(node["art"]["thumb"]) > 0:
        thumb = node["art"]["thumb"][0]["url"]
    fanart = ''
    if len(node["art"]["fanart"]) > 0:
        fanart = node["art"]["fanart"][0]["url"]
    banner = ''
    if len(node["art"]["banner"]) > 0:
        banner = node["art"]["banner"][0]["url"]

    extra_data = {
        'type':                 'video',
        'source':               type,
        'thumb':                thumb,
        'fanart_image':         fanart,
        'banner':               banner,
        'key':                  key
    }

    if __addon__.getSetting('request_nocast') == 'true':
        key += '&nocast=1'

    url = key
    set_watch_flag(extra_data, details)
    use_mode = 5
    # TODO: re-check logic as data/1/2 is no longer
    if __addon__.getSetting("useSeasons") == "false":
        # this will help when users is using grouping option in jmm which results in node in node
        if "data/1/2/" in extra_data['key'].lower():
            use_mode = 4
    u = sys.argv[0]
    u = set_parameter(u, 'url', url)
    u = set_parameter(u, 'mode', str(use_mode))
    #if filterid != '':
    #    u = set_parameter(u, 'filterid', filterid)
    #else:
    u = set_parameter(u, 'filterid', None)

    context = None
    add_gui_item(u, details, extra_data, context)


# TODO filterid is missing as I don't get it
def build_filters_menu():
    """
    Builds the list of items (filters) in the Main Menu
    """
    xbmcplugin.setContent(handle, content='tvshows')
    try:
        json_menu = json.loads(get_json(_server_ + "/api/filter"))
        set_window_heading("main")
        try:
            for menu in json_menu:
                title = menu["name"]
                use_mode = 4
                key = menu["url"]
                size = safeInt(menu["size"])

                if title == 'Continue Watching (SYSTEM)':
                    title = 'Continue Watching'
                elif title == 'Unsort':
                    title = 'Unsorted'
                    use_mode = 6

                if __addon__.getSetting("spamLog") == "true":
                    xbmc.log("build_filters_menu - key = " + key)

                if __addon__.getSetting('request_nocast') == 'true' and title != 'Unsorted':
                    key += '&nocast=1'
                url = key

                thumb = ''
                if len(menu["art"]["thumb"]) > 0:
                    thumb = menu["art"]["thumb"][0]["url"]
                fanart = ''
                if len(menu["art"]["fanart"]) > 0:
                    fanart = menu["art"]["fanart"][0]["url"]
                banner = ''
                if len(menu["art"]["banner"]) > 0:
                    banner = menu["art"]["banner"][0]["url"]

                u = sys.argv[0]
                u = set_parameter(u, 'url', url)
                u = set_parameter(u, 'mode', str(use_mode))
                u = set_parameter(u, 'name', urllib.quote_plus(title))
                # u = set_parameter(u, 'filterid', menu["id"]) <-----

                liz = xbmcgui.ListItem(label=title, label2=title, path=url)
                liz.setArt({'thumb': thumb, 'fanart': fanart, 'poster': thumb, 'banner': banner, 'clearart': fanart})
                liz.setIconImage('DefaultVideo.png')
                liz.setInfo(type="Video", infoLabels={"Title": title, "Plot": title, "count": size})
                xbmcplugin.addDirectoryItem(handle, url=u, listitem=liz, isFolder=True)
        except Exception as e:
            error("Error during build_filters_menu", str(e))
    except Exception as e:
        error("Invalid JSON Received in build_filters_menu", str(e))

    # Start Add_Search
    url = _server_ + "/serie/search?limit=" + __addon__.getSetting("maxlimit")
    title = "Search"
    thumb = _server_ + "/image/support/plex_others.png"
    liz = xbmcgui.ListItem(label=title, label2=title, path=url)
    liz.setArt({'thumb': thumb, 'poster': thumb})
    liz.setIconImage('DefaultVideo.png')
    liz.setInfo(type="Video", infoLabels={"Title": title, "Plot": title})
    u = sys.argv[0]
    u = set_parameter(u, 'url', url)
    u = set_parameter(u, 'mode', str(3))
    u = set_parameter(u, 'name', urllib.quote_plus(title))
    xbmcplugin.addDirectoryItem(handle, url=u, listitem=liz, isFolder=True)
    # End Add_Search

    xbmcplugin.endOfDirectory(handle, True, False, False)


# TODO filterid is missing as I don't get it and group (shoko) option have bad logic now
def build_groups_menu(params, extra_directories=None):
    """
    Builds the list of items for Filters and Groups
    Args:
        params:
        extra_directories:

    Returns:

    """
    # xbmcgui.Dialog().ok('MODE=4', 'IN')
    xbmcplugin.setContent(handle, 'tvshows')
    if __addon__.getSetting('use_server_sort') == 'false' and extra_directories is None:
        xbmcplugin.addSortMethod(handle, 27)  # video title ignore THE
        xbmcplugin.addSortMethod(handle, 3)  # date
        xbmcplugin.addSortMethod(handle, 18)  # rating
        xbmcplugin.addSortMethod(handle, 17)  # year
        xbmcplugin.addSortMethod(handle, 28)  # by MPAA

    try:
        # level 3 will fill group and series
        html = get_json(params['url'] + "&level=3")
        if __addon__.getSetting("spamLog") == "true":
            xbmc.log(params['url'])
            xbmc.log(html)
        body = json.loads(html)
        set_window_heading(body["name"])
        try:
            # TODO: Do we really use parent ?
            parent_title = body["name"]

            # converting series from search to group so we can handle them here
            if "groups" not in body:
                new_serie = dict()
                series_list = []
                for ser in body:
                    series_list.append(ser)
                new_serie["series"] = series_list
                new_group = []
                new_group.append(new_serie)
                new_body = dict()
                new_body["groups"] = new_group
                body = new_body

            if len(body["groups"]) <= 0:
                build_serie_episodes(params)
                return

            for grp in body["groups"]:
                if len(grp["series"]) > 0:
                    if len(grp["series"]) == 1:
                        add_serie_item(grp["series"][0], parent_title)
                    else:
                        add_group_item(grp, parent_title)

        except Exception as e:
            error("Error during build_groups_menu", str(e))
    except Exception as e:
        error("Invalid XML Received in build_groups_menu", str(e))
    xbmcplugin.endOfDirectory(handle)


# TODO continue here...... <---------------------------------------------------
# json - still broken - hacked - added dirs
def build_serie_episodes_types(params, extra_directories=None):
    """
    Builds list items for The Types Menu, or optionally subgroups
    Args:
        params:
        extra_directories:

    Returns:

    """
    # xbmcgui.Dialog().ok('MODE=5', str(params['url']))
    xbmcplugin.setContent(handle, 'seasons')
    try:
        html = get_json(params['url'])
        if __addon__.getSetting("spamLog") == "true":
            xbmc.log(html)
        body = json.loads(html)
        try:
            parent_title = ''
            try:
                parent_title = body["title"]
            except Exception as exc:
                error("Unable to get parent title in buildTVSeasons", str(exc))

            # if extra_directories is not None: <---
            #     e.extend(extra_directories) <---
            # if e.find('Directory') is None:
#                params['url'] = params['url'].replace('&mode=5', '&mode=6')
#                build_serie_episodes(params)
#                return
            content_dict = dict()
            if "eps" in body:
                if len(body["eps"]) >= 1:
                    for ep in body["eps"]:
                        if ep["eptype"] not in content_dict:
                            # episode
                            content_dict[str(ep["eptype"])] = ep["type"]
            if '1' in content_dict.keys() and len(content_dict) == 1:
                build_serie_episodes(params)
                return
            else:
                for content in content_dict.keys():
                    add_content_typ_dir(content_dict[content], body["id"], content)

                xbmcplugin.endOfDirectory(handle)
                return

            # it wont go below as it return in both cases
            e = ''
            set_window_heading(e)
            will_flatten = False

            # check for a single season
            if int(e.get('size', 0)) == 1:
                will_flatten = True

            #section_art = gen_image_url(e.get('art', ''))

            #set_window_heading(e)

            for atype in e.findall('Directory'):
                key = atype.get('key', '')

                if will_flatten:
                    new_params = {'url': key, 'mode': 6}
                    build_serie_episodes(new_params)
                    return

                plot = remove_anidb_links(encode(atype.get('summary', '')))

                temp_genre = get_tags(atype)
                watched = int(atype.get('viewedLeafCount', 0))

                list_cast = []
                list_cast_and_role = []
                actors = []
                if len(list_cast) == 0:
                    result_list = get_cast_and_role(atype)
                    actors = result_list
                    if result_list is not None:
                        result_list = convert_cast_and_role_to_legacy(result_list)
                        list_cast = result_list[0]
                        list_cast_and_role = result_list[1]

                # Create the basic data structures to pass up
                if __addon__.getSetting("local_total") == "true":
                    total = int(atype.get('totalLocal', 0))
                else:
                    total = int(atype.get('leafCount', 0))
                title = get_title(atype)
                details = {
                    'title':        title,
                    'parenttitle':  encode(parent_title),
                    'tvshowname':   title,
                    'sorttitle':    encode(atype.get('titleSort', title)),
                    'studio':       encode(atype.get('studio', '')),
                    'cast':         list_cast,
                    'castandrole':  list_cast_and_role,
                    'plot':         plot,
                    'genre':        temp_genre,
                    'season':       int(atype.get('season', 1)),
                    'episode':      total,
                    'mpaa':         atype.get('contentRating', ''),
                    'rating':       float(str(atype.get('rating', 0.0)).replace(',', '.')),
                    'userrating':       float(str(atype.get('UserRating', 0.0)).replace(',', '.')) if "UserRating" in atype else 0,
                    'aired':        atype.get('originallyAvailableAt', ''),
                    'year':         int(atype.get('year', 0))
                }
                temp_date = str(details['aired']).split('-')
                if len(temp_date) == 3:  # format is 2016-01-24, we want it 24.01.2016
                    details['date'] = temp_date[1] + '.' + temp_date[2] + '.' + temp_date[0]

                if atype.get('sorttitle'):
                    details['sorttitle'] = atype.get('sorttitle')

                thumb = atype.get('thumb')
                fanart = atype.get('art', thumb)
                banner = atype.get('banner', e.get('banner', ''))

                directory_type = atype.get('AnimeType', '')

                filterid = ''
                if get_version() > LooseVersion(
                        '3.6.1.0') and directory_type != 'AnimeType' and directory_type != 'AnimeSerie':
                    if params.get('filterid', '') != '':
                        filterid = params.get('filterid', '')
                        if directory_type == 'AnimeGroupFilter':
                            filterid = atype.get('GenericId', '')
                        length = len(_server_
                                     + "jmmserverkodi/getmetadata/" + __addon__.getSetting("userid") + "/") + 1
                        key = key[length:]
                        key = _server_ \
                              + "/api/metadata/" + key + '/' + filterid

                extra_data = {
                    'type':                 'video',
                    'source':               directory_type,
                    'TotalEpisodes':        details['episode'],
                    'WatchedEpisodes':      watched,
                    'UnWatchedEpisodes':    details['episode'] - watched,
                    'thumb':                thumb,
                    'fanart_image':         fanart,
                    'banner':               banner,
                    'key':                  key,
                    'mode':                 str(6),
                    'actors':               actors
                }

                if extra_data['fanart_image'] == "":
                    extra_data['fanart_image'] = section_art

                set_watch_flag(extra_data, details)

                key_append = ''
                if __addon__.getSetting('request_nocast') == 'true':
                    key_append = '/nocast'

                url = sys.argv[0]
                url = set_parameter(url, 'url', extra_data['key'] + key_append)
                url = set_parameter(url, 'mode', str(6))
                if filterid != '':
                    url = set_parameter(url, 'filterid', filterid)
                else:
                    url = set_parameter(url, 'filterid', None)

                context = None

                # Build the screen directory listing
                add_gui_item(url, details, extra_data, context)

            if __addon__.getSetting('use_server_sort') == 'false' and extra_directories is None:
                # Apparently date sorting in Kodi has been broken for years
                xbmcplugin.addSortMethod(handle, 17)  # year
                xbmcplugin.addSortMethod(handle, 27)  # video title ignore THE
                xbmcplugin.addSortMethod(handle, 3)  # date
                xbmcplugin.addSortMethod(handle, 18)  # rating
                xbmcplugin.addSortMethod(handle, 28)  # by MPAA

        except Exception as exc:
            error("Error during build_serie_episodes_types", str(exc))
    except Exception as exc:
        error("Invalid XML Received in build_serie_episodes_types", str(exc))
    xbmcplugin.endOfDirectory(handle)


# json - a lot comment out
def build_serie_episodes(params):
    # xbmcgui.Dialog().ok('MODE=6','IN')
    """

    :param params:
    :return:
    """
    xbmcplugin.setContent(handle, 'episodes')
    try:
        # dbg("build_episode:" + params['url'])
        html = get_json(params['url'])
        body = json.loads(html)
        if __addon__.getSetting("spamLog") == "true":
            xbmc.log(html)
        # set_window_heading(e) <-----
        try:
            parent_title = ''
            try:
                parent_title = body["title"]
            except Exception as exc:
                error("Unable to get parent title in buildTVEpisodes", str(exc))

            # DETECT PERSONA 4 THE ANIMATION TYPES OF EPISODES (before it was credit/ovas) not they are in eps
            # if e.find('Directory') is not None:  <-----
            #    params['url'] = params['url'].replace('&mode=6', '&mode=5')
            #    build_serie_episodes_types(params)
            #    return

            art = ''
            if len(body["art"]["fanart"]) > 0:
                art = body["art"]["fanart"][0]["url"]
            thumb = ''
            if len(body["art"]["thumb"]) > 0:
                thumb = body["art"]["thumb"][0]["url"]
            banner = ''
            if len(body["art"]["banner"]) > 0:
                banner = body["art"]["banner"][0]["url"]

            if __addon__.getSetting('use_server_sort') == 'false':
                # Set Sort Method
                xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_EPISODE)  # episode
                xbmcplugin.addSortMethod(handle, 3)  # date
                xbmcplugin.addSortMethod(handle, 25)  # video title ignore THE
                xbmcplugin.addSortMethod(handle, 19)  # date added
                xbmcplugin.addSortMethod(handle, 18)  # rating
                xbmcplugin.addSortMethod(handle, 17)  # year
                xbmcplugin.addSortMethod(handle, 29)  # runtime
                xbmcplugin.addSortMethod(handle, 28)  # by MPAA

            # value to hold position of not seen episode
            next_episode = -1
            episode_count = 0

            if len(body["eps"]) <= 0:
                error("No episodes in list")
            skip = __addon__.getSetting("skipExtraInfoOnLongSeries") == "true" and len(body["eps"]) > int(
                __addon__.getSetting("skipExtraInfoMaxEpisodes"))

            # keep this init out of the loop, as we only provide this once
            list_cast = []
            list_cast_and_role = []
            actors = []
            temp_genre = ""
            parent_key = ""
            grandparent_title = ""
            if not skip:
                result_list = get_cast_and_role(body["roles"])
                if result_list is not None:
                    actors = result_list
                    result_list = convert_cast_and_role_to_legacy(result_list)
                    list_cast = result_list[0]
                    list_cast_and_role = result_list[1]

                temp_genre = get_tags(body["tags"])
                parent_key = body["id"]
                grandparent_title = encode(body["title"])

            if len(body["eps"]) > 0:
                for video in body["eps"]:
                    # check if episode have files
                    episode_type = True
                    if "type" in params:
                        # dbg("param_type:" + str(params["type"]) + " video[eptype]:" + str(video["eptype"]))
                        episode_type = True if str(video["eptype"]) == str(params["type"]) else False
                    if video["files"] is not None and episode_type:
                        if len(video["files"]) > 0:
                            episode_count += 1
                            # view_offset = video.get('viewOffset', 0) <---
                            # Check for empty duration from MediaInfo check fail and handle it properly
                            try:
                                tmp_duration = video["files"][0]["duration"]
                            except:
                                continue
                            if not tmp_duration:
                                duration = 1
                            else:
                                duration = int(tmp_duration) / 1000
                            # Required listItem entries for XBMC
                            details = {
                                'plot':          "..." if skip else remove_anidb_links(encode(video["summary"])),
                                'title':         encode(video["title"]),
                                'sorttitle':     encode(video["title"]),
                                'parenttitle':   encode(parent_title),
                                'rating':        float(str(video["rating"]).replace(',', '.')),
                                'userrating':        float(str(video["UserRating"]).replace(',', '.')) if "UserRating" in video else 0,
                                # 'studio'      : episode.get('studio',tree.get('studio','')), 'utf-8') ,
                                # This doesn't work, some gremlins be afoot in this code...
                                # it's probably just that it only applies at series level
                                # 'cast'        : list(['Actor1','Actor2']),
                                # 'castandrole' : list([('Actor1','Character1'),('Actor2','Character2')]),
                                # According to the docs, this will auto fill castandrole
                                'CastAndRole':   list_cast_and_role,
                                'Cast':          list_cast,
                                # 'director': " / ".join(temp_dir),
                                # 'writer': " / ".join(temp_writer),
                                'genre':        "..." if skip else temp_genre,
                                'duration':      str(datetime.timedelta(seconds=duration)),
                                # 'mpaa':          video.get('contentRating', ''), <--
                                'year':          safeInt(video["year"]),
                                'tagline':       "..." if skip else temp_genre,
                                'episode':       safeInt(video["epnumber"]),
                                'aired':         video["air"],
                                'tvshowtitle':   grandparent_title,
                                'votes':         safeInt(video["votes"]),
                                # 'originaltitle': video.get('original_title', ''), <---
                                'size': safeInt(body["size"])
                            }

                            season = str(body["season"])
                            try:
                                if season != '1':
                                    season = season.split('x')[0]
                            except Exception as w:
                                error(w, season)
                            details['season'] = safeInt(season)

                            temp_date = str(details['aired']).split('-')
                            if len(temp_date) == 3:  # format is 2016-01-24, we want it 24.01.2016
                                details['date'] = temp_date[1] + '.' + temp_date[2] + '.' + temp_date[0]

                            thumb = ''
                            if len(video["art"]["thumb"]) > 0:
                                thumb = video["art"]["thumb"][0]["url"]
                            fanart = ''
                            if len(video["art"]["fanart"]) > 0:
                                fanart = video["art"]["fanart"][0]["url"]
                            banner = ''
                            if len(video["art"]["banner"]) > 0:
                                banner = video["art"]["banner"][0]["url"]

                            # we could leave this as is and when trigger get essential data for this episode/file only
                            key = video["files"][0]["url"]
                            #if key is not None:
                            #    dbg("key:" + key)
                            #else:
                            #    dbg("key is None")

                            # <--- V V V
                            # ext = video.find('Media').find('Part').get('container', '')
                            # new_key = video.find('Media').find('Part').get('key', '')

                            # if not key.lower().startswith("http") or 'videolocal' not in key.lower():
                            #    key = new_key
                            #    if not key.startswith("http") and 'videolocal' not in key.lower():
                            #        key = "http://" + __addon__.getSetting("ipaddress") + ":" + \
                            #              str(int(__addon__.getSetting("port")) + 1) + "/videolocal/0/" + key
                            #    if '.' + ext.lower() not in key.lower():
                            #        key += '.' + ext.lower()

                            # newerkey = encode(video.find('Media').find('Part').get('local_key', ''))
                            # newerkey = newerkey.replace('\\', '\\\\')
                            # if newerkey != '' and os.path.isfile(newerkey):
                            #    key = newerkey

                            # Extra data required to manage other properties
                            extra_data = {
                                'type':             "Video",
                                'source':           "tvepisodes",
                                # 'unsorted':         'animefile' in video.get('AnimeType', '').lower(), <---
                                'thumb':            None if skip else thumb,
                                'fanart_image':     None if skip else art,
                                'key':              key,
                                # 'resume':           int(int(view_offset) / 1000),<---
                                'parentKey':        parent_key,
                                'jmmepisodeid':     safeInt(body["id"]),
                                'banner':           banner,
                                # 'xVideoResolution': video["files"][0]["media"]["videos"]["1"]["Width"], <---
                                # 'xVideoCodec':      video["files"][0]["media"]["videos"]["1"]["Codec"], <---
                                # 'xVideoAspect':     float(video.find('Media').get('aspectRatio', 0)), <---
                                # 'xAudioCodec':      video["files"][0]["media"]["audios"]["1"]["Codec"], <---
                                # 'xAudioChannels':   safeInt(video["files"][0]["media"]["audios"]["1"]["Channels"]), <---
                                'actors':           actors,
                                'AudioStreams':     defaultdict(dict),
                                'SubStreams':       defaultdict(dict)
                                }

                            # Information about streams inside video file
                            if video["files"][0]["media"] is not None:
                                if len(video["files"][0]["media"]) > 0:
                                    for stream_info in video["files"][0]["media"]["videos"]:
                                        # Video
                                        extra_data['VideoCodec'] = video["files"][0]["media"]["videos"][stream_info]['Codec']
                                        extra_data['width'] = int(video["files"][0]["media"]["videos"][stream_info]["Width"])
                                        extra_data['height'] = int(video["files"][0]["media"]["videos"][stream_info]["Height"])
                                        #extra_data['duration'] = int(video["files"][0]["media"]["videos"][stream_info]["Duration"]) if "Duration" in video["files"][0]["media"]["videos"][stream_info] else 1

                                    for stream_info in video["files"][0]["media"]["audios"]:
                                        # Audio
                                        streams = extra_data.get('AudioStreams')
                                        streamid = int(video["files"][0]["media"]["audios"][stream_info]["Index"])
                                        streams[streamid]['AudioCodec'] = video["files"][0]["media"]["audios"][stream_info]["Codec"]
                                        streams[streamid]['AudioLanguage'] = video["files"][0]["media"]["audios"][stream_info]["LanguageCode"]
                                        streams[streamid]['AudioChannels'] = int(video["files"][0]["media"]["audios"][stream_info]["Channels"])
                                        extra_data['AudioStreams'] = streams

                                    for stream_info in video["files"][0]["media"]["subtitles"]:
                                        # Subtitle
                                        streams = extra_data.get('SubStreams')
                                        streamid = int(video["files"][0]["media"]["subtitles"][stream_info]["Index"])
                                        streams[streamid]['SubtitleLanguage'] = video["files"][0]["media"]["subtitles"][stream_info]["LanguageCode"] if "LanguageCode" in video["files"][0]["media"]["subtitles"][stream_info] else "unk"
                                        extra_data['SubStreams'] = streams

                            # Determine what type of watched flag [overlay] to use
                            if int(safeInt(video["view"])) > 0:
                                details['playcount'] = 1
                                # details['overlay'] = 5
                            else:
                                details['playcount'] = 0
                                # details['overlay'] = 0
                                if next_episode == -1:
                                    next_episode = episode_count - 1

                            if details['playcount'] == 0:
                                # Hide plot and thumb for unwatched by kodi setting
                                if not get_kodi_setting_bool("videolibrary.showunwatchedplots"):
                                    details['plot'] \
                                        = "Hidden due to user setting.\nCheck Show Plot" + \
                                          " for Unwatched Items in the Video Library Settings."
                                    extra_data['thumb'] = thumb
                                    extra_data['fanart_image'] = fanart

                            context = None
                            url = key

                            u = sys.argv[0]
                            u = set_parameter(u, 'url', url)
                            u = set_parameter(u, 'mode', '1')
                            u = set_parameter(u, 'file', key)
                            u = set_parameter(u, 'ep_id', str(video["id"]))
                            u = set_parameter(u, 'ui_index', str(int(episode_count - 1)))

                            add_gui_item(u, details, extra_data, context, folder=False, index=int(episode_count - 1))

            # add item to move to next not played item (not marked as watched)
            if __addon__.getSetting("show_continue") == "true":
                if str(parent_title).lower() != "unsort":
                    util.addDir("-continue-", '', '7', "http://" + __addon__.getSetting("ipaddress") + ":"
                                + __addon__.getSetting("port") + "/jmmserverkodi/GetSupportImage/plex_others.png",
                                "2", "3", "4", str(next_episode))

            if get_kodi_setting_int('videolibrary.tvshowsselectfirstunwatcheditem') > 0:
                try:
                    new_window = xbmcgui.Window(xbmcgui.getCurrentWindowId())
                    new_control = new_window.getControl(new_window.getFocusId())
                    move_position_on_list(new_control, next_episode)
                except:
                    pass

        except Exception as exc:
            error("Error during build_serie_episodes", str(exc))
    except Exception as exc:
        error("Invalid XML Received in build_serie_episodes", str(exc))
    xbmcplugin.endOfDirectory(handle)


# json - ok + one minnor clean need ? or not
def build_search(url=''):
    """
    Build directory list of series containing searched query
    Args:
        url: url pointing to search api

    Returns: build_groups_menu out of search query

    """
    try:
        term = util.searchBox()
        if term is not None and term != "":
            try:
                term = term.replace(' ', '%20').replace("'", '%27').replace('?', '%3F')

                if '/tag/' in url:
                    url2 = _server_ \
                         + "/api/serie/tag?limit=" + __addon__.getSetting("maxlimit_tag") + "&query="
                else:
                    url2 = _server_ \
                           + "/api/serie/search?limit=" + __addon__.getSetting("maxlimit") + "&query="
                to_send = {'url': url2 + term}
                search_body = json.loads(get_json(url2 + term))

                # is this needed ?
                directories = None
                if len(search_body) <= 0:
                    directories = None

                build_groups_menu(to_send, directories)
            except Exception as exc:
                error("Error during build_search", str(exc))
    except Exception as exc:
        error("Error during searchBox", str(exc))


# Other functions
# json
def play_video(url, ep_id):
    """
    Plays a file or episode
    Args:
        url: location of the file
        ep_id: episode id, if applicable for watched status and stream details

    Returns:

    """
    details = {
        'plot':          xbmc.getInfoLabel('ListItem.Plot'),
        'title':         xbmc.getInfoLabel('ListItem.Title'),
        'sorttitle':     xbmc.getInfoLabel('ListItem.Title'),
        'rating':        xbmc.getInfoLabel('ListItem.Rating'),
        'duration':      xbmc.getInfoLabel('ListItem.Duration'),
        'mpaa':          xbmc.getInfoLabel('ListItem.Mpaa'),
        'year':          xbmc.getInfoLabel('ListItem.Year'),
        'tagline':       xbmc.getInfoLabel('ListItem.Tagline'),
        'episode':       xbmc.getInfoLabel('ListItem.Episode'),
        'aired':         xbmc.getInfoLabel('ListItem.Premiered'),
        'tvshowtitle':   xbmc.getInfoLabel('ListItem.TVShowTitle'),
        'votes':         xbmc.getInfoLabel('ListItem.Votes'),
        'originaltitle': xbmc.getInfoLabel('ListItem.OriginalTitle'),
        'size':          xbmc.getInfoLabel('ListItem.Size'),
        'season':        xbmc.getInfoLabel('ListItem.Season')
    }

    item = xbmcgui.ListItem(details.get('title', 'Unknown'), thumbnailImage=xbmc.getInfoLabel('ListItem.Thumb'),
                            path=url)
    item.setInfo(type='Video', infoLabels=details)
    item.setProperty('IsPlayable', 'true')
    try:
        episode_url = _server_ + \
                          "/api/ep?id=" + str(ep_id)
        # dbg(episode_url)
        html = get_json(encode(episode_url))
        if __addon__.getSetting("spamLog") == "true":
            xbmc.log(html)
        episode_body = json.loads(html)
        # extract extra data about file from episode
        file_id = episode_body["files"][0]["id"]
        if file_id is not None and file_id != 0:
            file_url = _server_ + \
                          "/api/file?id=" + str(file_id)
            file_body = json.loads(get_json(file_url))
            
            # Information about streams inside video file
            # Video
            video_codec = dict()
            video_codec['codec'] = file_body["media"]["videos"]["1"]["Codec"]
            video_codec['width'] = int(file_body["media"]["videos"]["1"]["Width"])
            video_codec['height'] = int(file_body["media"]["videos"]["1"]["Height"])
            video_codec['duration'] = int(file_body["duration"])
            item.addStreamInfo('video', video_codec)

            # Audio
            audio_codec = dict()
            audio_codec['codec'] = file_body["media"]["audios"]["1"]["Codec"]
            audio_codec['language'] = file_body["media"]["audios"]["1"]["LanguageCode"]
            audio_codec['channels'] = int(file_body["media"]["audios"]["1"]["Channels"])
            item.addStreamInfo('audio', audio_codec)

            # Subtitle
            subtitle_codec = dict()
            subtitle_codec['language'] = file_body["media"]["subtitles"]["1"]["LanguageCode"]
            item.addStreamInfo('subtitle', subtitle_codec)
        else:
            # error
            error("Unknown Stream Type Received!")
    except Exception as exc:
        error('Error getting episode info', str(exc))

    player = xbmc.Player()

    try:
        player.play(item=url, listitem=item, windowed=False)
        xbmcplugin.setResolvedUrl(handle, True, item)
    except:
        pass
    # wait for player (network issue etc)
    xbmc.sleep(1000)
    mark = float(__addon__.getSetting("watched_mark"))
    mark /= 100
    file_fin = False
    # hack for slow connection and buffering time
    xbmc.sleep(int(__addon__.getSetting("player_sleep")))
    try:
        while player.isPlaying():
            try:
                xbmc.sleep(500)
                total_time = player.getTotalTime()
                current_time = player.getTime()
                if (total_time * mark) < current_time:
                    file_fin = True
                if not player.isPlaying():
                    break
            except:
                xbmc.sleep(500)
                break
    except:
        pass

    no_watch_status = False
    if __addon__.getSetting('no_mark') != "0":
        no_watch_status = True
        # reset no_mark so next file will mark watched status
        __addon__.setSetting('no_mark', '0')

    if file_fin is True:
        if no_watch_status is False:
            return ep_id
    return 0


# json
def play_continue_item():
    """
    Move to next item that was not marked as watched
    Essential information are query from Parameters via util lib
    """
    params = util.parseParameters()
    if 'offset' in params:
        offset = params['offset']
        pos = int(offset)
        if pos == 1:
            xbmcgui.Dialog().ok('Finished', 'You already finished this')
        else:
            wind = xbmcgui.Window(xbmcgui.getCurrentWindowId())
            control_id = wind.getFocusId()
            control_list = wind.getControl(control_id)
            move_position_on_list(control_list, pos)
            xbmc.sleep(1000)
    else:
        pass


# TODO: Trakt_Scrobble need work - JMM support it (for series not movies)
def trakt_scrobble(data=""):
    """

    Args:
        data:
    """
    xbmcgui.Dialog().ok('WIP', str(data))


# json
def vote_series(params):
    """
    Marks a rating for a series
    Args:
        params: must contain anime_id

    """
    vote_list = ['Don\'t Vote', '10', '9', '8', '7', '6', '5', '4', '3', '2', '1', '0']
    my_vote = xbmcgui.Dialog().select('my_vote', vote_list)
    if my_vote == -1:
        return
    elif my_vote != 0:
        vote_value = str(vote_list[my_vote])
        # vote_type = str(1)
        series_id = params['anime_id']
        body = '"id":"'+series_id+'","score":"'+vote_value+'"'
        post_json(_server_
                  + "/serie/vote", body)
        xbmc.executebuiltin("XBMC.Notification(%s, %s %s, 7500, %s)" % (
            'Vote saved', 'You voted', vote_value, __addon__.getAddonInfo('icon')))


# json
def vote_episode(params):
    """
    Marks a rating for an episode
    Args:
        params: must contain ep_id

    """
    vote_list = ['Don\'t Vote', '10', '9', '8', '7', '6', '5', '4', '3', '2', '1', '0']
    my_vote = xbmcgui.Dialog().select('My Vote', vote_list)
    if my_vote == -1:
        return
    elif my_vote != 0:
        vote_value = str(vote_list[my_vote])
        # vote_type = str(4)
        ep_id = params['ep_id']
        body = '"id":"'+ep_id+'","score":"'+vote_value+'"'
        post_json(_server_
                  + "/ep/vote", body)
        xbmc.executebuiltin("XBMC.Notification(%s, %s %s, 7500, %s)" % (
            'Vote saved', 'You voted', vote_value, __addon__.getAddonInfo('icon')))


# json + 1 legacy unimplemented
def watched_mark(params):
    """
    Marks an epsiode, series, or group as either watched or unwatched
    Args:
        params: must contain either an episode, series, or group id, and a watched value to mark
    """
    episode_id = params.get('ep_id', '')
    anime_id = params.get('anime_id', '')
    group_id = params.get('group_id', '')
    watched = bool(params['watched'])
    key = _server_
    if watched is True:
        watched_msg = "watched"
        if episode_id != '':
            key += "/ep/watch"
        elif anime_id != '':
            key += "/serie/watch"
        elif group_id != '':
            key = _server_ \
                + "/jmmserverkodi/watchgroup/" + __addon__.getSetting("userid") + "/" + group_id + "/" + str(
                watched).strip()
    else:
        watched_msg = "unwatched"
        if episode_id != '':
            key += "/ep/unwatch"
        elif anime_id != '':
            key += "/serie/unwatch"
        elif group_id != '':
            key = _server_ \
                  + "/jmmserverkodi/watchgroup/" + __addon__.getSetting("userid") + "/" + group_id + "/" + str(
                watched).strip()

    if __addon__.getSetting('log_spam') == 'true':
        xbmc.log('epid: ' + str(episode_id))
        xbmc.log('anime_id: ' + str(anime_id))
        xbmc.log('group_id: ' + str(group_id))
        xbmc.log('key: ' + key)

    # sync mark flags
    sync = __addon__.getSetting("syncwatched")
    if sync == "true":
        if episode_id != '':
            body = '"id":"' + episode_id + '"'
            post_json(key, body)
        elif anime_id != '':
            body = '"id":"' + anime_id + '"'
            post_json(key, body)
        elif group_id != '':
            get_xml(key)

    box = __addon__.getSetting("watchedbox")
    if box == "true":
        xbmc.executebuiltin("XBMC.Notification(%s, %s %s, 2000, %s)" % (
            'Watched status changed', 'Mark as ', watched_msg, __addon__.getAddonInfo('icon')))
    refresh()


# legacy unimplemented
def rescan_file(params, rescan):
    """
    Rescans or rehashes a file
    Args:
        params:
        rescan: True to rescan, False to rehash
    """
    episode_id = params.get('ep_id', '')
    command = 'rehash/'
    if rescan:
        command = 'rescan/'

    key = ""
    if episode_id != '':
        key = _server_ \
              + "/jmmserverkodi/" + command + episode_id
    if __addon__.getSetting('log_spam') == 'true':
        xbmc.log('vlid: ' + str(episode_id))
        xbmc.log('key: ' + key)

    get_xml(key)

    xbmc.executebuiltin("XBMC.Notification(%s, %s, 2000, %s)" % (
        'Queued file for ' + ('Rescan' if rescan else 'Rehash'), 'Refreshing in 10 seconds',
        __addon__.getAddonInfo('icon')))
    xbmc.sleep(10000)
    refresh()


# Setting up Remote Debug
if __addon__.getSetting('remote_debug') == 'true':
    try:
        if pydevd:
            pydevd.settrace(__addon__.getSetting('ide_ip'), port=int(__addon__.getSetting('ide_port')),
                            stdoutToServer=False, stderrToServer=False, suspend=False)
        else:
            error('Unable to start debugger')
    except Exception as ex:
        error('pydevd not found, disabling remote_debug', str(ex))
        __addon__.setSetting('remote_debug', 'false')

# Script run from here
if valid_user() is True:
    try:
        # xbmc.log('before', str(sys.argv[2]))
        parameters = util.parseParameters()
        # xbmc.log('after', str(parameters))
    except Exception as exp:
        error('valid_userid parseParameters() error', str(exp))
        parameters = {'mode': 2}
    if parameters:
        try:
            mode = int(parameters['mode'])
        except Exception as exp:
            error('valid_userid set \'mode\' error', str(exp) + " parameters: " + str(parameters))
            mode = None
    else:
        mode = None
    try:
        if 'cmd' in parameters:
            cmd = parameters['cmd']
        else:
            cmd = None
    except:
        cmd = None
    # xbmcgui.Dialog().ok("CMD", cmd)
    # xbmcgui.Dialog().ok("PARAMETERS", str(parameters))
    if cmd is not None:
        if cmd == "voteSer":
            vote_series(parameters)
        elif cmd == "voteEp":
            vote_episode(parameters)
        elif cmd == "watched":
            if get_kodi_setting_int('videolibrary.tvshowsselectfirstunwatcheditem') == 0:
                try:
                    win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
                    ctl = win.getControl(win.getFocusId())
                    # noinspection PyTypeChecker
                    ui_index = parameters.get('ui_index', '')
                    if ui_index != '':
                        move_position_on_list(ctl, int(ui_index) + 1)
                except Exception as exp:
                    xbmc.log(str(exp))
                    pass
            parameters['watched'] = True
            watched_mark(parameters)
            voting = __addon__.getSetting("vote_always")
            if voting == "true":
                vote_episode(parameters)
        elif cmd == "unwatched":
            parameters['watched'] = False
            watched_mark(parameters)
        elif cmd == "playlist":
            play_continue_item()
        elif cmd == "no_mark":
            __addon__.setSetting('no_mark', '1')
            xbmc.executebuiltin('Action(Select)')
        elif cmd == 'rescan':
            rescan_file(parameters, True)
        elif cmd == 'rehash':
            rescan_file(parameters, False)
    else:
        # xbmcgui.Dialog().ok('MODE=' + str(mode), str(parameters))
        if mode == 1:  # VIDEO
            # xbmcgui.Dialog().ok('MODE=1','MODE')
            try:
                win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
                ctl = win.getControl(win.getFocusId())
                # dbg("file:" + parameters['file'])
                if play_video(parameters['file'], parameters['ep_id']) != 0:
                    # noinspection PyTypeChecker
                    ui_index = parameters.get('ui_index', '')
                    if ui_index != '':
                        move_position_on_list(ctl, int(ui_index) + 1)
                    parameters['watched'] = True
                    watched_mark(parameters)
                    if __addon__.getSetting('vote_always') == 'true':
                        vote_episode(parameters)
            except Exception as exp:
                xbmc.log(str(exp))
                pass
        elif mode == 2:  # DIRECTORY
            xbmcgui.Dialog().ok('MODE=2', 'MODE')
        elif mode == 3:  # SEARCH
            # xbmcgui.Dialog().ok('MODE=3','MODE')
            build_search(str(parameters['url']))
        elif mode == 4:  # TVShows
            # xbmcgui.Dialog().ok('MODE=4','MODE')
            build_groups_menu(parameters)
        elif mode == 5:  # TVSeasons
            # xbmcgui.Dialog().ok('MODE=5','MODE')
            build_serie_episodes_types(parameters)
        elif mode == 6:  # TVEpisodes/Eps in Serie
            # xbmcgui.Dialog().ok('MODE=6','MODE')
            build_serie_episodes(parameters)
        elif mode == 7:  # Playlist -continue-
            # xbmcgui.Dialog().ok('MODE=7','MODE')
            play_continue_item()
        else:
            build_filters_menu()
else:
    error("Incorrect Credentials", "Please change in Settings")
if __addon__.getSetting('remote_debug') == 'true':
    try:
        if pydevd:
            pydevd.stoptrace()
    except Exception as remote_exc:
        xbmc.log(str(remote_exc))
        pass
