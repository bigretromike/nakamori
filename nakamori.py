#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import os
import re
import sys
import traceback
import urllib
import xml.etree.ElementTree as Tree

import urllib2

import resources.lib.TagBlacklist as TagFilter
import resources.lib.util as util
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
from StringIO import StringIO
import gzip

handle = int(sys.argv[1])
addon = xbmcaddon.Addon(id='plugin.video.nakamori')


# Internal function
def get_html(url, referer):

    # hacky fix for common url issues in 3.6, feel free to add to it
    if not url.lower().startswith("http://" + addon.getSetting("ipaddress") + ":" \
            + addon.getSetting("port") + "/jmmserverkodi/"):
        if url.lower().startswith(':' + addon.getSetting("port")):
            url = 'http://' + addon.getSetting("ipaddress") + url

    referer = urllib2.quote(referer.encode('utf-8')).replace("%3A", ":").replace("%2f", "/")
    req = urllib2.Request(url.encode('utf-8'))
    if len(referer) > 1:
        req.add_header('Referer', referer)
    use_gzip = addon.getSetting("use_gzip")
    if use_gzip == "true":
        req.add_header('Accept-encoding', 'gzip')
    data = None
    try:
        response = urllib2.urlopen(req, timeout=int(addon.getSetting('timeout')))
        if response.info().get('Content-Encoding') == 'gzip':
            try:
                buf = StringIO(response.read())
                f = gzip.GzipFile(fileobj=buf)
                data = f.read()
            except Exception as e:
                error('Decompresing gzip respond failed', str(e))
        else:
            data = response.read()
        response.close()
    except Exception as e:
        xbmc.log('There was an error retrieving url: ' + url)
        error('Connection Failed', str(e))
    return data


def xml(xmlstring):
    e = Tree.XML(xmlstring)
    if e.get('ErrorString','') != '':
        error(e.get('ErrorString'), 'JMM Error', 'JMM Error')
    return e


def set_window_heading(var_tree):
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
    #xbmc.executebuiltin("XBMC.Notification(%s, %s %s, 2000, %s)" % ('ERROR', ' ', 'Running filter tags', addon.getAddonInfo('icon')))
    str1 = [title]
    str1 = TagFilter.processTags(addon,str1)
    return len(str1) > 0


def add_gui_item(url, details, extra_data, context=None, folder=True):
    try:
        tbi = ""
        tp = 'Video'
        link_url = ""

        # do this before so it'll log
        # use the year as a fallback in case the date is unavailable
        if details.get('date', '') == '':
            if details.get('year', '') != '' and details['year'] != 0:
                details['date'] = '01.01.'+str(details['year'])
                details['aired'] = details['date']
                #details['aired'] = str(details['year'])+'-01-01'

        if addon.getSetting("spamLog") == 'true':
            if details is not None:
                xbmc.log("add_gui_item - details", xbmc.LOGWARNING)
                for i in details:
                    temp_log = ""
                    a = details.get(i.encode('utf-8'))
                    if a is None:
                        temp_log = "\'unset\'"
                    elif isinstance(a, list):
                        for b in a:
                            temp_log = str(b) if temp_log == "" else temp_log + " | " + str(b)
                    else:
                        temp_log = str(a)
                    xbmc.log("-" + str(i) + "- " + temp_log, xbmc.LOGWARNING)
            if extra_data is not None:
                xbmc.log("add_gui_item - extra_data", xbmc.LOGWARNING)
                for i in extra_data:
                    temp_log = ""
                    a = extra_data.get(i.encode('utf-8'))
                    if a is None:
                        temp_log = "\'unset\'"
                    elif isinstance(a, list):
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
        if details.get('parenttitle','').lower() == 'tags':
            if not filter_gui_item_by_tag(details.get('title','')):
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
                    if extra_data.get('duration'):
                        video_codec['duration'] = extra_data.get('duration')

                    audio_codec = {}
                    if extra_data.get('AudioCodec'):
                        audio_codec['codec'] = extra_data.get('AudioCodec')
                    if extra_data.get('AudioChannels'):
                        audio_codec['channels'] = int(extra_data.get('AudioChannels'))
                    if extra_data.get('AudioLanguage'):
                        audio_codec['language'] = extra_data.get('AudioLanguage')

                    liz.addStreamInfo('video', video_codec)
                    liz.addStreamInfo('audio', audio_codec)
            # UMS/PSM Jumpy plugin require 'path' to play video
            partemp = util.parseParameters(inputString=url)
            liz.setProperty('path', str(partemp.get('file', 'empty')))

        if extra_data and len(extra_data) > 0:
            if extra_data.get('source') == 'tvshows' or extra_data.get('source') == 'tvseasons':
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
                # TODO: We support this with JMM Patch or drop this (i prefer support)
                # We probably don't use those (second is probably custom)
                if extra_data.get('banner'):
                    liz.setArt({'banner': extra_data.get('banner', '')})
                if extra_data.get('season_thumb'):
                    liz.setArt({'seasonThumb': extra_data.get('season_thumb', '')})

        if context is None:
            if extra_data and len(extra_data) > 0:
                if extra_data.get('type', 'video').lower() == "video":
                    context = []
                    url_peep = sys.argv[2]
                    # Always allow 'More Info' to be executed. Some places have more info than others
                    context.append(('More Info', 'Action(Info)'))
                    if extra_data.get('source', 'none') == 'tvshows':
                        url_peep = url_peep + "&anime_id=" + extra_data.get('key') + "&cmd=voteSer"
                        context.append(('Vote', 'RunScript(plugin.video.nakamori, %s, %s)' % (sys.argv[1], url_peep)))
                    elif extra_data.get('source', 'none') == 'tvepisodes':
                        url_peep = url_peep + "&anime_id=" + extra_data.get('parentKey') + "&ep_id=" \
                                   + extra_data.get('jmmepisodeid')
                        context.append(('Vote for Series', 'RunScript(plugin.video.nakamori, %s, %s&cmd=voteSer)' % (
                            sys.argv[1], url_peep)))
                        context.append(('Vote for Episode', 'RunScript(plugin.video.nakamori, %s, %s&cmd=voteEp)' % (
                            sys.argv[1], url_peep)))
                        context.append(('Mark as Watched', 'RunScript(plugin.video.nakamori, %s, %s&cmd=watched)' % (
                            sys.argv[1], url_peep)))
                        context.append(('Mark as Unwatched', 'RunScript(plugin.video.nakamori, %s, %s&cmd=unwatched)' %
                                        (sys.argv[1], url_peep)))
                    liz.addContextMenuItems(context)
        return xbmcplugin.addDirectoryItem(handle, url, listitem=liz, isFolder=folder)
    except Exception as e:
        error("Error during add_gui_item", str(e))


def valid_user():
    e = xml(
        get_html("http://" + addon.getSetting("ipaddress") + ":" + addon.getSetting("port") +
                 "/jmmserverkodi/getusers", ""))
    valid = False
    for atype in e.findall('User'):
        user_id = atype.get('id')
        if user_id == addon.getSetting("userid"):
            valid = True
    return valid


def error(msg, error_msg="Generic", error_type='Error'):
    xbmc.log('---' + msg + '---', xbmc.LOGERROR)
    try:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        xbmc.log(str(exc_type) + " at line " + str(exc_tb.tb_lineno) + " in file " + str(
                os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]) + " : " + str(error_msg), xbmc.LOGERROR)
        traceback.print_exc()
    except Exception as e:
        xbmc.log("There was an error catching the error. WTF.", xbmc.LOGERROR)
        xbmc.log("There error message: ", str(e))
        traceback.print_exc()

    xbmc.executebuiltin("XBMC.Notification(%s, %s %s, 2000, %s)" % (error_type, ' ', msg, addon.getAddonInfo('icon')))


def remove_html(data=""):
    # search for string with 1 to 3 letters and 1 to 7 numbers
    p = re.compile('http://anidb.net/[a-z]{1,3}[0-9]{1,7}[ ]')
    data2 = p.sub('', data)
    # remove '[' and ']' that included link to anidb.net
    p = re.compile('(\[|\])')
    return p.sub('', data2)


def get_poster(data=""):
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
    if data is not None:
        if data.startswith("http"):
            return data
        if data.endswith("0.6667"):
            return "http://" + addon.getSetting("ipaddress") + ":" + addon.getSetting("port") \
                   + "/JMMServerREST/GetThumb/" + data
        else:
            return "http://" + addon.getSetting("ipaddress") + ":" + addon.getSetting("port") \
                   + "/JMMServerREST/GetImage/" + data
    return data


def set_watch_flag(extra_data, details):
    # TODO: Real watch progress instead of 0,50,100%
    # Set up overlays for watched and unwatched episodes
    if extra_data['WatchedEpisodes'] == 0:
        details['playcount'] = 0
    elif extra_data['UnWatchedEpisodes'] == 0:
        details['playcount'] = 1
    else:
        extra_data['partialTV'] = 1


def get_legacy_title(data):
    lang = addon.getSetting("displaylang")
    type = addon.getSetting("title_type")
    temptitle = unicode(data.get('original_title', 'Unknown'))
    titles = temptitle.split('|')

    try:
        for title in titles:
            stripped = title[title.index('}') + 1:]
            if ('{' + type.lower() + ':' + lang.lower() + '}') in title:
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

    return data.get('title', 'Unknown').encode('utf-8')


def get_title(data):
    try:
        if addon.getSetting('use_server_title') == 'true':
            return data.get('title', 'Unknown').encode('utf-8')
        #xbmc.log(data.get('title', 'Unknown'))
        title = unicode(data.get('title', '')).lower()
        if title == 'ova' or title == 'ovas' \
                or title == 'episode' or title == 'episodes' \
                or title == 'special' or title == 'specials' \
                or title == 'parody' or title == 'parodies' \
                or title == 'credit' or title == 'credits' \
                or title == 'trailer' or title == 'trailers' \
                or title == 'other' or title == 'others':
            return data.get('title','Error').encode('utf-8')
        if data.get('original_title', '') != '':
            return get_legacy_title(data)
        lang = addon.getSetting("displaylang")
        type = addon.getSetting("title_type")
        try:
            for titleTag in data.findall('AnimeTitle'):
                if titleTag.find('Type').text.lower() == type.lower():
                    if titleTag.find('Language').text.lower() == lang.lower():
                        return titleTag.find('Title').text.encode('utf-8')
            # fallback on language any title
            for titleTag in data.findall('AnimeTitle'):
                if titleTag.find('Language').text.lower() == lang.lower():
                    return titleTag.find('Title').text.encode('utf-8')
            # fallback on x-jat main title
            for titleTag in data.findall('AnimeTitle'):
                if titleTag.find('Type').text.lower() == 'main':
                    if titleTag.find('Language').text.lower() == 'x-jat':
                        return titleTag.find('Title').text.encode('utf-8')
            # fallback on directory title
            return data.get('title', 'Unknown').encode('utf-8')
        except:
            error('Error thrown on getting title')
            return data.get('title','Error').encode('utf-8')
    except Exception as e:
        error("get_title Exception", str(e))
        return 'Error'


def get_legacy_tags(atype):
    tempgenre = ""
    tag = atype.find("Tag")

    if tag is not None:
        tempgenre = tag.get('tag', '')
        temp_genres = str.split(tempgenre, ",")
        temp_genres = TagFilter.processTags(addon, temp_genres)
        tempgenre = ""

        for a in temp_genres:
            a = " ".join(w.capitalize() for w in a.split())
            tempgenre = unicode(a, 'utf8') if tempgenre == "" else tempgenre + " | " + unicode(a, 'utf8')
    return tempgenre

	
def get_tags(atype):
    tempgenre = ""
    try:
        if atype.find('Tag') is not None:
            return get_legacy_tags(atype)

        temp_genres = []
        for tag in atype.findall("Genre"):
            if tag is not None:
                tempgenre = tag.get('tag', '').encode('utf-8').strip()
                temp_genres.append(tempgenre)
                tempgenre = ""
        temp_genres = TagFilter.processTags(addon, temp_genres)
        tempgenre = " | ".join(temp_genres)
        return tempgenre
    except:
        error('Error generating tags')
        return ''

		
def get_cast_and_role(data):
    if data is not None:
        result_list = []
        list_cast = []
        list_cast_and_role = []

        characterTag = 'Role'
        if data.find('Characters') is not None:
            data = data.find('Characters')
            characterTag = 'Character'
        for char in data.findall(characterTag):
            # Don't init any variables we don't need right now
            # char_id = char.get('charID')
            if characterTag == 'Role':
                char_charname = char.get('role', '')
            else:
                char_charname = char.get('charname', '')
            # char_picture=char.get('picture','')
            # char_desc=char.get('description','')
            if characterTag == 'Role':
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
    xbmcplugin.setContent(handle, content='tvshows')
    try:
        # http://127.0.0.1:8111/jmmserverkodi/getfilters/1
        e = xml(get_html("http://" + addon.getSetting("ipaddress") + ":" + addon.getSetting("port") +
                              "/jmmserverkodi/getfilters/" + addon.getSetting("userid"), ""))
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
                    if key[-1] == '/':
                        key = key[:-1]

                if not key.startswith("http"):
                    key = "http://" + addon.getSetting("ipaddress") + ":" + addon.getSetting("port") \
                          + "/JMMServerKodi/GetMetadata/" + addon.getSetting("userid") + "/" + key
                if addon.getSetting("spamLog") == "true":
                    xbmc.log("build_main_menu - key = " + key)
                url = key

                thumb = gen_image_url(atype.get('thumb'))
                fanart = gen_image_url(atype.get('art', thumb))

                u = sys.argv[0] + "?url=" + url + "&mode=" + str(use_mode) + "&name=" + urllib.quote_plus(title)
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
    url = "http://" + addon.getSetting("ipaddress") + ":" + addon.getSetting("port") \
          + "/jmmserverkodi/search/" + addon.getSetting("userid") + "/" + addon.getSetting("maxlimit") + "/"
    title = "Search"
    thumb = "http://" + addon.getSetting("ipaddress") + ":" + addon.getSetting("port") \
            + "/jmmserverkodi/GetSupportImage/plex_others.png"
    liz = xbmcgui.ListItem(label=title, label2=title, path=url)
    liz.setArt({'thumb': thumb, 'poster': get_poster(thumb), 'icon': 'DefaultVideo.png'})
    liz.setInfo(type="Video", infoLabels={"Title": title, "Plot": title})
    u = sys.argv[0] + "?url=" + url + "&mode=" + str(3) + "&name=" + urllib.quote_plus(title)
    xbmcplugin.addDirectoryItem(handle, url=u, listitem=liz, isFolder=True)
    # End Add_Search
    xbmcplugin.endOfDirectory(handle, True, False, False)


def build_tv_shows(params):
    # xbmcgui.Dialog().ok('MODE=4','IN')
    xbmcplugin.setContent(handle, 'tvshows')
    if addon.getSetting('use_server_sort') == 'false':
        xbmcplugin.addSortMethod(handle, 27)  # video title ignore THE
        xbmcplugin.addSortMethod(handle, 3)  # date
        xbmcplugin.addSortMethod(handle, 18)  # rating
        xbmcplugin.addSortMethod(handle, 17)  # year
        xbmcplugin.addSortMethod(handle, 28)  # by MPAA

    try:
        html = get_html(params['url'], '').decode('utf-8').encode('utf-8')
        if addon.getSetting("spamLog") == "true":
            xbmc.log(params['url'])
            xbmc.log(html)
        e = xml(html)
        set_window_heading(e)
        try:
            parent_title=''
            try:
                parent_title=e.get('title1', '')
            except Exception:
                error("Unable to get parent title in buildTVShows")

            directory_list = e.findall('Directory')
            if len(directory_list) <= 0:
                if e.find('Video') is not None:
                    build_tv_episodes(params)
                    return
                error("No directory listing")
            for atype in directory_list:
                tempgenre = get_tags(atype)
                watched = int(atype.get('viewedLeafCount', 0))

                # TODO: Decide about future of cast_and_role in ALL
                # This is not used here because JMM don't present this data because of the size in 'ALL'
                # but we will leave this here to future support if we shrink the data flow
                list_cast = []
                list_cast_and_role = []
                if len(list_cast) == 0:
                    result_list = get_cast_and_role(atype)
                    if result_list is not None:
                        list_cast = result_list[0]
                        list_cast_and_role = result_list[1]

                if addon.getSetting("local_total") == "true":
                    total = int(atype.get('totalLocal', 0))
                else:
                    total = int(atype.get('leafCount', 0))
                title = get_title(atype)
                details = {
                    'title': title,
                    'parenttitle': parent_title.encode('utf-8'),
                    'genre': tempgenre,
                    'year': int(atype.get('year', 0)),
                    'episode': total,
                    'season': int(atype.get('season', 0)),
                    # 'count'        : count,
                    # 'size'         : size,
                    # 'Date'         : date,
                    'rating': float(str(atype.get('rating', 0))),
                    # 'playcount'    : int(atype.get('viewedLeafCount')),
                    # overlay        : integer (2, - range is 0..8. See GUIListItem.h for values
                    'cast': list_cast,  # cast : list (Michal C. Hall,
                    'castandrole': list_cast_and_role,
                    # This also does nothing. Those gremlins.
                    # 'cast'         : list([("Actor1", "Character1"),("Actor2","Character2")]),
                    # 'castandrole'  : list([("Actor1", "Character1"),("Actor2","Character2")]),
                    # director       : string (Dagur Kari,
                    'mpaa': atype.get('contentRating', ''),
                    'plot': remove_html(atype.get('summary', '').encode('utf-8')),
                    # 'plotoutline'  : plotoutline,
                    'originaltitle': atype.get('original_title', '').encode("utf-8"),
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
                    'aired': atype.get('originallyAvailableAt', ''),
                    # credits        : string (Andy Kaufman, - writing credits
                    # 'Lastplayed'   : lastplayed,
                    'votes': atype.get('votes'),
                    # trailer        : string (/home/user/trailer.avi,
                    'dateadded': atype.get('addedAt')
                }
                tempdate = str(details['aired']).split('-')
                if len(tempdate) == 3:  # format is 2016-01-24, we want it 24.01.2016
                    details['date'] = tempdate[1] + '.' + tempdate[2] + '.' + tempdate[0]

                key = atype.get('key', '')
                if not key.startswith("http") and not 'jmmserverkodi' in key.lower():
                    key = "http://" + addon.getSetting("ipaddress") + ":" + addon.getSetting("port") \
                          + "/JMMServerKodi/GetMetadata/" + addon.getSetting("userid") + "/" + key
                thumb = gen_image_url(atype.get('thumb'))
                fanart = gen_image_url(atype.get('art', thumb))

                # TODO: we really should fix banners. JMM doesn't send them...
                banner = gen_image_url(e.get('banner', ''))

                extra_data = {
                    'type': 'video',
                    'source': 'tvshows',
                    'UnWatchedEpisodes': int(details['episode']) - watched,
                    'WatchedEpisodes': watched,
                    'TotalEpisodes': details['episode'],
                    'thumb': thumb,
                    'fanart_image': fanart,
                    'banner': banner,
                    'key': key,
                    'ratingKey': str(atype.get('ratingKey', 0))
                    }
                url = key
                set_watch_flag(extra_data, details)
                use_mode = 5
                if addon.getSetting("useSeasons") == "false":
                    # this will help when users is using grouping option in jmm which results in series in series
                    if "data/1/2/" in extra_data['key'].lower():
                        use_mode = 4
                u = sys.argv[0] + "?url=" + url + "&mode=" + str(use_mode)
                context = None
                add_gui_item(u, details, extra_data, context)
        except Exception as e:
            error("Error during build_tv_shows", str(e))
    except Exception as e:
        error("Invalid XML Received in build_tv_shows", str(e))
    xbmcplugin.endOfDirectory(handle)


def build_tv_seasons(params):
    # xbmcgui.Dialog().ok('MODE=5','IN')
    xbmcplugin.setContent(handle, 'seasons')
    try:
        html = get_html(params['url'], '').decode('utf-8').encode('utf-8')
        if addon.getSetting("spamLog") == "true":
            xbmc.log(html)
        e = xml(html)
        set_window_heading(e)
        try:
            parent_title=''
            try:
                parent_title = e.get('title1', '')
            except Exception:
                error("Unable to get parent title in buildTVSeasons")
            if e.find('Directory') is None:
                params['url'] = params['url'].replace('&mode=5', '&mode=6')
                build_tv_episodes(params)
                return

            will_flatten = False
            # check for a single season
            if int(e.get('size', 0)) == 1:
                will_flatten = True

            sectionart = gen_image_url(e.get('art', ''))
            banner = gen_image_url(e.get('banner', ''))

            set_window_heading(e)
            # For all the directory tags

            if will_flatten:
                url = key
                u = sys.argv[0] + "?url=" + url + "&mode=" + str(6)
                build_tv_episodes(u)
                return

            directory_list = e.findall('Directory')
            if len(directory_list) <= 0:
                if e.find('Video') is not None:
                    url = key
                    u = sys.argv[0] + "?url=" + url + "&mode=" + str(6)
                    build_tv_episodes(u)
                    return
                error("No directory listings")
            for atype in directory_list:
                key = atype.get('key', '')
                if not key.startswith("http") and not 'jmmserverkodi' in key.lower():
                    key = "http://" + addon.getSetting("ipaddress") + ":" + addon.getSetting("port") \
                          + "/JMMServerKodi/GetMetadata/" + addon.getSetting("userid") + "/" + key

                plot = remove_html(atype.get('summary', '').encode('utf-8'))

                tempgenre = get_tags(atype)
                watched = int(atype.get('viewedLeafCount', 0))

                list_cast = []
                list_cast_and_role = []
                if len(list_cast) == 0:
                    result_list = get_cast_and_role(atype)
                    if result_list is not None:
                        list_cast = result_list[0]
                        list_cast_and_role = result_list[1]

                # Create the basic data structures to pass up
                if addon.getSetting("local_total") == "true":
                    total = int(atype.get('totalLocal', 0))
                else:
                    total = int(atype.get('leafCount', 0))
                title = get_title(atype)
                details = {
                    'title': title,
                    'parenttitle': parent_title.encode('utf-8'),
                    'tvshowname': title,
                    'sorttitle': atype.get('titleSort', title).encode('utf-8'),
                    'studio': atype.get('studio', '').encode('utf-8'),
                    'cast': list_cast,
                    'castandrole': list_cast_and_role,
                    'plot': plot,
                    'genre': tempgenre,
                    'season': int(atype.get('season', 0)),
                    'episode': total,
                    'mpaa': atype.get('contentRating', ''),
                    'rating': atype.get('rating'),
                    'aired': atype.get('originallyAvailableAt', ''),
                    'year': int(atype.get('year', 0))
                    }
                tempdate = str(details['aired']).split('-')
                if len(tempdate) == 3:  # format is 2016-01-24, we want it 24.01.2016
                    details['date'] = tempdate[1] + '.' + tempdate[2] + '.' + tempdate[0]

                if atype.get('sorttitle'):
                    details['sorttitle'] = atype.get('sorttitle')

                thumb = gen_image_url(atype.get('thumb'))
                fanart = gen_image_url(atype.get('art', thumb))

                extra_data = {
                    'type': 'video',
                    'source': 'tvseasons',
                    'TotalEpisodes': details['episode'],
                    'WatchedEpisodes': watched,
                    'UnWatchedEpisodes': details['episode'] - watched,
                    'thumb': thumb,
                    'fanart_image': fanart,
                    'key': key,
                    'ratingKey': str(atype.get('ratingKey', 0)),  # TODO: Do we need ratingKey ?
                    'mode': str(6)
                    }

                if banner:
                    extra_data['banner'] = banner

                if extra_data['fanart_image'] == "":
                    extra_data['fanart_image'] = sectionart

                set_watch_flag(extra_data, details)

                url = sys.argv[0] + "?url=" + extra_data['key'] + "&mode=" + str(6)
                context = None

                # Build the screen directory listing
                add_gui_item(url, details, extra_data, context)

            if addon.getSetting('use_server_sort') == 'false':
                # Apparently date sorting in Kodi has been broken for years
                xbmcplugin.addSortMethod(handle, 17)  # year
                xbmcplugin.addSortMethod(handle, 27)  # video title ignore THE
                xbmcplugin.addSortMethod(handle, 3)  # date
                xbmcplugin.addSortMethod(handle, 18)  # rating
                xbmcplugin.addSortMethod(handle, 28)  # by MPAA

        except Exception as e:
            error("Error during build_tv_seasons", str(e))
    except Exception as e:
        error("Invalid XML Received in build_tv_seasons", str(e))
    xbmcplugin.endOfDirectory(handle)


def build_tv_episodes(params):
    # xbmcgui.Dialog().ok('MODE=6','IN')
    xbmcplugin.setContent(handle, 'episodes')
    try:
        html = get_html(params['url'], '').decode('utf-8').encode('utf-8')
        e = xml(html)
        if addon.getSetting("spamLog") == "true":
            xbmc.log(html)
        set_window_heading(e)
        try:
            parent_title=''
            try:
                parent_title = e.get('title1', '')
            except Exception:
                error("Unable to get parent title in buildTVEpisodes")
            if e.find('Directory') is not None:
                # this is never true
                #if e.find('Directory').get('type', 'none') == 'season':
                params['url'] = params['url'].replace('&mode=6', '&mode=5')
                build_tv_seasons(params)
                return
            # TODO: when banner is supported add it here also
            # banner = gen_image_url(e.get('banner', ''))
            art = gen_image_url(e.get('art', ''))

            # unused
            # season_thumb = e.get('thumb', '')

            if addon.getSetting('use_server_sort') == 'false':
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
            nextepisode = 1
            episode_count = 0

            video_list = e.findall('Video')
            if len(video_list) <= 0:
                error("No episodes in list")
            skip = addon.getSetting("skipExtraInfoOnLongSeries") == "true" and len(video_list) > int(
                addon.getSetting("skipExtraInfoMaxEpisodes"))

            # keep this init out of the loop, as we only provide this once
            list_cast = []
            list_cast_and_role = []
            tempgenre = ""
            parentkey = ""
            grandparenttitle = ""
            if not skip:
                for atype in video_list:
                    # we only get this once, so only set it if it's not already set
                    if len(list_cast) == 0:
                        result_list = get_cast_and_role(atype)
                        if result_list is not None:
                            list_cast = result_list[0]
                            list_cast_and_role = result_list[1]
                        tempgenre = get_tags(atype)
                        parentkey = atype.get('parentKey', '0')
                        if not parentkey.startswith("http") and not 'jmmserverkodi' in parentkey.lower():
                            parentkey = "http://" + addon.getSetting("ipaddress") + ":" + addon.getSetting("port") \
                                        + "/JMMServerKodi/GetMetadata/" + addon.getSetting("userid") + "/" + parentkey
                        grandparenttitle = atype.get('grandparentTitle',
                                                     atype.get('grandparentTitle', '')).encode('utf-8')
            # Extended support
            for atype in video_list:
                episode_count += 1

            # Extended support END#
                tempdir = []
                tempwriter = []
                view_offset = atype.get('viewOffset', 0)
                # Check for empty duration from MediaInfo check fail and handle it properly
                tmp_duration = atype.find('Media').get('duration', '1000')
                if not tmp_duration:
                    duration = 1
                else:
                    duration = int(tmp_duration) / 1000
                # Required listItem entries for XBMC
                details = {
                    'plot': "..." if skip else atype.get('summary', '').encode('utf-8'),
                    'title': atype.get('title', 'Unknown').encode('utf-8'),
                    'sorttitle': atype.get('titleSort', atype.get('title', 'Unknown')).encode('utf-8'),
                    'parenttitle': parent_title.encode('utf-8'),
                    'rating': float(atype.get('rating', 0)),
                    # 'studio'      : episode.get('studio',tree.get('studio','')).encode('utf-8') ,
                    # This doesn't work, some gremlins be afoot in this code...
                    # it's probably just that it only applies at series level
                    # 'cast'        : list(['Actor1','Actor2']),
                    # 'castandrole' : list([('Actor1','Character1'),('Actor2','Character2')]),
                    # According to the docs, this will auto fill castandrole
                    'CastAndRole': list_cast_and_role,
                    'Cast': list_cast,
                    'director': " / ".join(tempdir),
                    'writer': " / ".join(tempwriter),
                    'genre': "..." if skip else tempgenre,
                    'duration': str(datetime.timedelta(seconds=duration)),
                    'mpaa': atype.get('contentRating', ''),
                    'year': int(atype.get('year', 0)),
                    'tagline': "..." if skip else tempgenre,
                    'episode': int(atype.get('index', 0)),
                    'aired': atype.get('originallyAvailableAt', ''),
                    'tvshowtitle': grandparenttitle,
                    'votes': int(atype.get('votes', 0)),
                    'originaltitle': atype.get('original_title', ''),
                    'size': int(atype.find('Media').find('Part').get('size', 0)),
                    'season': int(atype.get('season', 0))
                }
                tempdate = str(details['aired']).split('-')
                if len(tempdate) == 3:  # format is 2016-01-24, we want it 24.01.2016
                    details['date'] = tempdate[1] + '.' + tempdate[2] + '.' + tempdate[0]

                thumb = gen_image_url(atype.get('thumb', ''))
                key = atype.get('key', '')
                if not key.startswith("http") and not 'jmmserverkodi' in key.lower():
                    key = "http://" + addon.getSetting("ipaddress") + ":" + str(int(addon.getSetting("port")) + 1) \
                          + "/videolocal/0/" + key

                ext = atype.find('Media').find('Part').get('container', '')
                newkey = atype.find('Media').find('Part').get('key', '')
                if not 'videolocal' in key:
                    key = newkey + '.' + ext

                # Extra data required to manage other properties
                extra_data = {'type': "Video", 'source': 'tvepisodes', 'thumb': None if skip else thumb,
                              'fanart_image': None if skip else art, 'key': key, 'resume': int(int(view_offset) / 1000),
                              'parentKey': parentkey, 'jmmepisodeid': atype.get('JMMEpisodeId', atype.get('GenericId', '0')),
                              'xVideoResolution': atype.find('Media').get('videoResolution', 0),
                              'xVideoCodec': atype.find('Media').get('audioCodec', ''),
                              'xVideoAspect': float(atype.find('Media').get('aspectRatio', 0)),
                              'xAudioCodec': atype.find('Media').get('videoCodec', ''),
                              'xAudioChannels': int(atype.find('Media').get('audioChannels', 0))}

                # Information about streams inside video file

                for vtype in atype.find('Media').find('Part').findall('Stream'):
                    stream = int(vtype.get('streamType'))
                    if stream == 1:
                        extra_data['VideoCodec'] = vtype.get('codec', '')
                        extra_data['width'] = int(vtype.get('width', 0))
                        extra_data['height'] = int(vtype.get('height', 0))
                        extra_data['duration'] = duration
                    elif stream == 2:
                        extra_data['AudioCodec'] = vtype.get('codec')
                        extra_data['AudioLanguage'] = vtype.get('language')
                        extra_data['AudioChannels'] = int(vtype.get('channels'))
                    elif stream == 3:
                        # subtitle
                        # TODO: we don't use this, but we have data so let's use it!
                        # language = vtype.get('language', '')
                        pass
                    else:
                        # error
                        error("Something went wrong!")

                # Determine what type of watched flag [overlay] to use
                if int(atype.get('viewCount', 0)) > 0:
                    details['playcount'] = 1
                else:
                    details['playcount'] = 0
                    if nextepisode == 1:
                        nextepisode = episode_count
                        nextepisode += 1

                context = None
                url = key

                key = atype.find('Media').find('Part').get('key')
                if not key.startswith("http") and not 'videolocal' in key.lower():
                    key = "http://" + addon.getSetting("ipaddress") + ":" + str(int(addon.getSetting("port")) + 1) \
                          + "/videolocal/0/" + key
                sys.argv[0] += "?url=" + url + "&mode=" + str(1) + "&file=" + key + "&ep_id=" \
                               + extra_data.get('jmmepisodeid')
                u = sys.argv[0]

                add_gui_item(u, details, extra_data, context, folder=False)

            # add item to move to next not played item (not marked as watched)
            if addon.getSetting("show_continue") == "true":
                util.addDir("-continue-", "&offset=" + str(nextepisode), 7,
                            "http://" + addon.getSetting("ipaddress") + ":" + addon.getSetting(
                                "port") + "/jmmserverkodi/GetSupportImage/plex_others.png", "2", "3", "4")
        except Exception as e:
            error("Error during build_tv_episodes", str(e))
    except Exception as e:
        error("Invalid XML Received in build_tv_episodes", str(e))
    xbmcplugin.endOfDirectory(handle)


def build_search(url):
    try:
        term = util.searchBox()
        tosend = {'url': url + term}
        build_tv_shows(tosend)
    except Exception as ex:
        error("Error during build_search", str(ex))


# Other functions
def play_video(url):
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
    player = xbmc.Player()
    try:
        player.play(item=url, listitem=item, windowed=False)
        xbmcplugin.setResolvedUrl(handle, True, item)
    except:
        pass
    # wait for player (network issue etc)
    xbmc.sleep(1000)
    mark = float(addon.getSetting("watched_mark"))
    mark /= 100
    file_fin = False
    # hack for slow connection and buffering time
    xbmc.sleep(int(addon.getSetting("player_sleep")))
    try:
        while player.isPlaying():
            try:
                xbmc.sleep(500)
                totaltime = player.getTotalTime()
                currenttime = player.getTime()
                if (totaltime * mark) < currenttime:
                    file_fin = True
                if not player.isPlaying():
                    break
            except:
                xbmc.sleep(500)
                break
    except:
        pass
    if file_fin is True:
        xbmc.executebuiltin('RunScript(plugin.video.nakamori, %s, %s&cmd=watched)' % (sys.argv[1], sys.argv[2]))


# TODO: Not used maybe it should be added to '-continue-' that would add all episodes to list? or Drop it
def play_playlist(data):
    offset = data['offset']
    pos = int(offset)
    if pos == 1:
        xbmcgui.Dialog().ok('Finished', 'You already finished this')
    else:
        win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
        cid = win.getFocusId()
        ctl = win.getControl(cid)
        ctl.selectItem(pos)
        # temporary hack to prevent from going back on first item
        xbmc.sleep(1000)
        # Jarvis code:
        # xbmc.executebuiltin('SetFocus(%s, %s)' % (cid, pos))


# TODO: Trakt_Scrobble need work - JMM support it (for series not movies)
def trakt_scrobble(data=""):
    xbmcgui.Dialog().ok('WIP', str(data))


def vote_series(params):
    vote_list = ['Don\'t Vote', '10', '9', '8', '7', '6', '5', '4', '3', '2', '1', '0']
    my_vote = xbmcgui.Dialog().select('my_vote', vote_list)
    if my_vote == -1:
        return
    elif my_vote != 0:
        my_len = len(
            "http://" + addon.getSetting("ipaddress") + ":" + addon.getSetting("port") + addon.getSetting("userid"))
        vote_value = str(vote_list[my_vote])
        vote_type = str(1)
        series_id = params['anime_id'][(my_len + 30):]
        get_html("http://" + addon.getSetting("ipaddress") + ":" + addon.getSetting("port") + "/jmmserverkodi/vote/" \
                 + addon.getSetting("userid") + "/" + series_id + "/" + vote_value + "/" + vote_type, "")
        xbmc.executebuiltin("XBMC.Notification(%s, %s %s, 7500, %s)" % (
            'Vote saved', 'You voted', vote_value, addon.getAddonInfo('icon')))


def vote_episode(params):
    vote_list = ['Don\'t Vote', '10', '9', '8', '7', '6', '5', '4', '3', '2', '1', '0']
    my_vote = xbmcgui.Dialog().select('my_vote', vote_list)
    if my_vote == -1:
        return
    elif my_vote != 0:
        vote_value = str(vote_list[my_vote])
        vote_type = str(4)
        ep_id = params['ep_id']
        get_html("http://" + addon.getSetting("ipaddress") + ":" + addon.getSetting(
            "port") + "/jmmserverkodi/vote/" + addon.getSetting(
            "userid") + "/" + ep_id + "/" + vote_value + "/" + vote_type, "")
        xbmc.executebuiltin("XBMC.Notification(%s, %s %s, 7500, %s)" % (
            'Vote saved', 'You voted', vote_value, addon.getAddonInfo('icon')))


def watched_mark(params):
    episode_id = params['ep_id']
    if addon.getSetting('log_spam') == 'true':
        xbmc.log('epid: ' + str(episode_id))
        xbmc.log('key: ' + "http://" + addon.getSetting("ipaddress") + ":" + addon.getSetting(
                "port") + "/jmmserverkodi/watch/" + addon.getSetting("userid") + "/" + episode_id + "/" + str(watched))
    watched = bool(params['watched'])
    if watched is True:
        watched_msg = "watched"
    else:
        watched_msg = "unwatched"
    xbmc.executebuiltin('XBMC.Action(ToggleWatched)')
    sync = addon.getSetting("syncwatched")
    if sync == "true":
        get_html("http://" + addon.getSetting("ipaddress") + ":" + addon.getSetting(
            "port") + "/jmmserverkodi/watch/" + addon.getSetting("userid") + "/" + episode_id + "/" + str(watched), "")
    box = addon.getSetting("watchedbox")
    if box == "true":
        xbmc.executebuiltin("XBMC.Notification(%s, %s %s, 2000, %s)" % (
            'Watched status changed', 'Mark as ', watched_msg, addon.getAddonInfo('icon')))


# Script run from here
if valid_user() is True:
    try:
        parameters = util.parseParameters()
    except Exception as e:
        error('valid_user parseParameters() error', str(e))
        parameters = {'mode': 2}
    if parameters:
        try:
            mode = int(parameters['mode'])
        except Exception as e:
            error('valid_user set \'mode\' error', str(e) + " parameters: " + str(parameters))
            mode = None
    else:
        mode = None
    try:
        cmd = parameters['cmd']
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
            parameters['watched'] = True
            watched_mark(parameters)
            voting = addon.getSetting("voteallways")
            if voting == "true":
                vote_episode(parameters)
        elif cmd == "unwatched":
            parameters['watched'] = False
            watched_mark(parameters)
        elif cmd == "playlist":
            play_playlist(parameters)
    else:
        if mode == 1:  # VIDEO
            # xbmcgui.Dialog().ok('MODE=1','MODE')
            play_video(parameters['file'])
            # play_playlist()
        elif mode == 2:  # DIRECTORY
            xbmcgui.Dialog().ok('MODE=2', 'MODE')
        elif mode == 3:  # SEARCH
            # xbmcgui.Dialog().ok('MODE=3','MODE')
            build_search(parameters['url'])
        elif mode == 4:  # TVShows
            # xbmcgui.Dialog().ok('MODE=4','MODE')
            build_tv_shows(parameters)
        elif mode == 5:  # TVSeasons
            # xbmcgui.Dialog().ok('MODE=5','MODE')
            build_tv_seasons(parameters)
        elif mode == 6:  # TVEpisodes
            # xbmcgui.Dialog().ok('MODE=6','MODE')
            build_tv_episodes(parameters)
        elif mode == 7:  # Playlist continue
            # xbmcgui.Dialog().ok('MODE=7','MODE')
            play_playlist(parameters)
        else:
            build_main_menu()
else:
    error("Wrong UserID", "Please change UserID in Settings")
