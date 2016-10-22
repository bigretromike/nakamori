#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import os
import re
import sys
import urllib
import json

import resources.lib.TagBlacklist as TagFilter
import resources.lib.util as util

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

from resources.lib.util import set_parameter, error, get_xml,\
    get_json, xml, post_data, encode, decode

from collections import defaultdict

try:
    import pydevd
except ImportError:
    pass

handle = int(sys.argv[1])

__addon__ = xbmcaddon.Addon(id='plugin.video.nakamori')
__addonversion__ = __addon__.getAddonInfo('version')
__addonid__ = __addon__.getAddonInfo('id')


def valid_user():
    """
    Logs into the server and stores the apikey, then checks if the userid is valid
    :return: bool True if all completes successfully
    """
    xml_file = get_xml("http://" + __addon__.getSetting("ipaddress") + ":" + __addon__.getSetting("port") +
                       "/jmmserverkodi/getversion")
    if xml_file is not None:
        data = xml(xml_file)
        version = data.get('Message')
        if version == "3.6.1.0":
            return valid_userid()

    # reset apikey if user enters new login info
    if __addon__.getSetting("apikey") != "" and __addon__.getSetting("login") == "":
        # ignore what we put in for userid, the api sets it
        set_userid()
        return valid_userid()
    else:
        xbmc.log('-- apikey empty --')
        # password can be empty as JMM Default account have blank password
        try:
            if __addon__.getSetting("login") != "" and __addon__.getSetting("device") != "":
                body = '{"user":"' + __addon__.getSetting("login") + '",' + \
                       '"device":"' + __addon__.getSetting("device") + '",' + \
                       '"pass":"' + __addon__.getSetting("password") + '"}'
                post = post_data("http://" + __addon__.getSetting("ipaddress") + ":" + __addon__.getSetting("port") +
                                 "/api/auth", body)
                auth = json.loads(post)
                if "apikey" in auth:
                    xbmc.log('-- save apikey and reset user credentials --')
                    __addon__.setSetting(id='apikey', value=str(auth["apikey"]))
                    __addon__.setSetting(id='login', value='')
                    __addon__.setSetting(id='password', value='')
                    set_userid()
                    return valid_userid()
                else:
                    raise Exception('Error Getting apikey')
            else:
                xbmc.log('-- Login and Device Empty --')
                return False
        except Exception as exc:
            error('Error in Valid_User', str(exc))
            return False


def set_userid():
    """
    Set userid that is assign to current user via jmm3.7+ api
    Returns: bool True if set assign was successful
    """
    uid = json.loads(get_json("http://" + __addon__.getSetting("ipaddress") + ":" +
                              __addon__.getSetting("port") + "/api/myid/get"))
    if "userid" in uid:
        __addon__.setSetting(id='userid', value=str(uid['userid']))
        return True
    else:
        return False


def valid_userid():
    """
    Checks if the set userid is valid
    Returns: bool True if valid

    """
    xml_file = get_xml("http://" + __addon__.getSetting("ipaddress") + ":" + __addon__.getSetting("port") +
                       "/jmmserverkodi/getusers")
    if xml_file is not None:
        data = xml(xml_file)
        for user_data in data.findall('User'):
            user_id = user_data.get('id', '')
            if user_id == __addon__.getSetting("userid"):
                return True
        return False
    return False


def refresh():
    """
    Refresh and re-request data from server
    """
    # refresh watch status as we now mark episode and refresh list so it show real status not kodi_cached
    xbmc.executebuiltin('Container.Refresh')
    # Allow time for the ui to reload (this may need to be tweaked, I am running on localhost)
    xbmc.sleep(int(__addon__.getSetting('refresh_wait')))


# use episode number for position
def move_position_on_list(control_list, position=0):
    """
    Move to the position in a list
    Args:
        control_list: the list control
        position: the index of the item not including settings
    """
    if __addon__.getSetting('show_continue') == 'true':
        position = int(position + 1)

    try:
        parent_setting = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Settings.GetSettingValue", "params":' +
                                             '{"setting": "filelists.showparentdiritems"}, "id": 1}')
        # {"id":1,"jsonrpc":"2.0","result":{"value":false}} or true if ".." is displayed on list

        setting = json.loads(parent_setting)
        if "result" in setting:
            if "value" in setting["result"]:
                if setting["result"]["value"]:
                    position = int(position + 1)
    except Exception as ex:
        error("jsonrpc_error: " + str(ex))

    try:
        control_list.selectItem(position)
    except:
        try:
            control_list.selectItem(position - 1)
        except:
            error('Unable to reselect item')
            xbmc.log('control_list: ' + str(control_list.getId()), xbmc.LOGWARNING)
            xbmc.log('position: ' + str(position), xbmc.LOGWARNING)


def set_window_heading(var_tree):
    """
    Sets the window titles
    Args:
        var_tree: details dict
    """
    window_obj = xbmcgui.Window(xbmcgui.getCurrentWindowId())
    try:
        window_obj.setProperty("heading", var_tree.get('title1'))
    except Exception as e:
        error('set_window_heading Exception', str(e))
        window_obj.clearProperty("heading")
    try:
        window_obj.setProperty("heading2", var_tree.get('title2'))
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

        # handle short urls to work with seriesid and epid
        if extra_data.get('key', '') != '':
            url_in = str(extra_data.get('key'))
            if folder:
                if not url_in.lower().startswith("http://" + __addon__.getSetting("ipaddress") + ":" +
                                                 __addon__.getSetting("port")):
                    if url_in.lower().startswith('/jmmserverkodi'):
                        extra_data['key'] = "http://" + __addon__.getSetting("ipaddress") + ":" + \
                                            __addon__.getSetting("port") + url_in

        # do this before so it'll log
        # use the year as a fallback in case the date is unavailable
        if details.get('date', '') == '':
            if details.get('year', '') != '' and details['year'] != 0:
                details['date'] = '01.01.' + str(details['year'])
                details['aired'] = details['date']
                # details['aired'] = str(details['year'])+'-01-01'
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

        if extra_data is not None:
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
            liz.setArt({'poster': get_poster(tbi)})

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
            if extra_data.get('source') == 'AnimeGroup' or extra_data.get('source') == 'AnimeSerie':
                # Then set the number of watched and unwatched, which will be displayed per season
                liz.setProperty('TotalEpisodes', str(extra_data['TotalEpisodes']))
                liz.setProperty('WatchedEpisodes', str(extra_data['WatchedEpisodes']))
                liz.setProperty('UnWatchedEpisodes', str(extra_data['UnWatchedEpisodes']))
                # Hack to show partial flag for TV shows and seasons
                if extra_data.get('partialTV') == 1:
                    liz.setProperty('TotalTime', '100')
                    liz.setProperty('ResumeTime', '50')
                if extra_data.get('fanart_image'):
                    liz.setArt({"fanart": extra_data.get('fanart_image', '')})
                if extra_data.get('banner'):
                    liz.setArt({'banner': extra_data.get('banner', '')})
                if extra_data.get('season_thumb'):
                    liz.setArt({'seasonThumb': extra_data.get('season_thumb', '')})

        if context is None:
            if extra_data and len(extra_data) > 0:
                if extra_data.get('type', 'video').lower() == "video":
                    context = []
                    url_peep_base = sys.argv[2]
                    my_len = len(
                        "http://" + __addon__.getSetting("ipaddress") + ":" + __addon__.getSetting("port")
                        + __addon__.getSetting("userid"))

                    if extra_data.get('source', 'none') == 'AnimeSerie':
                        series_id = extra_data.get('key')[(my_len + 30):]
                        url_peep = url_peep_base + "&anime_id=" + series_id + "&cmd=voteSer"
                        if __addon__.getSetting('context_show_info') == 'true':
                            context.append(('More Info', 'Action(Info)'))
                        if __addon__.getSetting('context_show_vote_Series') == 'true':
                            context.append(('Vote (JMM)', 'RunScript(plugin.video.nakamori, %s, %s)' %
                                            (sys.argv[1], url_peep)))
                        url_peep = url_peep_base + "&anime_id=" + series_id
                        context.append(('Mark as Watched (JMM)',
                                        'RunScript(plugin.video.nakamori, %s, %s&cmd=watched)'
                                        % (sys.argv[1], url_peep)))
                        context.append(('Mark as Unwatched (JMM)',
                                        'RunScript(plugin.video.nakamori, %s, %s&cmd=unwatched)'
                                        % (sys.argv[1], url_peep)))
                    elif extra_data.get('source', 'none') == 'AnimeGroup':
                        series_id = extra_data.get('key')[(my_len + 30):]
                        if __addon__.getSetting('context_show_info') == 'true':
                            context.append(('More Info', 'Action(Info)'))
                        url_peep = url_peep_base + "&group_id=" + series_id
                        context.append(('Mark as Watched (JMM)',
                                        'RunScript(plugin.video.nakamori, %s, %s&cmd=watched)'
                                        % (sys.argv[1], url_peep)))
                        context.append(('Mark as Unwatched (JMM)',
                                        'RunScript(plugin.video.nakamori, %s, %s&cmd=unwatched)'
                                        % (sys.argv[1], url_peep)))
                    elif extra_data.get('source', 'none') == 'tvepisodes':
                        series_id = extra_data.get('parentKey')[(my_len + 30):]
                        url_peep = url_peep_base + "&anime_id=" + series_id + \
                                   "&ep_id=" + extra_data.get('jmmepisodeid') + '&ui_index=' + str(index)
                        if __addon__.getSetting('context_show_play_no_watch') == 'true':
                            context.append(('Play (Do not Mark as Watched (JMM))',
                                            'RunScript(plugin.video.nakamori, %s, %s&cmd=no_mark)'
                                            % (sys.argv[1], url_peep)))
                        if __addon__.getSetting('context_show_info') == 'true':
                            context.append(('More Info', 'Action(Info)'))
                        if __addon__.getSetting('context_show_vote_Series') == 'true':
                            if series_id != '':
                                context.append(
                                    ('Vote for Series (JMM)',
                                     'RunScript(plugin.video.nakamori, %s, %s&cmd=voteSer)'
                                     % (sys.argv[1], url_peep)))
                        if __addon__.getSetting('context_show_vote_Episode') == 'true':
                            if extra_data.get('jmmepisodeid') != '':
                                context.append(
                                    ('Vote for Episode (JMM)',
                                     'RunScript(plugin.video.nakamori, %s, %s&cmd=voteEp)'
                                     % (sys.argv[1], url_peep)))

                        if extra_data.get('jmmepisodeid') != '':
                            if __addon__.getSetting('context_krypton_watched') == 'true':
                                if details.get('playcount', 0) == 0:
                                    context.append(
                                        ('Mark as Watched (JMM)',
                                         'RunScript(plugin.video.nakamori, %s, %s&cmd=watched)'
                                         % (sys.argv[1], url_peep)))
                                else:
                                    context.append(
                                        ('Mark as Unwatched (JMM)',
                                         'RunScript(plugin.video.nakamori, %s, %s&cmd=unwatched)'
                                         % (sys.argv[1], url_peep)))
                            else:
                                context.append(
                                    ('Mark as Watched (JMM)',
                                     'RunScript(plugin.video.nakamori, %s, %s&cmd=watched)'
                                     % (sys.argv[1], url_peep)))
                                context.append(
                                    ('Mark as Unwatched (JMM)',
                                     'RunScript(plugin.video.nakamori, %s, %s&cmd=unwatched)'
                                     % (sys.argv[1], url_peep)))
                    liz.addContextMenuItems(context)
        return xbmcplugin.addDirectoryItem(handle, url, listitem=liz, isFolder=folder)
    except Exception as e:
        error("Error during add_gui_item", str(e))


def remove_anidb_links(data=""):
    """
    Remove anidb links from descriptions
    Args:
        data: the strong to remove links from

    Returns: new string without links

    """
    # search for string with 1 to 3 letters and 1 to 7 numbers
    p = re.compile('http://anidb.net/[a-z]{1,3}[0-9]{1,7}[ ]')
    data2 = p.sub('', data)
    # remove '[' and ']' that included link to anidb.net
    p = re.compile('(\[|\])')
    return p.sub('', data2)


def get_poster(data=""):
    """
    Convert a thumb to a poster if needed and return
    Args:
        data: The url of the image

    Returns: the new url of the image

    """
    if data is not None:
        result = data
        if len(data) > 0 and "getthumb" in data.lower():
            p = data.lower().replace('getthumb', 'getimage')
            s = p.split("/")
            last_word = ""
            for chunk in s:
                last_word = chunk
            result = p.replace(last_word, '')[:-1]
        return result
    return data


def gen_image_url(data=""):
    """
    Perform conversion of url if necessary
    Args:
        data: URL of the image

    Returns: the new URL of the image

    """
    if __addon__.getSetting('useOriginalThumbnailRatio') == 'true':
        ratio = '0'
    else:
        ratio = '1.7778'
    if data is not None:
        if data.startswith("http"):
            if data.endswith("0.6667"):
                data = data.replace("0.6667", ratio)
            elif data.endswith("0,6667"):
                data = data.replace("0,6667", ratio)
            if 'getsupportimage' in data.lower():
                data = data.replace("/0.6667", '')
                data = data.replace("/0,6667", '')
            return data
        if data.endswith("0.6667"):
            return ("http://" + __addon__.getSetting("ipaddress") + ":" + __addon__.getSetting("port")
                    + "/JMMServerREST/GetThumb/" + data).replace("0.6667", ratio)
        elif data.endswith("0,6667"):
            return ("http://" + __addon__.getSetting("ipaddress") + ":" + __addon__.getSetting("port")
                    + "/JMMServerREST/GetThumb/" + data).replace("0,6667", ratio)
        else:
            return ("http://" + __addon__.getSetting("ipaddress") + ":" + __addon__.getSetting("port")
                    + "/JMMServerREST/GetImage/" + data)
    return data


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


def get_legacy_title(data):
    """
    Get the legacy title format
    Args:
        data: the xml node containing the title

    Returns: string of the desired title

    """
    lang = __addon__.getSetting("displaylang")
    title_type = __addon__.getSetting("title_type")
    temp_title = encode(data.get('original_title', 'Unknown'))
    titles = temp_title.split('|')

    try:
        for title in titles:
            stripped = title[title.index('}') + 1:]
            if ('{' + title_type.lower() + ':' + lang.lower() + '}') in title:
                return stripped
        for title in titles:
            # fallback on language
            stripped = title[title.index('}') + 1:]
            if (':' + lang.lower() + '}') in title:
                return stripped
        for title in titles:
            # fallback on x-jat
            stripped = title[title.index('}') + 1:]
            if '{main:x-jat}' in title:
                return stripped
    except:
        pass

    return encode(data.get('title', 'Unknown'))


def get_title(data):
    """
    Get the new title
    Args:
        data: the xml node containing the title

    Returns: string of the desired title

    """
    try:
        if __addon__.getSetting('use_server_title') == 'true':
            return encode(data.get('title', 'Unknown'))
        # xbmc.log(data.get('title', 'Unknown'))
        title = encode(data.get('title', '')).lower()
        if title == 'ova' or title == 'ovas' \
                or title == 'episode' or title == 'episodes' \
                or title == 'special' or title == 'specials' \
                or title == 'parody' or title == 'parodies' \
                or title == 'credit' or title == 'credits' \
                or title == 'trailer' or title == 'trailers' \
                or title == 'other' or title == 'others':
            return encode(data.get('title', 'Error'))
        if data.get('original_title', '') != '':
            return get_legacy_title(data)
        lang = __addon__.getSetting("displaylang")
        title_type = __addon__.getSetting("title_type")
        try:
            for titleTag in data.findall('AnimeTitle'):
                if titleTag.find('Type').text.lower() == title_type.lower():
                    if titleTag.find('Language').text.lower() == lang.lower():
                        return encode(titleTag.find('Title').text)
            # fallback on language any title
            for titleTag in data.findall('AnimeTitle'):
                if titleTag.find('Type').text.lower() != 'short':
                    if titleTag.find('Language').text.lower() == lang.lower():
                        return encode(titleTag.find('Title').text)
            # fallback on x-jat main title
            for titleTag in data.findall('AnimeTitle'):
                if titleTag.find('Type').text.lower() == 'main':
                    if titleTag.find('Language').text.lower() == 'x-jat':
                        return encode(titleTag.find('Title').text)
            # fallback on directory title
            return encode(data.get('title', 'Unknown'))
        except Exception as ex:
            error('Error thrown on getting title', str(ex))
            return encode(data.get('title', 'Error'))
    except Exception as ex:
        error("get_title Exception", str(ex))
        return 'Error'


def get_legacy_tags(tag_xml):
    """
    Get the tags from the legacy style
    Args:
        tag_xml: the xml node containing the tags

    Returns: a string of all of the tags formatted

    """
    temp_genre = ""
    tag = tag_xml.find("Tag")

    if tag is not None:
        temp_genre = tag.get('tag', '')
        temp_genres = str.split(temp_genre, ",")
        temp_genres = TagFilter.processTags(__addon__, temp_genres)
        temp_genre = ""

        for a in temp_genres:
            a = " ".join(w.capitalize() for w in a.split())
            temp_genre = encode(a) if temp_genre == "" else temp_genre + " | " + encode(a)
    return temp_genre


def get_tags(tag_xml):
    """
    Get the tags from the new style
    Args:
        tag_xml: the xml node containing the tags

    Returns: a string of all of the tags formatted

    """
    try:
        if tag_xml.find('Tag') is not None:
            return get_legacy_tags(tag_xml)

        temp_genres = []
        for tag in tag_xml.findall("Genre"):
            if tag is not None:
                temp_genre = encode(tag.get('tag', '')).strip()
                temp_genres.append(temp_genre)
        temp_genres = TagFilter.processTags(__addon__, temp_genres)
        temp_genre = " | ".join(temp_genres)
        return temp_genre
    except Exception as exc:
        error('Error generating tags', str(exc))
        return ''


def get_cast_and_role(data):
    """
    Get cast from the xml
    Args:
        data: xml node containing the cast

    Returns: a list of the cast

    """
    if data is not None:
        result_list = []
        list_cast = []
        list_cast_and_role = []

        character_tag = 'Role'
        if data.find('Characters') is not None:
            data = data.find('Characters')
            character_tag = 'Character'
        for char in data.findall(character_tag):
            # Don't init any variables we don't need right now
            # char_id = char.get('charID')
            if character_tag == 'Role':
                char_charname = char.get('role', '')
            else:
                char_charname = char.get('charname', '')
            # char_picture=char.get('picture','')
            # char_desc=char.get('description','')
            if character_tag == 'Role':
                char_seiyuuname = char.get('seiyuuname', 'Unknown')
            else:
                char_seiyuuname = char.get('tag', 'Unknown')
            # char_seiyuupic=char.get('seiyuupic', 'err404')
            # only add it if it has data
            # reorder these to match the convention (Actor is cast, character is role, in that order)
            if len(char_charname) != 0:
                list_cast.append(str(char_charname))
                if len(char_seiyuuname) != 0:
                    list_cast_and_role.append((str(char_seiyuuname), str(char_charname)))
        result_list.append(list_cast)
        result_list.append(list_cast_and_role)
        return result_list


# Adding items to list/menu:
def build_main_menu():
    """

    """
    xbmcplugin.setContent(handle, content='tvshows')
    try:
        # http://127.0.0.1:8111/jmmserverkodi/getfilters/1
        e = xml(get_xml("http://" + __addon__.getSetting("ipaddress") + ":" + __addon__.getSetting("port") +
                "/jmmserverkodi/getfilters/" + __addon__.getSetting("userid")))
        try:
            for atype in e.findall('Directory'):
                title = atype.get('title')
                use_mode = 4

                key = atype.get('key', '')

                if title == 'Continue Watching (SYSTEM)':
                    title = 'Continue Watching'
                elif title == 'Unsort':
                    title = 'Unsorted'
                    use_mode = 6
                    key = "http://" + __addon__.getSetting("ipaddress") + ":" + __addon__.getSetting("port") \
                          + "/JMMServerKodi/GetMetadata/" + __addon__.getSetting("userid") + "/1/0"

                if __addon__.getSetting("spamLog") == "true":
                    xbmc.log("build_main_menu - key = " + key)

                if __addon__.getSetting('request_nocast') == 'true' and title != 'Unsorted':
                    key += '/nocast'
                url = key

                thumb = gen_image_url(atype.get('thumb'))
                fanart = gen_image_url(atype.get('art', thumb))

                u = sys.argv[0]
                u = set_parameter(u, 'url', url)
                u = set_parameter(u, 'mode', str(use_mode))
                u = set_parameter(u, 'name', urllib.quote_plus(title))

                liz = xbmcgui.ListItem(label=title, label2=title, path=url)
                liz.setArt({'thumb': thumb, 'fanart': fanart, 'poster': get_poster(thumb), 'icon': 'DefaultVideo.png'})
                liz.setInfo(type="Video", infoLabels={"Title": title, "Plot": title})
                xbmcplugin.addDirectoryItem(handle, url=u, listitem=liz, isFolder=True)
        except Exception as e:
            error("Error during build_main_menu", str(e))
    except Exception as e:
        # get_html now catches, so an XML error is the only thing this will catch
        error("Invalid XML Received in build_main_menu", str(e))

    # Start Add_Search
    url = "http://" + __addon__.getSetting("ipaddress") + ":" + __addon__.getSetting("port") \
          + "/jmmserverkodi/search/" + __addon__.getSetting("userid") + "/" + __addon__.getSetting("maxlimit") + "/"
    title = "Search"
    thumb = "http://" + __addon__.getSetting("ipaddress") + ":" + __addon__.getSetting("port") \
            + "/jmmserverkodi/GetSupportImage/plex_others.png"
    liz = xbmcgui.ListItem(label=title, label2=title, path=url)
    liz.setArt({'thumb': thumb, 'poster': get_poster(thumb), 'icon': 'DefaultVideo.png'})
    liz.setInfo(type="Video", infoLabels={"Title": title, "Plot": title})
    u = sys.argv[0]
    u = set_parameter(u, 'url', url)
    u = set_parameter(u, 'mode', str(3))
    u = set_parameter(u, 'name', urllib.quote_plus(title))

    xbmcplugin.addDirectoryItem(handle, url=u, listitem=liz, isFolder=True)
    # End Add_Search
    xbmcplugin.endOfDirectory(handle, True, False, False)


def build_tv_shows(params, extra_directories=None):
    """

    Args:
        params:
        extra_directories:

    Returns:

    """
    # xbmcgui.Dialog().ok('MODE=4','IN')
    xbmcplugin.setContent(handle, 'tvshows')
    if __addon__.getSetting('use_server_sort') == 'false' and extra_directories is None:
        xbmcplugin.addSortMethod(handle, 27)  # video title ignore THE
        xbmcplugin.addSortMethod(handle, 3)  # date
        xbmcplugin.addSortMethod(handle, 18)  # rating
        xbmcplugin.addSortMethod(handle, 17)  # year
        xbmcplugin.addSortMethod(handle, 28)  # by MPAA

    try:
        html = encode(decode(get_xml(params['url'])))
        if __addon__.getSetting("spamLog") == "true":
            xbmc.log(params['url'])
            xbmc.log(html)
        e = xml(html)
        set_window_heading(e)
        try:
            parent_title = ''
            try:
                parent_title = e.get('title1', '')
            except Exception as exc:
                error("Unable to get parent title in buildTVShows", str(exc))

            if extra_directories is not None:
                e.extend(extra_directories)

            directory_list = e.findall('Directory')

            if len(directory_list) <= 0:
                if e.find('Video') is not None:
                    build_tv_episodes(params)
                    return
                error("No directory listing")
            for directory in directory_list:
                temp_genre = get_tags(directory)
                watched = int(directory.get('viewedLeafCount', 0))

                # TODO: Decide about future of cast_and_role in ALL
                # This is not used here because JMM don't present this data because of the size in 'ALL'
                # but we will leave this here to future support if we shrink the data flow
                list_cast = []
                list_cast_and_role = []
                if len(list_cast) == 0:
                    result_list = get_cast_and_role(directory)
                    if result_list is not None:
                        list_cast = result_list[0]
                        list_cast_and_role = result_list[1]

                if __addon__.getSetting("local_total") == "true":
                    total = int(directory.get('totalLocal', 0))
                else:
                    total = int(directory.get('leafCount', 0))
                title = get_title(directory)
                details = {
                    'title': title,
                    'parenttitle': encode(parent_title),
                    'genre': temp_genre,
                    'year': int(directory.get('year', 0)),
                    'episode': total,
                    'season': int(directory.get('season', 1)),
                    # 'count'        : count,
                    # 'size'         : size,
                    # 'Date'         : date,
                    'rating': float(str(directory.get('rating', 0.0)).replace(',', '.')),
                    # 'playcount'    : int(atype.get('viewedLeafCount')),
                    # overlay        : integer (2, - range is 0..8. See GUIListItem.h for values
                    'cast': list_cast,  # cast : list (Michal C. Hall,
                    'castandrole': list_cast_and_role,
                    # This also does nothing. Those gremlins.
                    # 'cast'         : list([("Actor1", "Character1"),("Actor2","Character2")]),
                    # 'castandrole'  : list([("Actor1", "Character1"),("Actor2","Character2")]),
                    # director       : string (Dagur Kari,
                    'mpaa': directory.get('contentRating', ''),
                    'plot': remove_anidb_links(encode(directory.get('summary', ''))),
                    # 'plotoutline'  : plotoutline,
                    'originaltitle': encode(directory.get('original_title', '')),
                    'sorttitle': title,
                    # 'Duration'     : duration,
                    # 'Studio'       : studio, < ---
                    # 'Tagline'      : tagline,
                    # 'Writer'       : writer,
                    # 'tvshowtitle'  : tvshowtitle,
                    'tvshowname': title,
                    # 'premiered'    : premiered,
                    # 'Status'       : status,
                    # code           : string (tt0110293, - IMDb code
                    'aired': directory.get('originallyAvailableAt', ''),
                    # credits        : string (Andy Kaufman, - writing credits
                    # 'Lastplayed'   : lastplayed,
                    'votes': directory.get('votes'),
                    # trailer        : string (/home/user/trailer.avi,
                    'dateadded': directory.get('addedAt')
                }
                temp_date = str(details['aired']).split('-')
                if len(temp_date) == 3:  # format is 2016-01-24, we want it 24.01.2016
                    details['date'] = temp_date[1] + '.' + temp_date[2] + '.' + temp_date[0]

                key = directory.get('key', '')

                thumb = gen_image_url(directory.get('thumb'))
                fanart = gen_image_url(directory.get('art', thumb))

                banner = gen_image_url(directory.get('banner', ''))

                directory_type = directory.get('AnimeType', '')

                extra_data = {
                    'type': 'video',
                    'source': directory_type,
                    'UnWatchedEpisodes': int(details['episode']) - watched,
                    'WatchedEpisodes': watched,
                    'TotalEpisodes': details['episode'],
                    'thumb': thumb,
                    'fanart_image': fanart,
                    'banner': banner,
                    'key': key,
                }
                if __addon__.getSetting('request_nocast') == 'true':
                    key += '/nocast'

                url = key
                set_watch_flag(extra_data, details)
                use_mode = 5
                if __addon__.getSetting("useSeasons") == "false":
                    # this will help when users is using grouping option in jmm which results in series in series
                    if "data/1/2/" in extra_data['key'].lower():
                        use_mode = 4
                u = sys.argv[0]
                u = set_parameter(u, 'url', url)
                u = set_parameter(u, 'mode', str(use_mode))
                context = None
                add_gui_item(u, details, extra_data, context)
        except Exception as e:
            error("Error during build_tv_shows", str(e))
    except Exception as e:
        error("Invalid XML Received in build_tv_shows", str(e))
    xbmcplugin.endOfDirectory(handle)


def build_tv_seasons(params, extra_directories=None):
    """

    Args:
        params:
        extra_directories:

    Returns:

    """
    # xbmcgui.Dialog().ok('MODE=5','IN')
    xbmcplugin.setContent(handle, 'seasons')
    try:
        html = encode(decode(get_xml(params['url'])))
        if __addon__.getSetting("spamLog") == "true":
            xbmc.log(html)
        e = xml(html)
        set_window_heading(e)
        try:
            parent_title = ''
            try:
                parent_title = e.get('title1', '')
            except Exception as exc:
                error("Unable to get parent title in buildTVSeasons", str(exc))

            if extra_directories is not None:
                e.extend(extra_directories)

            if e.find('Directory') is None:
                params['url'] = params['url'].replace('&mode=5', '&mode=6')
                build_tv_episodes(params)
                return

            will_flatten = False

            # check for a single season
            if int(e.get('size', 0)) == 1:
                will_flatten = True

            section_art = gen_image_url(e.get('art', ''))

            set_window_heading(e)

            for atype in e.findall('Directory'):
                key = atype.get('key', '')

                if will_flatten:                    
                    new_params = {'url': key, 'mode': 6}
                    build_tv_episodes(new_params)
                    return

                plot = remove_anidb_links(encode(atype.get('summary', '')))

                temp_genre = get_tags(atype)
                watched = int(atype.get('viewedLeafCount', 0))

                list_cast = []
                list_cast_and_role = []
                if len(list_cast) == 0:
                    result_list = get_cast_and_role(atype)
                    if result_list is not None:
                        list_cast = result_list[0]
                        list_cast_and_role = result_list[1]

                # Create the basic data structures to pass up
                if __addon__.getSetting("local_total") == "true":
                    total = int(atype.get('totalLocal', 0))
                else:
                    total = int(atype.get('leafCount', 0))
                title = get_title(atype)
                details = {
                    'title': title,
                    'parenttitle': encode(parent_title),
                    'tvshowname': title,
                    'sorttitle': encode(atype.get('titleSort', title)),
                    'studio': encode(atype.get('studio', '')),
                    'cast': list_cast,
                    'castandrole': list_cast_and_role,
                    'plot': plot,
                    'genre': temp_genre,
                    'season': int(atype.get('season', 1)),
                    'episode': total,
                    'mpaa': atype.get('contentRating', ''),
                    'rating': float(str(atype.get('rating', 0.0)).replace(',', '.')),
                    'aired': atype.get('originallyAvailableAt', ''),
                    'year': int(atype.get('year', 0))
                }
                temp_date = str(details['aired']).split('-')
                if len(temp_date) == 3:  # format is 2016-01-24, we want it 24.01.2016
                    details['date'] = temp_date[1] + '.' + temp_date[2] + '.' + temp_date[0]

                if atype.get('sorttitle'):
                    details['sorttitle'] = atype.get('sorttitle')

                thumb = gen_image_url(atype.get('thumb'))
                fanart = gen_image_url(atype.get('art', thumb))
                banner = gen_image_url(atype.get('banner', e.get('banner', '')))

                directory_type = atype.get('AnimeType', '')

                extra_data = {
                    'type': 'video',
                    'source': directory_type,
                    'TotalEpisodes': details['episode'],
                    'WatchedEpisodes': watched,
                    'UnWatchedEpisodes': details['episode'] - watched,
                    'thumb': thumb,
                    'fanart_image': fanart,
                    'banner': banner,
                    'key': key,
                    'mode': str(6)
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
            error("Error during build_tv_seasons", str(exc))
    except Exception as exc:
        error("Invalid XML Received in build_tv_seasons", str(exc))
    xbmcplugin.endOfDirectory(handle)


def build_tv_episodes(params):
    # xbmcgui.Dialog().ok('MODE=6','IN')
    """

    :param params:
    :return:
    """
    xbmcplugin.setContent(handle, 'episodes')
    try:
        html = encode(decode(get_xml(params['url'])))
        e = xml(html)
        if __addon__.getSetting("spamLog") == "true":
            xbmc.log(html)
        set_window_heading(e)
        try:
            parent_title = ''
            try:
                parent_title = e.get('title1', '')
            except Exception as exc:
                error("Unable to get parent title in buildTVEpisodes", str(exc))
            if e.find('Directory') is not None:
                # this is never true
                # if e.find('Directory').get('type', 'none') == 'season':
                params['url'] = params['url'].replace('&mode=6', '&mode=5')
                build_tv_seasons(params)
                return
            banner = gen_image_url(e.get('banner', ''))
            art = gen_image_url(e.get('art', ''))

            # unused
            # season_thumb = e.get('thumb', '')

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
            next_episode = 1
            episode_count = 0

            video_list = e.findall('Video')
            if len(video_list) <= 0:
                error("No episodes in list")
            skip = __addon__.getSetting("skipExtraInfoOnLongSeries") == "true" and len(video_list) > int(
                __addon__.getSetting("skipExtraInfoMaxEpisodes"))

            # keep this init out of the loop, as we only provide this once
            list_cast = []
            list_cast_and_role = []
            temp_genre = ""
            parent_key = ""
            grandparent_title = ""
            if not skip:
                for video in video_list:
                    # we only get this once, so only set it if it's not already set
                    if len(list_cast) == 0:
                        result_list = get_cast_and_role(video)
                        if result_list is not None:
                            list_cast = result_list[0]
                            list_cast_and_role = result_list[1]
                        temp_genre = get_tags(video)
                        parent_key = video.get('parentKey', '0')

                        grandparent_title = encode(video.get('grandparentTitle', video.get('grandparentTitle', '')))
            for video in video_list:
                episode_count += 1

                view_offset = video.get('viewOffset', 0)
                # Check for empty duration from MediaInfo check fail and handle it properly
                tmp_duration = video.find('Media').get('duration', '1000')
                if not tmp_duration:
                    duration = 1
                else:
                    duration = int(tmp_duration) / 1000
                # Required listItem entries for XBMC
                details = {
                    'plot': "..." if skip else remove_anidb_links(encode(video.get('summary', ''))),
                    'title': encode(video.get('title', 'Unknown')),
                    'sorttitle': encode(video.get('titleSort', video.get('title', 'Unknown'))),
                    'parenttitle': encode(parent_title),
                    'rating': float(str(video.get('rating', 0.0)).replace(',', '.')),
                    # 'studio'      : episode.get('studio',tree.get('studio','')), 'utf-8') ,
                    # This doesn't work, some gremlins be afoot in this code...
                    # it's probably just that it only applies at series level
                    # 'cast'        : list(['Actor1','Actor2']),
                    # 'castandrole' : list([('Actor1','Character1'),('Actor2','Character2')]),
                    # According to the docs, this will auto fill castandrole
                    'CastAndRole': list_cast_and_role,
                    'Cast': list_cast,
                    # 'director': " / ".join(temp_dir),
                    # 'writer': " / ".join(temp_writer),
                    'genre': "..." if skip else temp_genre,
                    'duration': str(datetime.timedelta(seconds=duration)),
                    'mpaa': video.get('contentRating', ''),
                    'year': int(video.get('year', 0)),
                    'tagline': "..." if skip else temp_genre,
                    'episode': int(video.get('index', 0)),
                    'aired': video.get('originallyAvailableAt', ''),
                    'tvshowtitle': grandparent_title,
                    'votes': int(video.get('votes', 0)),
                    'originaltitle': video.get('original_title', ''),
                    'size': int(video.find('Media').find('Part').get('size', 0)),
                    'season': int(video.get('season', 1))
                }
                temp_date = str(details['aired']).split('-')
                if len(temp_date) == 3:  # format is 2016-01-24, we want it 24.01.2016
                    details['date'] = temp_date[1] + '.' + temp_date[2] + '.' + temp_date[0]

                thumb = gen_image_url(video.get('thumb', ''))

                key = video.get('key', '')

                ext = video.find('Media').find('Part').get('container', '')
                new_key = video.find('Media').find('Part').get('key', '')

                if not key.lower().startswith("http") or 'videolocal' not in key.lower():
                    key = new_key
                    if not key.startswith("http") and 'videolocal' not in key.lower():
                        key = "http://" + __addon__.getSetting("ipaddress") + ":" + \
                              str(int(__addon__.getSetting("port")) + 1) + "/videolocal/0/" + key
                    if '.' + ext.lower() not in key.lower():
                        key += '.'+ext.lower()

                newerkey = encode(video.find('Media').find('Part').get('local_key', ''))
                newerkey = newerkey.replace('\\', '\\\\')
                if newerkey != '' and os.path.isfile(newerkey):
                    key = newerkey

                # Extra data required to manage other properties
                extra_data = dict()
                extra_data['type'] = "Video"
                extra_data['source'] = "tvepisodes"
                extra_data['thumb'] = None if skip else thumb
                extra_data['fanart_image'] = None if skip else art
                extra_data['key'] = key
                extra_data['resume'] = int(int(view_offset) / 1000)
                extra_data['parentKey'] = parent_key
                extra_data['jmmepisodeid'] = video.get('JMMEpisodeId', video.get('GenericId', '0'))
                extra_data['banner'] = banner
                extra_data['xVideoResolution'] = video.find('Media').get('videoResolution', 0)
                extra_data['xVideoCodec'] = video.find('Media').get('videoCodec', '')
                extra_data['xVideoAspect'] = float(video.find('Media').get('aspectRatio', 0))
                extra_data['xAudioCodec'] = video.find('Media').get('audioCodec', '')
                extra_data['xAudioChannels'] = int(video.find('Media').get('audioChannels', 0))

                # Information about streams inside video file
                extra_data['AudioStreams'] = defaultdict(dict)
                extra_data['SubStreams'] = defaultdict(dict)
                for stream_info in video.find('Media').find('Part').findall('Stream'):
                    stream = int(stream_info.get('streamType'))
                    if stream == 1:
                        # Video
                        extra_data['VideoCodec'] = stream_info.get('codec', '')
                        extra_data['width'] = int(stream_info.get('width', 0))
                        extra_data['height'] = int(stream_info.get('height', 0))
                        extra_data['duration'] = duration
                    elif stream == 2:
                        # Audio
                        streams = extra_data.get('AudioStreams')
                        streamid = int(stream_info.get('index'))
                        streams[streamid]['AudioCodec'] = stream_info.get('codec')
                        streams[streamid]['AudioLanguage'] = stream_info.get('languageCode')
                        streams[streamid]['AudioChannels'] = int(stream_info.get('channels'))
                        extra_data['AudioStreams'] = streams
                    elif stream == 3:
                        # Subtitle
                        streams = extra_data.get('SubStreams')
                        streamid = int(stream_info.get('index'))
                        streams[streamid]['SubtitleLanguage'] = stream_info.get('languageCode')
                        extra_data['SubStreams'] = streams
                    else:
                        # error
                        error("Unknown Stream Type Received!")

                # Determine what type of watched flag [overlay] to use
                if int(video.get('viewCount', 0)) > 0:
                    details['playcount'] = 1
                    # details['overlay'] = 5
                else:
                    details['playcount'] = 0
                    # details['overlay'] = 0
                    if next_episode == 1:
                        next_episode = episode_count - 1

                if details['playcount'] == 0:
                    # Hide plot and thumb for unwatched by kodi setting
                    try:
                        parent_setting = xbmc.executeJSONRPC(
                            '{"jsonrpc": "2.0", "method": "Settings.GetSettingValue", "params":' +
                            '{"setting": "videolibrary.showunwatchedplots"}, "id": 1}')
                        # {"id":1,"jsonrpc":"2.0","result":{"value":false}} or true if ".." is displayed on list

                        setting = json.loads(parent_setting)
                        if "result" in setting:
                            if "value" in setting["result"]:
                                if not setting["result"]["value"]:
                                    details['plot'] \
                                        = "Hidden due to user setting.\nCheck Show Plot" + \
                                          " for Unwatched Items in the Video Library Settings."
                                    extra_data['thumb'] = None
                                    extra_data['fanart_image'] = None
                    except Exception as exc:
                        error("jsonrpc_error: " + str(exc))

                context = None
                url = key

                u = sys.argv[0]
                u = set_parameter(u, 'url', url)
                u = set_parameter(u, 'mode', '1')
                u = set_parameter(u, 'file', key)
                u = set_parameter(u, 'ep_id', extra_data.get('jmmepisodeid'))
                u = set_parameter(u, 'ui_index', str(int(episode_count - 1)))

                add_gui_item(u, details, extra_data, context, folder=False, index=int(episode_count - 1))

            # add item to move to next not played item (not marked as watched)
            if __addon__.getSetting("show_continue") == "true":
                if str(parent_title).lower() != "unsort":
                    util.addDir("-continue-", '', '7', "http://" + __addon__.getSetting("ipaddress") + ":"
                                + __addon__.getSetting("port") + "/jmmserverkodi/GetSupportImage/plex_others.png",
                                "2", "3", "4", str(next_episode))

            try:
                parent_setting = xbmc.executeJSONRPC(
                    '{"jsonrpc": "2.0", "method": "Settings.GetSettingValue", "params":' +
                    '{"setting": "videolibrary.tvshowsselectfirstunwatcheditem"}, "id": 1}')
                # {"id":1,"jsonrpc":"2.0","result":{"value":false}} or true if ".." is displayed on list

                setting = json.loads(parent_setting)
                if "result" in setting:
                    if "value" in setting["result"]:
                        if int(setting["result"]["value"]) > 0:
                            try:
                                new_window = xbmcgui.Window(xbmcgui.getCurrentWindowId())
                                new_control = new_window.getControl(new_window.getFocusId())
                                move_position_on_list(new_control, next_episode)
                            except:
                                pass
            except Exception as exc:
                error("jsonrpc_error: " + str(exc))
        except Exception as exc:
            error("Error during build_tv_episodes", str(exc))
    except Exception as exc:
        error("Invalid XML Received in build_tv_episodes", str(exc))
    xbmcplugin.endOfDirectory(handle)


def build_search(url=''):
    """
    Build directory list of series containing searched query
    Args:
        url: url pointing to search api

    Returns: build_tv_shows out of search query

    """
    try:
        term = util.searchBox()
        if term is not None and term != "":
            try:
                term = term.replace(' ', '%20').replace("'", '%27').replace('?', '%3F')
                to_send = {'url': url + term}
                url2 = "http://" + __addon__.getSetting("ipaddress") + ":" + __addon__.getSetting("port") \
                       + "/jmmserverkodi/searchtag/" + __addon__.getSetting("userid") + "/" + \
                       __addon__.getSetting("maxlimit_tag") + "/"
                e = xml(encode(get_xml(url2 + term)))
                directories = e.findall('Directory')
                if len(directories) <= 0:
                    directories = None
                build_tv_shows(to_send, directories)
            except Exception as exc:
                error("Error during build_search", str(exc))
    except Exception as exc:
        error("Error during searchBox", str(exc))


# Other functions
def play_video(url, ep_id):
    """

    Args:
        url:
        ep_id:

    Returns:

    """
    details = {
        'plot': xbmc.getInfoLabel('ListItem.Plot'),
        'title': xbmc.getInfoLabel('ListItem.Title'),
        'sorttitle': xbmc.getInfoLabel('ListItem.Title'),
        'rating': xbmc.getInfoLabel('ListItem.Rating'),
        'duration': xbmc.getInfoLabel('ListItem.Duration'),
        'mpaa': xbmc.getInfoLabel('ListItem.Mpaa'),
        'year': xbmc.getInfoLabel('ListItem.Year'),
        'tagline': xbmc.getInfoLabel('ListItem.Tagline'),
        'episode': xbmc.getInfoLabel('ListItem.Episode'),
        'aired': xbmc.getInfoLabel('ListItem.Premiered'),
        'tvshowtitle': xbmc.getInfoLabel('ListItem.TVShowTitle'),
        'votes': xbmc.getInfoLabel('ListItem.Votes'),
        'originaltitle': xbmc.getInfoLabel('ListItem.OriginalTitle'),
        'size': xbmc.getInfoLabel('ListItem.Size'),
        'season': xbmc.getInfoLabel('ListItem.Season')
    }

    item = xbmcgui.ListItem(details.get('title', 'Unknown'), thumbnailImage=xbmc.getInfoLabel('ListItem.Thumb'),
                            path=url)
    item.setInfo(type='Video', infoLabels=details)
    item.setProperty('IsPlayable', 'true')
    try:
        # jmmserverkodi/getmetadata/userid/type (5 is episode)/ep_id
        episode_xml_url = "http://" + __addon__.getSetting("ipaddress") + ":" + __addon__.getSetting("port") + \
                          "/jmmserverkodi/getmetadata/" + __addon__.getSetting("userid") + "/5/" + str(ep_id)
        html = get_xml(encode(episode_xml_url))
        if __addon__.getSetting("spamLog") == "true":
            xbmc.log(html)
        e = xml(html)
        video_list = e.findall('Video')
        for video in video_list:
            tmp_duration = video.find('Media').get('duration', '1000')
            if not tmp_duration:
                duration = 1
            else:
                duration = int(tmp_duration) / 1000
            # Information about streams inside video file
            for stream_info in video.find('Media').find('Part').findall('Stream'):
                stream = int(stream_info.get('streamType'))
                if stream == 1:
                    # Video
                    video_codec = dict()
                    video_codec['codec'] = stream_info.get('codec', '')
                    video_codec['width'] = int(stream_info.get('width', 0))
                    video_codec['height'] = int(stream_info.get('height', 0))
                    video_codec['duration'] = duration
                    item.addStreamInfo('video', video_codec)
                elif stream == 2:
                    # Audio
                    audio_codec = dict()
                    audio_codec['codec'] = stream_info.get('codec')
                    audio_codec['language'] = stream_info.get('languageCode')
                    audio_codec['channels'] = int(stream_info.get('channels'))
                    item.addStreamInfo('audio', audio_codec)
                elif stream == 3:
                    # Subtitle
                    subtitle_codec = dict()
                    subtitle_codec['language'] = stream_info.get('languageCode')
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


def vote_series(params):
    """

    Args:
        params: must contain anime_id

    Returns:

    """
    vote_list = ['Don\'t Vote', '10', '9', '8', '7', '6', '5', '4', '3', '2', '1', '0']
    my_vote = xbmcgui.Dialog().select('my_vote', vote_list)
    if my_vote == -1:
        return
    elif my_vote != 0:
        vote_value = str(vote_list[my_vote])
        vote_type = str(1)
        series_id = params['anime_id']
        get_xml("http://" + __addon__.getSetting("ipaddress") + ":" + __addon__.getSetting("port")
                + "/jmmserverkodi/vote/" + __addon__.getSetting("userid") + "/" + series_id + "/" +
                vote_value + "/" + vote_type)
        xbmc.executebuiltin("XBMC.Notification(%s, %s %s, 7500, %s)" % (
            'Vote saved', 'You voted', vote_value, __addon__.getAddonInfo('icon')))


def vote_episode(params):
    """

    Args:
        params:

    Returns:

    """
    vote_list = ['Don\'t Vote', '10', '9', '8', '7', '6', '5', '4', '3', '2', '1', '0']
    my_vote = xbmcgui.Dialog().select('my_vote', vote_list)
    if my_vote == -1:
        return
    elif my_vote != 0:
        vote_value = str(vote_list[my_vote])
        vote_type = str(4)
        ep_id = params['ep_id']
        get_xml("http://" + __addon__.getSetting("ipaddress") + ":" + __addon__.getSetting(
            "port") + "/jmmserverkodi/vote/" + __addon__.getSetting(
            "userid") + "/" + ep_id + "/" + vote_value + "/" + vote_type)
        xbmc.executebuiltin("XBMC.Notification(%s, %s %s, 7500, %s)" % (
            'Vote saved', 'You voted', vote_value, __addon__.getAddonInfo('icon')))


def watched_mark(params):
    """

    Args:
        params:
    """
    episode_id = params.get('ep_id', '')
    anime_id = params.get('anime_id', '')
    group_id = params.get('group_id', '')
    watched = bool(params['watched'])
    if watched is True:
        watched_msg = "watched"
    else:
        watched_msg = "unwatched"

    key = ""
    if episode_id != '':
        key = "http://" + __addon__.getSetting("ipaddress") + ":" + __addon__.getSetting("port") \
              + "/jmmserverkodi/watch/" + __addon__.getSetting("userid") + "/" + episode_id + "/" + str(watched).strip()
    elif anime_id != '':
        key = "http://" + __addon__.getSetting("ipaddress") + ":" + __addon__.getSetting("port") \
              + "/jmmserverkodi/watchseries/" + __addon__.getSetting("userid") + "/" + anime_id + "/" + str(watched).strip()
    elif group_id != '':
        key = "http://" + __addon__.getSetting("ipaddress") + ":" + __addon__.getSetting("port") \
              + "/jmmserverkodi/watchgroup/" + __addon__.getSetting("userid") + "/" + group_id + "/" + str(watched).strip()
    if __addon__.getSetting('log_spam') == 'true':
        xbmc.log('epid: ' + str(episode_id))
        xbmc.log('anime_id: ' + str(anime_id))
        xbmc.log('group_id: ' + str(group_id))
        xbmc.log('key: ' + key)

    sync = __addon__.getSetting("syncwatched")
    if sync == "true":
        get_xml(key)

    box = __addon__.getSetting("watchedbox")
    if box == "true":
        xbmc.executebuiltin("XBMC.Notification(%s, %s %s, 2000, %s)" % (
            'Watched status changed', 'Mark as ', watched_msg, __addon__.getAddonInfo('icon')))
    refresh()


# Setting up Remote Debug
if __addon__.getSetting('remote_debug') == 'true':
    try:
        if pydevd:
            pydevd.settrace(__addon__.getSetting('ide_ip'), port=int(__addon__.getSetting('ide_port')),
                            stdoutToServer=True, stderrToServer=True, suspend=False)
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
            try:
                win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
                ctl = win.getControl(win.getFocusId())
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
    else:
        if mode == 1:  # VIDEO
            # xbmcgui.Dialog().ok('MODE=1','MODE')
            try:
                win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
                ctl = win.getControl(win.getFocusId())
                if play_video(parameters['file'], parameters['ep_id']) != 0:
                    ui_index = parameters.get('ui_index', '')
                    if ui_index != '':
                        move_position_on_list(ctl, int(ui_index) + 1)
                    parameters['watched'] = True
                    watched_mark(parameters)
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
            build_tv_shows(parameters)
        elif mode == 5:  # TVSeasons
            # xbmcgui.Dialog().ok('MODE=5','MODE')
            build_tv_seasons(parameters)
        elif mode == 6:  # TVEpisodes
            # xbmcgui.Dialog().ok('MODE=6','MODE')
            build_tv_episodes(parameters)
        elif mode == 7:  # Playlist -continue-
            # xbmcgui.Dialog().ok('MODE=7','MODE')
            play_continue_item()
        else:
            build_main_menu()
else:
    error("Incorrect Credentials", "Please change in Settings")
if __addon__.getSetting('remote_debug') == 'true':
    try:
        if pydevd:
            pydevd.stoptrace()
    except Exception as remote_exc:
        xbmc.log(str(remote_exc))
        pass
