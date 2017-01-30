#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import json

import resources.lib.TagBlacklist as TagFilter
import resources.lib.util as util
import resources.lib.search as search

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

from resources.lib.util import *

from collections import defaultdict

try:
    import pydevd
except ImportError:
    pass

handle = int(sys.argv[1])

__addon__ = xbmcaddon.Addon(id='plugin.video.nakamori')
__addonversion__ = __addon__.getAddonInfo('version')
__addonid__ = __addon__.getAddonInfo('id')

_server_ = "http://" + __addon__.getSetting("ipaddress") + ":" + __addon__.getSetting("port")
_home_ = xbmc.translatePath(__addon__.getAddonInfo('path').decode('utf-8'))


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


def refresh():
    """
    Refresh and re-request data from server
    """
    # refresh watch status as we now mark episode and refresh list so it show real status not kodi_cached
    xbmc.executebuiltin('Container.Refresh')
    # Allow time for the ui to reload (this may need to be tweaked, I am running on localhost)
    xbmc.sleep(int(__addon__.getSetting('refresh_wait')))


def move_position_on_list(control_list, position=0):
    """
    Move to the position in a list - use episode number for position
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
    if window_name == 'Continue Watching (System)':
        window_name = 'Continue Watching'
    elif window_name == 'Unsort':
        window_name = 'Unsorted'

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


def video_file_information(node_base, detail_dict):
    # extra_data['xVideoAspect'] = float(video.find('Media').get('aspectRatio', 0))
    # Video
    if 'VideoStream' not in detail_dict:
        detail_dict['VideoStream'] = ''
    if 'AudioStream' not in detail_dict:
        detail_dict['AudioStreams'] = ''
    if 'SubStream' not in detail_dict:
        detail_dict['SubStreams'] = ''

    for node in node_base:
        if "video" in node:
            for stream_info in node["videos"]:
                streams = detail_dict.get('VideoStreams')
                stream_id = int(stream_info["Index"])
                streams[stream_id]['VideoCodec'] = stream_info['Codec']
                streams['xVideoCodec'] = stream_info['Codec']
                streams[stream_id]['width'] = stream_info['Width']
                streams['xVideoResolution'] = stream_info['Width']
                streams[stream_id]['height'] = stream_info['Height']
                streams['xVideoResolution'] += "x" + stream_info['Height']
                streams[stream_id]['duration'] = stream_info['Duration']
                detail_dict['VideoStreams'] = streams

        # Audio
        if "audios" in node:
            for stream_info in node["audios"]:
                streams = detail_dict.get('AudioStreams')
                stream_id = int(stream_info["Index"])
                streams[stream_id]['AudioCodec'] = stream_info["Codec"] if "Codec" in stream_info else ""
                streams['xAudioChannels'] = safeInt(streams[stream_id]['AudioCodec'])
                streams[stream_id]['AudioLanguage'] = stream_info["LanguageCode"] if "LanguageCode" in stream_info else "unk"
                streams[stream_id]['AudioChannels'] = int(stream_info["Channels"]) if "Channels" in stream_info else ""
                streams['xAudioChannels'] = safeInt(streams[stream_id]['AudioChannels'])
                detail_dict['AudioStreams'] = streams

        # Subtitle
        if "subtitles" in node:
            for stream_info in node["subtitles"]:
                streams = detail_dict.get('SubStreams')
                stream_id = int(stream_info["Index"])
                streams[stream_id]['SubtitleLanguage'] = stream_info["LanguageCode"] if "LanguageCode" in stream_info else "unk"
                detail_dict['SubStreams'] = streams


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
            liz.setArt({'thumb': tbi, 'icon': tbi, 'poster': tbi})

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
                url_peep_base = sys.argv[2]

                # menu for episode
                if extra_data.get('source', 'none') == 'ep':
                    series_id = extra_data.get('serie_id')
                    ep_id = extra_data.get('ep_id')
                    url_peep = url_peep_base + "&serie_id=" + str(series_id) + "&ep_id=" + str(ep_id) + '&ui_index=' + str(index)

                    if __addon__.getSetting('context_show_play_no_watch') == 'true':
                        context.append(('Play (Do not Mark as Watched)', 'RunScript(plugin.video.nakamori, %s, %s&cmd=no_mark)' % (sys.argv[1], url_peep)))
                    if __addon__.getSetting('context_show_info') == 'true':
                        context.append(('More Info', 'Action(Info)'))

                    if __addon__.getSetting('context_show_vote_Series') == 'true':
                        if series_id != '':
                            context.append(('Vote for Series', 'RunScript(plugin.video.nakamori, %s, %s&cmd=voteSer)' % (sys.argv[1], url_peep)))
                    if __addon__.getSetting('context_show_vote_Episode') == 'true':
                        if ep_id != '':
                            context.append(('Vote for Episode', 'RunScript(plugin.video.nakamori, %s, %s&cmd=voteEp)' % (sys.argv[1], url_peep)))

                    if extra_data.get('jmmepisodeid') != '':
                        if __addon__.getSetting('context_krypton_watched') == 'true':
                            if details.get('playcount', 0) == 0:
                                context.append(('Mark episode as Watched', 'RunScript(plugin.video.nakamori, %s, %s&cmd=watched)' % (sys.argv[1], url_peep)))
                            else:
                                context.append(('Mark episode as Unwatched', 'RunScript(plugin.video.nakamori, %s, %s&cmd=unwatched)'% (sys.argv[1], url_peep)))
                        else:
                            context.append(('Mark episode as Watched', 'RunScript(plugin.video.nakamori, %s, %s&cmd=watched)' % (sys.argv[1], url_peep)))
                            context.append(('Mark episode as Unwatched', 'RunScript(plugin.video.nakamori, %s, %s&cmd=unwatched)' % (sys.argv[1], url_peep)))

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
        data: json node containing the title

    Returns: string of the desired title

    """
    try:
        if __addon__.getSetting('use_server_title') == 'true':
            return encode(data['name'])
        # xbmc.log(data.get('title', 'Unknown'))
        title = encode(data['name'].lower())
        if title == 'ova' or title == 'ovas' \
                or title == 'episode' or title == 'episodes' \
                or title == 'special' or title == 'specials' \
                or title == 'parody' or title == 'parodies' \
                or title == 'credit' or title == 'credits' \
                or title == 'trailer' or title == 'trailers' \
                or title == 'other' or title == 'others':
            return encode(data['name'])

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
            return encode(data['name'])
        except Exception as expc:
            error('Error thrown on getting title', str(expc))
            return encode(data['name'])
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
            temp_genre = ''
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
            char_seiyuuname = char['name']
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


def convert_cast_and_role_to_legacy(list_of_dicts):
    # This is for Kodi 16 and under which doesn't take the nice new function
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


# region Adding items to list/menu:

def add_raw_files(node):
    name = encode(node["filename"])
    file_id = node["id"]
    key = node["url"]
    url = _server_ + "/api/file?id=" + str(file_id)
    title = os.path.split(str(name))[1]
    thumb = _server_ + "/image/support/plex_others.png"
    liz = xbmcgui.ListItem(label=title, label2=title, path=url)
    liz.setArt({'thumb': thumb, 'poster': thumb, 'icon': 'DefaultVideo.png'})
    liz.setInfo(type="Video", infoLabels={"Title": title, "Plot": title})
    liz.setProperty('IsPlayable', 'true')
    u = sys.argv[0]
    u = set_parameter(u, 'url', url)
    u = set_parameter(u, 'mode', 1)
    u = set_parameter(u, 'id', file_id)
    u = set_parameter(u, 'name', urllib.quote_plus(title))
    u = set_parameter(u, 'type', "raw")
    u = set_parameter(u, 'file', key)
    u = set_parameter(u, 'ep_id', node["import_folder_id"])
    context = [('Rescan File', 'RunScript(plugin.video.nakamori, %s, %s&cmd=rescan)' % (sys.argv[1], u)),
               ('Rehash File', 'RunScript(plugin.video.nakamori, %s, %s&cmd=rehash)' % (sys.argv[1], u)),
               ('Remove missing files', 'RunScript(plugin.video.nakamori, %s, %s&cmd=missing)' % (sys.argv[1], u))]
    liz.addContextMenuItems(context)
    xbmcplugin.addDirectoryItem(handle, url=u, listitem=liz, isFolder=False)


def add_content_typ_dir(name, serie_id):
    """
    Adding directories for given types of content
    :param name: name of directory
    :param serie_id: id that the content belong too
    :return: add new directory
    """
    url = _server_ + "/api/serie?id=" + str(serie_id) + "&level=4"
    title = str(name)
    thumb = _server_ + "/api/image/support/"

    if title == "Credit":
        thumb += "plex_credits.png"
    elif title == "Movie":
        thumb += "plex_movies.png"
    elif title == "Ova":
        thumb += "plex_ovas.png"
    elif title == "Other":
        thumb += "plex_others.png"
    elif title == "Episode":
        thumb += "plex_episodes.png"
    elif title == "TV Episode":
        thumb += "plex_tvepisodes.png"
    elif title == "Web Clip":
        thumb += "plex_webclips.png"
    elif title == "Episode":
        thumb += "plex_episodes.png"
    elif title == "Parody":
        thumb += "plex_parodies.png"
    elif title == "Special":
        thumb += "plex_specials.png"
    elif title == "Trailer":
        thumb += "plex_trailers.png"
    elif title == "Misc":
        thumb += "plex_misc.png"
    else:
        thumb += "plex_others.png"

    liz = xbmcgui.ListItem(label=title, label2=title, path=url)
    liz.setArt({'thumb': thumb, 'poster': thumb, 'icon': 'DefaultVideo.png'})
    liz.setInfo(type="Video", infoLabels={"Title": title, "Plot": title})
    u = sys.argv[0]
    u = set_parameter(u, 'url', url)
    u = set_parameter(u, 'mode', str(6))
    u = set_parameter(u, 'name', urllib.quote_plus(title))
    u = set_parameter(u, 'type', name)
    xbmcplugin.addDirectoryItem(handle, url=u, listitem=liz, isFolder=True)


def add_serie_item(node, parent_title):
    # xbmcgui.Dialog().ok('series', 'series')
    temp_genre = get_tags(node["tags"])
    watched = int(node["viewed"])

    list_cast = []
    list_cast_and_role = []
    actors = []
    if len(list_cast) == 0:
        result_list = get_cast_and_role(node["roles"])
        actors = result_list
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
    key = set_parameter(key, 'id', key_id)
    if __addon__.getSetting('request_nocast') == 'true':
        key = set_parameter(key, 'nocast', 1)

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
        'actors':               actors,
        'serie_id':             key_id
    }

    url = key
    set_watch_flag(extra_data, details)
    use_mode = 5

    u = sys.argv[0]
    u = set_parameter(u, 'url', url)
    u = set_parameter(u, 'mode', use_mode)
    u = set_parameter(u, 'movie', node['ismovie'] if 'ismovie' in node else 0)

    context = []
    url_peep = sys.argv[2] + "&serie_id=" + key_id
    if __addon__.getSetting('context_show_info') == 'true':
        context.append(('More Info', 'Action(Info)'))
    if __addon__.getSetting('context_show_vote_Series') == 'true':
        context.append(('Vote on serie', 'RunScript(plugin.video.nakamori, %s, %s)' % (sys.argv[1], url_peep + "&cmd=voteSer")))
    context.append(('Mark serie as Watched', 'RunScript(plugin.video.nakamori, %s, %s&cmd=watched)' % (sys.argv[1], url_peep)))
    context.append(('Mark serie as Unwatched', 'RunScript(plugin.video.nakamori, %s, %s&cmd=unwatched)' % (sys.argv[1], url_peep)))

    add_gui_item(u, details, extra_data, context)


def add_group_item(node, parent_title, filter_id, is_filter=False):
    temp_genre = get_tags(node.get("tags", ""))
    title = node['name']
    size = node["size"]
    content_type = node["type"] if not is_filter else "filter"
    details = {
        'title':            title,
        'parenttitle':      encode(parent_title),
        'genre':            temp_genre,
        'year':             safeInt(node["year"]) if "year" in node else "2001",
        'episode':          size,
        'season':           safeInt(node["season"]) if "season" in node else "0",
        'size':             size,
        'rating':           float(str(node["rating"] if node["rating"] is not None else 0.0).replace(',', '.')) if "rating" in node else "0.0",
        'playcount':        int(node["viewed"]) if "viewed" in node else "0",
        'plot':             remove_anidb_links(encode(node["summary"] if node["summary"] is not None else "...")) if "summary" in node else "...",
        'originaltitle':    title,
        'sorttitle':        title,
        'tvshowname':       title,
        'dateadded':        node["added"] if "added" in node else "01-01-2001"
    }

    key_id = str(node["id"])
    if is_filter:
        key = _server_ + "/api/filter?id=" + key_id
    else:
        key = _server_ + "/api/group?id=" + key_id
    key = set_parameter(key, 'id', key_id)
    key = set_parameter(key, 'filter', filter_id)
    if __addon__.getSetting('request_nocast') == 'true':
        key = set_parameter(key, 'nocast', 1)

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
        'source':               content_type,
        'thumb':                thumb,
        'fanart_image':         fanart,
        'banner':               banner,
        'key':                  key,
        'group_id':             key_id,
        'WatchedEpisodes':      0,
        'TotalEpisodes':        size,
        'UnWatchedEpisodes':    size
    }

    url = key
    set_watch_flag(extra_data, details)
    use_mode = 5 if not is_filter else 4

    u = sys.argv[0]
    u = set_parameter(u, 'url', url)
    u = set_parameter(u, 'mode', str(use_mode))
    if filter_id != '':
        u = set_parameter(u, 'filter', filter_id)
    else:
        u = set_parameter(u, 'filter', None)

    context = []
    if __addon__.getSetting('context_show_info') == 'true' and not is_filter:
        context.append(('More Info', 'Action(Info)'))
        url_peep = sys.argv[2] + "&group_id=" + key_id
        context.append(('Mark group as Watched', 'RunScript(plugin.video.nakamori, %s, %s&cmd=watched)' % (sys.argv[1], url_peep)))
        context.append(('Mark group as Unwatched', 'RunScript(plugin.video.nakamori, %s, %s&cmd=unwatched)' % (sys.argv[1], url_peep)))

    add_gui_item(u, details, extra_data, context)


def build_filters_menu():
    """
    Builds the list of items (filters) in the Main Menu
    """
    xbmcplugin.setContent(handle, content='tvshows')
    try:
        json_menu = json.loads(get_json(_server_ + "/api/filter"))
        set_window_heading(json_menu['name'])
        try:
            for menu in json_menu["filters"]:
                title = menu['name']
                use_mode = 4
                key = menu["url"]
                size = safeInt(menu["size"])

                if title == 'Continue Watching (SYSTEM)':
                    title = 'Continue Watching'
                # TODO : is it not lang related? because we can 'if /file/unsort'
                elif title == 'Unsort':
                    title = 'Unsorted'
                    use_mode = 8

                if __addon__.getSetting("spamLog") == "true":
                    xbmc.log("build_filters_menu - key = " + key)

                if __addon__.getSetting('request_nocast') == 'true' and title != 'Unsorted':
                    key += '&nocast=1'
                url = key

                thumb = ''
                try:
                    if len(menu["art"]["thumb"]) > 0:
                        thumb = menu["art"]["thumb"][0]["url"]
                    if "Year" in title:
                        thumb = os.path.join(_home_, 'resources/media/icons', 'year.png')
                    elif "Tag" in title:
                        thumb = os.path.join(_home_, 'resources/media/icons', 'tag.png')
                except:
                    if "Year" in title:
                        thumb = os.path.join(_home_, 'resources/media/icons', 'year.png')
                    elif "Tag" in title:
                        thumb = os.path.join(_home_, 'resources/media/icons', 'tag.png')
                fanart = ''
                try:
                    if len(menu["art"]["fanart"]) > 0:
                        fanart = menu["art"]["fanart"][0]["url"]
                except:
                    pass
                banner = ''
                try:
                    if len(menu["art"]["banner"]) > 0:
                        banner = menu["art"]["banner"][0]["url"]
                except:
                    pass

                u = sys.argv[0]
                u = set_parameter(u, 'url', url)
                u = set_parameter(u, 'mode', use_mode)
                u = set_parameter(u, 'name', urllib.quote_plus(title))
                u = set_parameter(u, 'filter_id', menu["id"])

                liz = xbmcgui.ListItem(label=title, label2=title, path=url)
                liz.setArt({'icon': thumb, 'thumb': thumb, 'fanart': fanart, 'poster': thumb, 'banner': banner, 'clearart': fanart})
                if thumb == '': liz.setIconImage('DefaultVideo.png')
                liz.setInfo(type="Video", infoLabels={"Title": title, "Plot": title, "count": size})
                xbmcplugin.addDirectoryItem(handle, url=u, listitem=liz, isFolder=True)
        except Exception as e:
            error("Error during build_filters_menu", str(e))
    except Exception as e:
        error("Invalid JSON Received in build_filters_menu", str(e))

    # region Start Add_Search
    url = _server_ + "/api/search"
    title = "Search"
    liz = xbmcgui.ListItem(label=title, label2=title, path=url)
    liz.setArt({"icon": os.path.join(_home_, 'resources/media/icons', 'search.png'), "fanart": os.path.join(_home_, 'resources/media', 'new-search.jpg')})
    liz.setInfo(type="Video", infoLabels={"Title": title, "Plot": title})
    u = sys.argv[0]
    u = set_parameter(u, 'url', url)
    u = set_parameter(u, 'mode', str(3))
    u = set_parameter(u, 'name', urllib.quote_plus(title))
    xbmcplugin.addDirectoryItem(handle, url=u, listitem=liz, isFolder=True)
    # endregion

    xbmcplugin.endOfDirectory(handle, True, False, False)


def build_groups_menu(params, json_body=None):
    """
    Builds the list of items for Filters and Groups
    Args:
        params:
        json_body: parsing json_file directly, this will skip loading remote url from params
    Returns:

    """
    # xbmcgui.Dialog().ok('MODE=4', 'IN')
    xbmcplugin.setContent(handle, 'tvshows')
    if __addon__.getSetting('use_server_sort') == 'false':
        xbmcplugin.addSortMethod(handle, 27)  # video title ignore THE
        xbmcplugin.addSortMethod(handle, 3)  # date
        xbmcplugin.addSortMethod(handle, 18)  # rating
        xbmcplugin.addSortMethod(handle, 17)  # year
        xbmcplugin.addSortMethod(handle, 28)  # by MPAA

    try:
        if json_body is None:
            # level 3 will fill group and series
            html = get_json(params['url'] + "&level=3")
            if __addon__.getSetting("spamLog") == "true":
                xbmc.log(params['url'])
                xbmc.log(html)
            dbg(html)
            body = json.loads(html)
        else:
            body = json_body

        # check if this is maybe filter-inception
        try:
            set_window_heading(body['name'])
        except:
            try: # this might not be a filter
                # it isn't single filter
                for nest_filter in body:
                    add_group_item(nest_filter, '', body['id'], True)
                xbmcplugin.endOfDirectory(handle)
                return
            except:
                pass

        try:
            parent_title = body['name']

            directory_type = body['type']
            filter_id = ''
            if directory_type != 'ep' and directory_type != 'serie':
                if 'filter' in params:
                    filter_id = params['filter']
                    if directory_type == 'filter':
                        filter_id = body['id']

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
            elif directory_type == 'filters':
                for flt in body["filters"]:
                    add_group_item(flt, parent_title, filter_id)

        except Exception as e:
            error("Error during build_groups_menu", str(e))
    except Exception as e:
        error("Invalid JSON Received in build_groups_menu", str(e))
    xbmcplugin.endOfDirectory(handle)


def build_serie_episodes_types(params):
    """
    Builds list items for The Types Menu, or optionally subgroups
    Args:
        params:

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

            content_type = dict()
            if "eps" in body:
                if len(body["eps"]) >= 1:
                    for ep in body["eps"]:
                        if ep["eptype"] not in content_type.keys():
                            content_type[ep["eptype"]] = ep["art"]["thumb"][0]["url"]
            # no matter what type is its only one type, flat directory
            if len(content_type) == 1:
                build_serie_episodes(params)
                return
            else:
                set_window_heading(parent_title)

                if __addon__.getSetting('use_server_sort') == 'false':
                    # Apparently date sorting in Kodi has been broken for years
                    xbmcplugin.addSortMethod(handle, 17)  # year
                    xbmcplugin.addSortMethod(handle, 27)  # video title ignore THE
                    xbmcplugin.addSortMethod(handle, 3)  # date
                    xbmcplugin.addSortMethod(handle, 18)  # rating
                    xbmcplugin.addSortMethod(handle, 28)  # by MPAA

                for content in content_type:
                    add_content_typ_dir(content, body["id"])
                xbmcplugin.endOfDirectory(handle)
                return

        except Exception as exc:
            error("Error during build_serie_episodes_types", str(exc))
    except Exception as exc:
        error("Invalid JSON Received in build_serie_episodes_types", str(exc))
    xbmcplugin.endOfDirectory(handle)


def build_serie_episodes(params):
    # xbmcgui.Dialog().ok('MODE=6','IN')
    """

    :param params:
    :return:
    """
    xbmcplugin.setContent(handle, 'episodes')
    try:
        html = get_json(params['url'])
        body = json.loads(html)
        if __addon__.getSetting("spamLog") == "true":
            xbmc.log(html)

        try:
            parent_title = ''
            try:
                parent_title = body["title"]
                set_window_heading(parent_title)
            except Exception as exc:
                error("Unable to get parent title in buildTVEpisodes", str(exc))

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
            temp_genre = ""
            parent_key = ""
            grandparent_title = ""
            list_cast = []
            list_cast_and_role = []
            actors = []
            if not skip:
                if len(list_cast) == 0:
                    result_list = get_cast_and_role(body["roles"])
                    actors = result_list
                    if result_list is not None:
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
                                'userrating':    float(str(video["UserRating"]).replace(',', '.')) if "UserRating" in video else 0,
                                # 'studio'      : episode.get('studio',tree.get('studio','')), 'utf-8') ,
                                # This doesn't work, some gremlins be afoot in this code...
                                # it's probably just that it only applies at series level
                                'castandrole':   list_cast_and_role,
                                'cast':          list_cast,
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
                                'originaltitle': encode(video["title"]),
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

                            key = video["files"][0]["url"]
                            media = video["files"][0]["media"]

                            # Extra data required to manage other properties
                            extra_data = {
                                'type':             "video",
                                'source':           "ep",
                                'thumb':            None if skip else thumb,
                                'fanart_image':     None if skip else fanart,
                                'banner':           None if skip else banner,
                                'key':              key,
                                # 'resume':           int(int(view_offset) / 1000),<---
                                'parentKey':        parent_key,
                                'jmmepisodeid':     safeInt(body["id"]),
                                'actors':           actors,
                                'AudioStreams':     defaultdict(dict),
                                'SubStreams':       defaultdict(dict),
                                'ep_id':            safeInt(video["id"]),
                                'serie_id':         safeInt(body["id"])
                            }

                            # Information about streams inside video file
                            if media is not None:
                                if len(video["files"][0]["media"]) > 0:
                                    for media_info in video["files"][0]["media"]:
                                        video_file_information(media_info, extra_data)

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
                            u = set_parameter(u, 'mode', 1)
                            u = set_parameter(u, 'file', key)
                            u = set_parameter(u, 'ep_id', video["id"])
                            u = set_parameter(u, 'serie_id', body["id"])
                            u = set_parameter(u, 'userrate', details["userrating"])
                            u = set_parameter(u, 'ui_index', str(int(episode_count - 1)))

                            add_gui_item(u, details, extra_data, context, folder=False, index=int(episode_count - 1))

            # add item to move to next not played item (not marked as watched)
            if __addon__.getSetting("show_continue") == "true":
                if str(parent_title).lower() != "unsort":
                    util.addDir("-continue-", '', '7', _server_ + "/image/support/plex_others.png", "Next episode", "3", "4", str(next_episode))

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
        error("Invalid JSON Received in build_serie_episodes", str(exc))
    xbmcplugin.endOfDirectory(handle)


def build_search_directory():
    """
    Build Search directory 'New Search' and read Search History
    :return:
    """
    items = [{
        "title": "New Search",
        "url": _server_ + "/api/serie",
        "mode": 3,
        "poster": "none",
        "icon": os.path.join(_home_, 'resources/media/icons', 'search.png'),
        "fanart": os.path.join(_home_, 'resources/media', 'new-search.jpg'),
        "type": "",
        "plot": "",
        "extras": "true-search"
    }, {
        "title": "[COLOR yellow]Clear Search Terms[/COLOR]",
        "url": "delete-all",
        "mode": 31,
        "poster": "none",
        "icon": os.path.join(_home_, 'resources/media/icons', 'trash.png'),
        "fanart": os.path.join(_home_, 'resources/media', 'clear-search.jpg'),
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
                    "url": _server_ + "/api/search?query=" + ss[0],
                    "mode": 3,
                    "poster": "none",
                    "icon": os.path.join(_home_, 'resources/media/icons', 'tag.png'),
                    "fanart": os.path.join(_home_, '', 'fanart.jpg'),
                    "type": "",
                    "plot": "",
                    "extras": "force-search",
                    "extras2": "db-search"
                })
        except:
            pass

    for detail in items:
        u = sys.argv[0] + "?url=" + detail['url'] + "&mode=" + str(detail['mode']) + "&name=" + urllib.quote_plus(detail['title'].encode("utf-8")) + "&extras=" + detail['extras']
        liz = xbmcgui.ListItem(detail['title'].encode("utf-8"))
        liz.setArt({'thumb': detail['icon'], 'poster': detail['poster'], 'icon': detail['icon'], 'fanart': detail['fanart']})
        liz.setInfo(type=detail['type'], infoLabels={"Title": detail['title'].encode("utf-8"), "Plot": detail['plot']})
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    xbmcplugin.endOfDirectory(handle)


def search_for(url):
    try:
        url = set_parameter(url, 'tags', 2)
        url = set_parameter(url, 'level', 1)
        url = set_parameter(url, 'limit', __addon__.getSetting('maxlimit'))
        url = set_parameter(url, 'limit_tag', __addon__.getSetting('maxlimit_tag'))
        json_body = json.loads(get_json(url))
        if json_body["groups"][0]["size"] == 0:
            xbmc.executebuiltin("XBMC.Notification(%s, %s %s, 7500, %s)" % ('No results', 'No items found', '!', __addon__.getAddonInfo('icon')))
        else:
            build_groups_menu(url, json_body)
    except:
        error("error in findVideo")


def execute_search_and_add_query():
    """
    Search for query and if its not in Search History add it
    :return:
    """
    find = util.searchBox()
    # check search history
    if not search.check_in_database(find):
        # if its not add to history & refresh
        search.add_search_history(find)
        xbmc.executebuiltin('Container.Refresh')
    search_for(_server_ + "/api/search?query=" + find)


def build_raw_list(params):
    """
    Build list of RawFiles (ex. Unsort)
    :param params: json body with all files to draw
    :return:
    """
    xbmcplugin.setContent(handle, 'files')
    try:
        html = get_json(params['url'])
        body = json.loads(html)
        if __addon__.getSetting("spamLog") == "true":
            xbmc.log(html)

        try:
            for file_body in body:
                add_raw_files(file_body)
        except Exception as exc:
            error("Error during build_raw_list add_raw_files", str(exc))
    except Exception as exc:
        error("Error during build_raw_list", str(exc))

    xbmcplugin.endOfDirectory(handle, True, False, False)

# endregion


# Other functions
def play_video(url, ep_id, raw_id, movie):
    """
    Plays a file or episode
    Args:
        url: location of the file
        ep_id: episode id, if applicable for watched status and stream details
        raw_id: file id, that is only used when ep_id = 0
        movie: determinate if played object is movie or episode (ex.Trakt)
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

    item = xbmcgui.ListItem(details.get('title', 'Unknown'), thumbnailImage=xbmc.getInfoLabel('ListItem.Thumb'), path=url)
    item.setInfo(type='Video', infoLabels=details)
    item.setProperty('IsPlayable', 'true')
    try:
        if ep_id != "0":
            episode_url = _server_ + "/api/ep?id=" + str(ep_id)
            html = get_json(encode(episode_url))
            if __addon__.getSetting("spamLog") == "true":
                xbmc.log(html)
            episode_body = json.loads(html)
            # extract extra data about file from episode
            file_id = episode_body["files"][0]["id"]
        else:
            file_id = raw_id
        if file_id is not None and file_id != 0:
            file_url = _server_ + "/api/file?id=" + str(file_id)
            file_body = json.loads(get_json(file_url))
            
            # Information about streams inside video file
            # Video
            codecs = dict()

            for stream_info in file_body["media"]:
                video_file_information(stream_info, codecs)
            item.addStreamInfo('video', codecs["VideoStream"])
            item.addStreamInfo('audio', codecs["AudioStreams"])
            item.addStreamInfo('subtitle', codecs["SubStreams"])
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
    trakt_404 = False
    # hack for slow connection and buffering time
    xbmc.sleep(int(__addon__.getSetting("player_sleep")))
    try:
        clock_tick = -1
        while player.isPlaying():
            try:
                if clock_tick == -1:
                    if __addon__.getSetting("trakt_scrobble_notification") == "true":
                        xbmc.executebuiltin("XBMC.Notification(%s, %s %s, 7500, %s)" % ('Trakt.tv', 'Starting Scrobble', '', __addon__.getAddonInfo('icon')))
                clock_tick += 1
                xbmc.sleep(60)
                total_time = player.getTotalTime()
                current_time = player.getTime()

                # region Trakt support
                if __addon__.getSetting("trakt_scrobble") == "true":
                    if clock_tick >= 200:
                        clock_tick = 0
                        if ep_id != 0:
                            progress = int((current_time / total_time) * 100)
                            try:
                                if not trakt_404:
                                    # status: 1-start,2-pause,3-stop
                                    trakt_body = json.loads(get_json(_server_ + "/api/ep/scrobble?id=" + str(ep_id) + "&ismovie=" + str(movie) + "&status=" + str(1) + "&progress=" + str(progress)))
                                    if str(trakt_body['code']) != str(200):
                                        trakt_404 = True
                            except Exception as trakt_ex:
                                dbg(str(trakt_ex))
                                pass
                # endregion

                if (total_time * mark) < current_time:
                    file_fin = True
                if not player.isPlaying():
                    break
            except:
                xbmc.sleep(60)
                if not trakt_404:
                    # send 'pause' to trakt
                    json.loads(get_json(_server_ + "/api/ep/scrobble?id=" + str(ep_id) + "&ismovie=" + str(movie) + "&status=" + str(2) + "&progress=" + str(progress)))
                break
    except Exception as ops_ex:
        dbg(ops_ex)
        pass

    no_watch_status = False
    if __addon__.getSetting('no_mark') != "0":
        no_watch_status = True
        # reset no_mark so next file will mark watched status
        __addon__.setSetting('no_mark', '0')

    if file_fin is True:
        if __addon__.getSetting("trakt_scrobble") == "true":
            if not trakt_404:
                get_json(_server_ + "/api/ep/scrobble?id=" + str(ep_id) + "&ismovie=" + str(movie) + "&status=" + str(3) + "&progress=" + str(100))
                if __addon__.getSetting("trakt_scrobble_notification") == "true":
                    xbmc.executebuiltin("XBMC.Notification(%s, %s %s, 7500, %s)" % ('Trakt.tv', 'Stopping scrobble', '', __addon__.getAddonInfo('icon')))

        if no_watch_status is False:
            return ep_id
    return 0


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
        series_id = params['serie_id']
        body = '?id=' + series_id + '&score=' + vote_value
        get_json(_server_ + "/serie/vote" + body)
        xbmc.executebuiltin("XBMC.Notification(%s, %s %s, 7500, %s)" % ('Serie voting', 'You voted', vote_value, __addon__.getAddonInfo('icon')))


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
        body = '?id=' + ep_id + '&score=' + vote_value
        get_json(_server_ + "/ep/vote" + body)
        xbmc.executebuiltin("XBMC.Notification(%s, %s %s, 7500, %s)" % ('Episode voting', 'You voted', vote_value, __addon__.getAddonInfo('icon')))


def watched_mark(params):
    """
    Marks an episode, series, or group as either watched or unwatched
    Args:
        params: must contain either an episode, series, or group id, and a watched value to mark
    """
    episode_id = params.get('ep_id', '')
    anime_id = params.get('serie_id', '')
    group_id = params.get('group_id', '')
    watched = bool(params['watched'])
    key = _server_ + "/api"
    if watched is True:
        watched_msg = "watched"
        if episode_id != '':
            key += "/ep/watch"
        elif anime_id != '':
            key += "/serie/watch"
        elif group_id != '':
            key += "/group/watch"
    else:
        watched_msg = "unwatched"
        if episode_id != '':
            key += "/ep/unwatch"
        elif anime_id != '':
            key += "/serie/unwatch"
        elif group_id != '':
            key += "/group/unwatch"

    if __addon__.getSetting('log_spam') == 'true':
        xbmc.log('epid: ' + str(episode_id))
        xbmc.log('anime_id: ' + str(anime_id))
        xbmc.log('group_id: ' + str(group_id))
        xbmc.log('key: ' + key)

    # sync mark flags
    sync = __addon__.getSetting("syncwatched")
    if sync == "true":
        if episode_id != '':
            body = '?id=' + episode_id
            get_json(key + body)
        elif anime_id != '':
            body = '?id=' + anime_id + '"'
            get_json(key + body)
        elif group_id != '':
            body = '?id=' + group_id + '"'
            get_json(key + body)

    box = __addon__.getSetting("watchedbox")
    if box == "true":
        xbmc.executebuiltin("XBMC.Notification(%s, %s %s, 2000, %s)" % ('Watched status changed', 'Mark as ', watched_msg, __addon__.getAddonInfo('icon')))
    refresh()


def rescan_file(params, rescan):
    """
    Rescans or rehashes a file
    Args:
        params:
        rescan: True to rescan, False to rehash
    """
    vl_id = params.get('ep_id', '')
    command = 'rehash'
    if rescan:
        command = 'rescan'

    key_url = ""
    if vl_id != '':
        key_url = _server_ + "/api/" + command + "?id=" + vl_id
    if __addon__.getSetting('log_spam') == 'true':
        xbmc.log('vlid: ' + str(vl_id))
        xbmc.log('key: ' + key_url)

    get_json(key_url)

    xbmc.executebuiltin("XBMC.Notification(%s, %s, 2000, %s)" % ('Queued file for ' + ('Rescan' if rescan else 'Rehash'), 'Refreshing in 10 seconds', __addon__.getAddonInfo('icon')))
    xbmc.sleep(10000)
    refresh()


def remove_missing_files():
    """
    Run "remove missing files" on server to remove every file that is not accessible by server
    :return:
    """
    key = _server_ + "/api/remove_missing_files"

    if __addon__.getSetting('log_spam') == 'true':
        xbmc.log('key: ' + key)

    get_json(key)
    xbmc.executebuiltin("XBMC.Notification(%s, %s, 2000, %s)" % ('Removing missing files...', 'This can take some time', __addon__.getAddonInfo('icon')))
    xbmc.sleep(10000)
    refresh()


# region Setting up Remote Debug
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
#endregion

# Script run from here
if valid_user() is True:
    try:
        parameters = util.parseParameters()
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
        elif cmd == 'missing':
            remove_missing_files()
    else:
        # xbmcgui.Dialog().ok('MODE=' + str(mode), str(parameters))
        if mode == 1:  # play_file
            try:
                win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
                ctl = win.getControl(win.getFocusId())
                if play_video(parameters['file'], parameters['ep_id'], parameters['file_id'] if 'id' in parameters else "0", parameters['movie'] if 'movie' in parameters else 0) != 0:
                    # noinspection PyTypeChecker
                    ui_index = parameters.get('ui_index', '')
                    if ui_index != '':
                        move_position_on_list(ctl, int(ui_index) + 1)
                    parameters['watched'] = True
                    watched_mark(parameters)
                    if __addon__.getSetting('vote_always') == 'true':
                        if parameters.get('userrate', 0) == 0:
                            vote_episode(parameters)
            except Exception as exp:
                xbmc.log(str(exp))
                pass
        elif mode == 2:  # DIRECTORY
            xbmcgui.Dialog().ok('MODE=2', 'MODE')
        elif mode == 3:  # Search
            try:
                if parameters['extras'] == "force-search":
                    search_for(parameters['url'])
                else:
                    xbmcplugin.setContent(int(handle), "movies")
                    execute_search_and_add_query()
            except:
                build_search_directory()
        elif mode == 4:  # Group/Serie
            build_groups_menu(parameters)
        elif mode == 5:  # Serie EpisodeTypes (episodes/ovs/credits)
            build_serie_episodes_types(parameters)
        elif mode == 6:  # Serie Episodes (list of episodes)
            build_serie_episodes(parameters)
        elif mode == 7:  # Playlist -continue-
            play_continue_item()
        elif mode == 8:  # File List
            build_raw_list(parameters)
        elif mode == 31:
            search.clear_search_history(parameters)
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
