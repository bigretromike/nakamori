import datetime
import os.path
import re
import sys
import traceback
import urllib
import xml.etree.ElementTree as tree

import urllib2

import TagBlacklist
import resources.lib.util as util
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

handle = int(sys.argv[1])
addon = xbmcaddon.Addon(id='plugin.video.nakamoriplugin')

urlopen = urllib2.urlopen
Request = urllib2.Request


# Internal function
def getHtml (url, referer):
    referer = urllib2.quote(referer).replace("%3A", ":")
    req = Request(url)
    if len(referer) > 1:
        req.add_header('Referer', referer)
    response = urlopen(req, timeout=int(addon.getSetting('timeout')))
    data = response.read()
    response.close()
    return data


def setWindowHeading (tree):
    WINDOW = xbmcgui.Window(xbmcgui.getCurrentWindowId())
    try:
        WINDOW.setProperty("heading", tree.get('title1'))
    except:
        WINDOW.clearProperty("heading")
    try:
        WINDOW.setProperty("heading2", tree.get('title2'))
    except:
        WINDOW.clearProperty("heading2")


def getTitle (data):
    lang = addon.getSetting("displaylang")
    titles = data.split('|')
    skip = addon.getSetting("skipofficial")
    if skip == "true":
        for title in titles:
            if '{official:' + lang + '}' in title:
                return title.replace('{official:' + lang + '}', '')
    for title in titles:
        if '{main:' + lang + '}' in title:
            return title.replace('{main:' + lang + '}', '')
    return 'err404'


def addGUIItem (url, details, extraData, context=None, folder=True):
    tbi = ""
    tp = 'Video'
    if addon.getSetting("spamLog") == "true":
        if details is not None:
            xbmc.log("addGuiItem - details")
            for i in details:
                tempLog = ""
                a = details.get(i)
                if a is None:
                    tempLog = "\'unset\'"
                elif isinstance(a, list):
                    for b in a:
                        tempLog = str(b) if tempLog == "" else tempLog + " | " + str(b)
                else:
                    tempLog = str(a)
                xbmc.log("-" + str(i) + "- " + tempLog)
        if extraData is not None:
            xbmc.log("addGuiItem - extraData")
            for i in extraData:
                tempLog = ""
                a = extraData.get(i)
                if a is None:
                    tempLog = "\'unset\'"
                elif isinstance(a, list):
                    for b in a:
                        tempLog = str(b) if tempLog == "" else tempLog + " | " + str(b)
                else:
                    tempLog = str(a)
                xbmc.log("-" + str(i) + "- " + tempLog)

    if extraData is not None:
        if extraData.get('parameters'):
            for argument, value in extraData.get('parameters').items():
                link_url = "%s&%s=%s" % (link_url, argument, urllib.quote(value))
        tbi = extraData.get('thumb', '')
        tp = extraData.get('type', 'Video')
    link_url = url
    title = ""
    if folder:
        title = details.get('originaltitle', '')
        title = getTitle(title)
        if 'err404' in title:
            title = details.get('title', 'Unknown')
    else:
        title = details.get('title', 'Unknown')
    details['title'] = title
    liz = xbmcgui.ListItem(details.get('title', 'Unknown'), thumbnailImage=tbi)

    # Set the properties of the item, such as summary, name, season, etc
    liz.setInfo(type=tp, infoLabels=details)

    # For all end items
    if not folder:
        liz.setProperty('IsPlayable', 'true')
        if extraData and len(extraData) > 0:
            if extraData.get('type', 'video').lower() == "video":
                liz.setProperty('TotalTime', str(extraData.get('duration')))
                liz.setProperty('ResumeTime', str(extraData.get('resume')))

                liz.setProperty('VideoResolution', str(extraData.get('xVideoResolution', '')))
                liz.setProperty('VideoCodec', extraData.get('xVideoCodec', ''))
                liz.setProperty('AudioCodec', extraData.get('xAudioCodec', ''))
                liz.setProperty('AudioChannels', str(extraData.get('xAudioChannels', '')))
                liz.setProperty('VideoAspect', str(extraData.get('xVideoAspect', '')))

                video_codec = { }
                if extraData.get('VideoCodec'): video_codec['codec'] = extraData.get('VideoCodec')
                if extraData.get('height'): video_codec['height'] = int(extraData.get('height'))
                if extraData.get('width'): video_codec['width'] = int(extraData.get('width'))
                if extraData.get('duration'): video_codec['duration'] = extraData.get('duration')

                audio_codec = { }
                if extraData.get('AudioCodec'): audio_codec['codec'] = extraData.get('AudioCodec')
                if extraData.get('AudioChannels'): audio_codec['channels'] = int(extraData.get('AudioChannels'))
                if extraData.get('AudioLanguage'): audio_codec['language'] = extraData.get('AudioLanguage')

                liz.addStreamInfo('video', video_codec)
                liz.addStreamInfo('audio', audio_codec)
        # Jumpy like this and Nakamori like Jumpy
        partemp = util.parseParameters(inputString=url)
        liz.setProperty('path', str(partemp.get('file', 'pusto')))
    if extraData and len(extraData) > 0:
        if extraData.get('source') == 'tvshows' or extraData.get('source') == 'tvseasons':
            # Then set the number of watched and unwatched, which will be displayed per season
            liz.setProperty('TotalEpisodes', str(extraData['TotalEpisodes']))
            liz.setProperty('WatchedEpisodes', str(extraData['WatchedEpisodes']))
            liz.setProperty('UnWatchedEpisodes', str(extraData['UnWatchedEpisodes']))

            # Hack to show partial flag for TV shows and seasons
            if extraData.get('partialTV') == 1:
                liz.setProperty('TotalTime', '100')
                liz.setProperty('ResumeTime', '50')

    if extraData and len(extraData) > 0:
        # fanart is nearly always available, so exceptions are rare.
        if extraData.get('fanart_image'):
            liz.setProperty('fanart_image', extraData.get('fanart_image'))

        if extraData.get('banner'):
            liz.setProperty('banner', '%s' % extraData.get('banner', ''))

        if extraData.get('season_thumb'):
            liz.setProperty('seasonThumb', '%s' % extraData.get('season_thumb', ''))

    if context is None:
        if extraData and len(extraData) > 0:
            if extraData.get('type', 'video').lower() == "video":
                context = []
                url_peep = sys.argv[2]
                # Always allow 'More Info' to be executed. Some places have more info than others
                context.append(('More Info', 'Action(Info)'))
                if extraData.get('source', 'none') == 'tvshows' or extraData.get('source', 'none') == 'tvseasons':
                    url_peep = url_peep + "&anime_id=" + extraData.get('key') + "&cmd=voteSer"
                    context.append(('Vote', 'RunScript(plugin.video.nakamoriplugin, %s, %s)' % (sys.argv[1], url_peep)))
                    if addon.getSetting("spamLog") == "true":
                        xbmc.log("Vote for Series on Series or Season - " + 'RunScript(plugin.video.nakamoriplugin, %s, %s)' % (sys.argv[1], url_peep))
                if extraData.get('source', 'none') == 'tvepisodes':
                    url_peep = url_peep + "&anime_id=" + extraData.get('parentKey') + "&ep_id=" + extraData.get(
                            'jmmepisodeid')
                    context.append(('Vote for Series', 'RunScript(plugin.video.nakamoriplugin, %s, %s&cmd=voteSer)' % (
                        sys.argv[1], url_peep)))
                    if addon.getSetting("spamLog") == "true":
                        xbmc.log("Vote for Series on Episode - " + 'RunScript(plugin.video.nakamoriplugin, %s, %s&cmd=voteSer)' % (sys.argv[1], url_peep))
                    context.append(('Vote for Episode', 'RunScript(plugin.video.nakamoriplugin, %s, %s&cmd=voteEp)' % (
                        sys.argv[1], url_peep)))
                    context.append(('Mark as Watched', 'RunScript(plugin.video.nakamoriplugin, %s, %s&cmd=watched)' % (
                        sys.argv[1], url_peep)))
                    context.append(('Mark as Unwatched',
                                    'RunScript(plugin.video.nakamoriplugin, %s, %s&cmd=unwatched)' % (
                                        sys.argv[1], url_peep)))
                liz.addContextMenuItems(context)
    return xbmcplugin.addDirectoryItem(handle, url, listitem=liz, isFolder=folder)


def validUser ():
    e = tree.XML(
            getHtml("http://" + addon.getSetting("ipaddress") + ":" + addon.getSetting("port") + "/jmmserverkodi/getusers",
                    ""))
    valid = False
    for atype in e.findall('User'):
        id = atype.get('id')
        if id == addon.getSetting("userid"):
            valid = True
    return valid


def Error (msg, error="Generic"):
    xbmc.log('---' + msg + '---')
    try:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        xbmc.log(str(exc_type) + " at line " + str(exc_tb.tb_lineno) + " in file " + str(
                os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]) + " : " + str(error))
    except:
        xbmc.log("There was an error catching the error. WTF.")
        traceback.print_exc()

    xbmc.executebuiltin("XBMC.Notification(%s, %s %s, 2000, %s)" % ('ERROR', ' ', msg, addon.getAddonInfo('icon')))


def removeHTML (data):
    # p = re.compile(r'<.*?>')
    p = re.compile('http://anidb.net/[a-z]{1,3}[0-9]{1,7}[ ]')
    data2 = p.sub('', data)
    p = re.compile('(\[|\])')
    return p.sub('', data2)


# Adding items to list/menu:
def buildMainMenu ():
    xbmcplugin.setContent(handle, content='tvshows')
    try:
        e = tree.XML(getHtml("http://" + addon.getSetting("ipaddress") + ":" + addon.getSetting(
                "port") + "/jmmserverkodi/getfilters/" + addon.getSetting("userid"), ""))
        try:
            for atype in e.findall('Directory'):
                title = atype.get('title')
                mode = 4
                if title == 'Continue Watching (SYSTEM)':
                    title = 'Continue Watching'
                elif title == 'Unsort':
                    mode = 6
                url = atype.get('key')
                thumb = atype.get('thumb', '')
                fanart = atype.get('art', thumb)
                u = sys.argv[0] + "?url=" + url + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(title)
                liz = xbmcgui.ListItem(label=title, label2=title, iconImage="DefaultVideo.png", thumbnailImage=thumb,
                                       path=url)
                liz.setProperty('fanart_image', fanart)
                liz.setInfo(type="Video", infoLabels={
                    "Title": title
                })
                xbmcplugin.addDirectoryItem(handle, url=u, listitem=liz, isFolder=True)
        except Exception as e:
            Error("Error during buildMainMenu", e)
    except Exception as e:
        Error("Connection error", e)

    # Add Search
    url = "http://" + addon.getSetting("ipaddress") + ":" + addon.getSetting(
            "port") + "/jmmserverkodi/search/" + addon.getSetting("userid") + "/" + addon.getSetting("maxlimit") + "/"
    mode = 3
    title = "Search"
    thumb = "http://" + addon.getSetting("ipaddress") + ":" + addon.getSetting(
            "port") + "/jmmserverkodi/GetSupportImage/plex_others.png"
    liz = xbmcgui.ListItem(label=title, label2=title, iconImage="DefaultVideo.png", thumbnailImage=thumb, path=url)
    liz.setInfo(type="Video", infoLabels={
        "Title": title
    })
    u = sys.argv[0] + "?url=" + url + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(title)
    xbmcplugin.addDirectoryItem(handle, url=u, listitem=liz, isFolder=True)
    xbmcplugin.endOfDirectory(handle, True, False, False)


def buildTVShows (params):
    # xbmcgui.Dialog().ok('MODE=4','IN')
    xbmcplugin.setContent(handle, 'tvshows')
    xbmcplugin.addSortMethod(handle, 25)  # video title ignore THE
    xbmcplugin.addSortMethod(handle, 3)  # date
    xbmcplugin.addSortMethod(handle, 18)  # rating
    xbmcplugin.addSortMethod(handle, 17)  # year
    xbmcplugin.addSortMethod(handle, 28)  # by MPAA

    try:
        html = getHtml(params['url'], '')
        e = tree.XML(html)
        if addon.getSetting("spamLog") == "true":
            xbmc.log(html)
        setWindowHeading(e)
        try:
            for atype in e.findall('Directory'):
                tempgenre = ""
                tag = atype.find("Tag")
                if tag is not None:
                    tempgenre = tag.get('tag', '')
                    tempGenres = str.split(tempgenre, ",")
                    tempGenres = TagBlacklist.processTags(addon, tempGenres)
                    tempgenre = ""
                    for a in tempGenres:
                        a = " ".join(w.capitalize() for w in a.split())
                        tempgenre = a if tempgenre == "" else tempgenre + " | " + a
                watched = int(atype.get('viewedLeafCount', 0))

                # Extended support
                listCastAndRole = []
                charTag = atype.find('Characters')
                if charTag is not None:
                    for char in charTag.findall('Character'):
                        # don't init any variables we don't need
                        # char_id = char.get('charID')
                        char_charname = char.get('charname', '')
                        # char_picture=char.get('picture','')
                        # char_desc=char.get('description','')
                        char_seiyuuname = char.get('seiyuuname', '')
                        # char_seiyuupic=char.get('seiyuupic','')
                        # only add it if it has data
                        # reorder these to match the convention (Actor is cast, character is role, in that order)
                        if len(char_charname) != 0 or len(char_seiyuuname) != 0:
                            listCastAndRole.append((str(char_seiyuuname), str(char_charname)))
                # Extended support END#

                total = 0
                if addon.getSetting("local_total") == "true":
                    total = int(atype.get('totalLocal', 0))
                else:
                    total = int(atype.get('leafCount', 0))
                details = {

                    'title'        : atype.get('title', 'Unknown').encode('utf-8'),
                    'genre'        : tempgenre,
                    'year'         : int(atype.get('year', 0)),
                    'episode'      : total,
                    'season'       : int(atype.get('season', 0)),
                    # 'count'        : count,
                    # 'size'         : size,
                    # 'Date'         : date,
                    'rating'       : float(atype.get('rating')),
                    # 'playcount'    : int(atype.get('viewedLeafCount')),
                    # overlay        : integer (2, - range is 0..8. See GUIListItem.h for values
                    'cast'         : listCastAndRole,  # cast : list (Michal C. Hall,
                    'castandrole'  : listCastAndRole,
                    # This also does nothing. Those gremlins.
                    # 'cast'         : list([("Actor1", "Character1"),("Actor2","Character2")]),
                    # 'castandrole'  : list([("Actor1", "Character1"),("Actor2","Character2")]),
                    # director       : string (Dagur Kari,
                    'mpaa'         : atype.get('contentRating', ''),
                    'plot'         : removeHTML(atype.get('summary', '').encode('utf-8')),
                    # 'plotoutline'  : plotoutline,
                    'originaltitle': atype.get('original_title', '').encode("utf-8"),
                    'sorttitle'    : atype.get('title', 'Unknown').encode('utf-8'),
                    # 'Duration'     : duration,
                    # 'Studio'       : studio, < ---
                    # 'Tagline'      : tagline,
                    # 'Writer'       : writer,
                    # 'tvshowtitle'  : tvshowtitle,
                    'tvshowname'   : atype.get('title', 'Unknown').encode('utf-8'),
                    # 'premiered'    : premiered,
                    # 'Status'       : status,
                    # code           : string (tt0110293, - IMDb code
                    'aired'        : atype.get('originallyAvailableAt', ''),
                    # credits        : string (Andy Kaufman, - writing credits
                    # 'Lastplayed'   : lastplayed,
                    'votes'        : atype.get('votes'),
                    # trailer        : string (/home/user/trailer.avi,
                    'dateadded'    : atype.get('addedAt')
                }

                extraData = {
                    'type'             : 'video',
                    'source'           : 'tvshows',
                    'UnWatchedEpisodes': int(details['episode']) - watched,
                    'WatchedEpisodes'  : watched,
                    'TotalEpisodes'    : details['episode'],
                    'thumb'            : atype.get('thumb'),
                    'fanart_image'     : atype.get('art', atype.get('thumb')),
                    'key'              : atype.get('key', ''),
                    'ratingKey'        : str(atype.get('ratingKey', 0))
                }
                url = atype.get('key')

                # Set up overlays for watched and unwatched episodes
                if extraData['WatchedEpisodes'] == 0:
                    details['playcount'] = 0
                elif extraData['UnWatchedEpisodes'] == 0:
                    details['playcount'] = 1
                else:
                    extraData['partialTV'] = 1

                u = sys.argv[0] + "?url=" + url + "&mode=" + str(5)
                context = None
                addGUIItem(u, details, extraData, context)
        except Exception as e:
            Error("Error during buildTVShows", e)
    except Exception as e:
        Error("Connection error", e)
    xbmcplugin.endOfDirectory(handle)


def buildTVSeasons (params):
    # xbmcgui.Dialog().ok('MODE=5','IN')

    xbmcplugin.setContent(handle, 'seasons')
    try:
        html = getHtml(params['url'], '')
        e = tree.XML(html)
        if addon.getSetting("spamLog") == "true":
            xbmc.log(html)
        setWindowHeading(e)
        try:
            if e.find('Directory') is None:
                params['url'] = params['url'].replace('&mode=5', '&mode=6')
                buildTVEpisodes(params)
                return

            willFlatten = False
            # check for a single season
            if int(e.get('size', 0)) == 1:
                willFlatten = True

            sectionart = e.get('art', '')
            banner = e.get('banner', '')
            setWindowHeading(e)
            # For all the directory tags

            for atype in e.findall('Directory'):
                if willFlatten:
                    url = atype.get('key')
                    u = sys.argv[0] + "?url=" + url + "&mode=" + str(6)
                    buildTVEpisodes(u)
                    return

                plot = removeHTML(atype.get('summary', '').encode('utf-8'))

                tempgenre = ""
                tag = atype.find("Tag")
                if tag is not None:
                    tempgenre = tag.get('tag', '').encode('utf-8')
                    tempGenres = str.split(tempgenre, ",")
                    tempGenres = TagBlacklist.processTags(addon, tempGenres)
                    tempgenre = ""
                    for a in tempGenres:
                        " ".join(w.capitalize() for w in a.split())
                        tempgenre = a if tempgenre == "" else tempgenre + " | " + a

                watched = int(atype.get('viewedLeafCount', 0))

                listCastAndRole = []
                charTag = atype.find('Characters')
                if charTag is not None:
                    for char in charTag.findall('Character'):
                        # don't init any variables we don't need
                        # char_id = char.get('charID')
                        char_charname = char.get('charname', '')
                        # char_picture=char.get('picture','')
                        # char_desc=char.get('description','')
                        char_seiyuuname = char.get('seiyuuname', '')
                        # char_seiyuupic=char.get('seiyuupic','')
                        # only add it if it has data
                        # reorder these to match the convention (Actor is cast, character is role, in that order)
                        if len(char_charname) != 0 or len(char_seiyuuname) != 0:
                            listCastAndRole.append((str(char_seiyuuname), str(char_charname)))

                # Create the basic data structures to pass up
                total = 0
                if addon.getSetting("local_total") == "true":
                    total = int(atype.get('totalLocal', 0))
                else:
                    total = int(atype.get('leafCount', 0))
                details = {
                    'title'      : atype.get('title', 'Unknown').encode('utf-8'),
                    'tvshowname' : atype.get('title', 'Unknown').encode('utf-8'),
                    'sorttitle'  : atype.get('titleSort', atype.get('title', 'Unknown')).encode('utf-8'),
                    'studio'     : atype.get('studio', '').encode('utf-8'),
                    'cast'       : listCastAndRole,
                    'castandrole': listCastAndRole,
                    'plot'       : plot,
                    'genre'      : tempgenre,
                    'season'     : int(atype.get('season', 0)),
                    'episode'    : total,
                    'mpaa'       : atype.get('contentRating', ''),
                    'rating'     : atype.get('rating'),
                    'aired'      : atype.get('originallyAvailableAt', '')
                }

                if atype.get('sorttitle'): details['sorttitle'] = atype.get('sorttitle')

                extraData = {
                    'type'             : 'video',
                    'source'           : 'tvseasons',
                    'TotalEpisodes'    : details['episode'],
                    'WatchedEpisodes'  : watched,
                    'UnWatchedEpisodes': details['episode'] - watched,
                    'thumb'            : atype.get('thumb', ''),
                    'fanart_image'     : atype.get('art', ''),
                    'key'              : atype.get('key', ''),
                    'ratingKey'        : str(atype.get('ratingKey', 0)),  # <--------------
                    'mode'             : str(6)
                }

                if banner:
                    extraData['banner'] = banner

                if extraData['fanart_image'] == "":
                    extraData['fanart_image'] = sectionart

                # Set up overlays for watched and unwatched episodes
                if extraData['WatchedEpisodes'] == 0:
                    details['playcount'] = 0
                elif extraData['UnWatchedEpisodes'] == 0:
                    details['playcount'] = 1
                else:
                    extraData['partialTV'] = 1

                url = sys.argv[0] + "?url=" + extraData['key'] + "&mode=" + str(6)
                context = None

                # Build the screen directory listing
                addGUIItem(url, details, extraData, context)
        except Exception as e:
            Error("Error during buildTVSeasons", e)
    except Exception as e:
        Error("Connection error", e)
    xbmcplugin.endOfDirectory(handle)


def buildTVEpisodes (params):
    # xbmcgui.Dialog().ok('MODE=6','IN')
    xbmcplugin.setContent(handle, 'episodes')
    try:
        html = getHtml(params['url'], '')
        e = tree.XML(html)
        if addon.getSetting("spamLog") == "true":
            xbmc.log(html)
        setWindowHeading(e)
        try:
            if e.find('Directory') is not None:
                if e.find('Directory').get('type', 'none') == 'season':
                    params['url'] = params['url'].replace('&mode=6', '&mode=5')
                    buildTVSeasons(params)
                    return

            banner = e.get('banner', '')
            art = e.get('art', '')
            season_thumb = e.get('thumb', '')
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

            videoList = e.findall('Video')
            skip = addon.getSetting("skipExtraInfoOnLongSeries") == "true" and len(videoList) > int(
                    addon.getSetting("skipExtraInfoMaxEpisodes"))

            tempgenre = ""
            if not skip:
                # xbmc.log(str(e.find("Tag")))
                tag = e.find("Tag")
                if tag is not None:
                    tempgenre = tag.get('tag', '').encode('utf-8')
                    tempGenres = str.split(tempgenre, ",")
                    tempGenres = TagBlacklist.processTags(addon, tempGenres)
                    tempgenre = ""
                    for a in tempGenres:
                        " ".join(w.capitalize() for w in a.split())
                        tempgenre = a if tempgenre == "" else tempgenre + " | " + a
            # keep this init out of the loop, as we only provide this once
            listCastAndRole = []
            for atype in videoList:
                episode_count += 1

                # we only get this onc, so only set it if it's not already set
                if len(listCastAndRole) == 0:
                    charTag = atype.find('Characters')
                    if charTag is not None:
                        for char in charTag.findall('Character'):
                            # don't init any variables we don't need
                            # char_id = char.get('charID')
                            char_charname = char.get('charname', '')
                            # char_picture=char.get('picture','')
                            # char_desc=char.get('description','')
                            char_seiyuuname = char.get('seiyuuname', '')
                            # char_seiyuupic=char.get('seiyuupic','')
                            # only add it if it has data
                            # reorder these to match the convention (Actor is cast, character is role, in that order)
                            if len(char_charname) != 0 or len(char_seiyuuname) != 0:
                                listCastAndRole.append((str(char_seiyuuname), str(char_charname)))
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
                    'plot'         : "..." if skip else atype.get('summary', '').encode('utf-8'),
                    'title'        : atype.get('title', 'Unknown').encode('utf-8'),
                    'sorttitle'    : atype.get('titleSort', atype.get('title', 'Unknown')).encode('utf-8'),
                    'rating'       : float(atype.get('rating', 0)),
                    # 'studio'      : episode.get('studio',tree.get('studio','')).encode('utf-8') ,
                    # This doesn't work, some gremlins be afoot in this code...it's probably just that it only applies at series level
                    # 'cast'        : list(['Actor1','Actor2']),
                    # 'castandrole' : list([('Actor1','Character1'),('Actor2','Character2')]),
                    # According to the docs, this will auto fill castandrole
                    'cast'         : listCastAndRole,
                    'director'     : " / ".join(tempdir),
                    'writer'       : " / ".join(tempwriter),
                    'genre'        : tempgenre,
                    'duration'     : str(datetime.timedelta(seconds=duration)),
                    'mpaa'         : atype.get('contentRating', ''),
                    'year'         : int(atype.get('year', 0)),
                    'tagline'      : "..." if skip else tempgenre,
                    'episode'      : int(atype.get('index', 0)),
                    'aired'        : atype.get('originallyAvailableAt', ''),
                    'tvshowtitle'  : atype.get('grandparentTitle', atype.get('grandparentTitle', '')).encode('utf-8'),
                    # <-----------------------
                    'votes'        : int(atype.get('votes', 0)),
                    'originaltitle': atype.get('original_title', ''),
                    'size'         : int(atype.find('Media').find('Part').get('size', 0)),
                    'season'       : int(atype.get('season', 0))
                }

                # Extra data required to manage other properties
                extraData = {
                    'type'        : "Video",
                    'source'      : 'tvepisodes',
                    'thumb'       : None if skip else atype.get('thumb', ''),
                    'fanart_image': None if skip else art,
                    'key'         : atype.get('key', ''),
                    # 'ratingKey'    : str(episode.get('ratingKey',0)),
                    # 'duration'     : duration,
                    'resume'      : int(int(view_offset) / 1000),
                    'parentKey'   : atype.get('parentKey', '0'),
                    'jmmepisodeid': atype.get('JMMEpisodeId', '0')
                }

                # Information about streams inside video file
                extraData['xVideoResolution'] = atype.find('Media').get('videoResolution', 0)
                extraData['xVideoCodec'] = atype.find('Media').get('audioCodec', '')
                extraData['xVideoAspect'] = float(atype.find('Media').get('aspectRatio', 0))
                extraData['xAudioCodec'] = atype.find('Media').get('videoCodec', '')
                extraData['xAudioChannels'] = int(atype.find('Media').get('audioChannels', 0))

                for vtype in atype.find('Media').find('Part').findall('Stream'):
                    stream = int(vtype.get('streamType'))
                    if stream == 1:
                        extraData['VideoCodec'] = vtype.get('codec', '')
                        extraData['width'] = int(vtype.get('width', 0))
                        extraData['height'] = int(vtype.get('height', 0))
                        extraData['duration'] = duration
                    elif stream == 2:
                        extraData['AudioCodec'] = vtype.get('codec')
                        extraData['AudioLanguage'] = vtype.get('language')
                        extraData['AudioChannels'] = int(vtype.get('channels'))
                    elif stream == 3:
                        # subtitle
                        try:
                            language = vtype.get('language')
                        except:
                            pass
                    else:
                        # error
                        Error("Something went wrong!")

                # Determine what type of watched flag [overlay] to use
                if int(atype.get('viewCount', 0)) > 0:
                    details['playcount'] = 1
                else:
                    details['playcount'] = 0
                    if nextepisode == 1:
                        nextepisode = episode_count
                        nextepisode += 1

                context = None
                url = atype.get('key')

                sys.argv[0] = sys.argv[0] + "?url=" + url + "&mode=" + str(1) + "&file=" + atype.find('Media').find(
                        'Part').get('key') + "&ep_id=" + extraData.get('jmmepisodeid')
                u = sys.argv[0]

                addGUIItem(u, details, extraData, context, folder=False)

            # add item to move to next not played item (not marked as watched)
            if addon.getSetting("show_continue") == "true":
                util.addDir("-continue-", "&offset=" + str(nextepisode), 7,
                            "http://" + addon.getSetting("ipaddress") + ":" + addon.getSetting(
                                    "port") + "/jmmserverkodi/GetSupportImage/plex_others.png", "2", "3", "4")
        except Exception as e:
            Error("Error during buildTVEpisodes", e)
    except Exception as e:
        Error("Connection error", e)
    xbmcplugin.endOfDirectory(handle)


def buildSearch (url):
    try:
        term = util.searchBox()
        toSend = {
            'url': url + term
        }
        buildTVShows(toSend)
    except Exception as e:
        Error("Error during buildSearch", e)


# Other functions
def playVideo (url):
    details = {
        'plot'         : xbmc.getInfoLabel('ListItem.Plot'),
        'title'        : xbmc.getInfoLabel('ListItem.Title'),
        'sorttitle'    : xbmc.getInfoLabel('ListItem.Title'),
        'rating'       : xbmc.getInfoLabel('ListItem.Rating'),
        'duration'     : xbmc.getInfoLabel('ListItem.Duration'),
        'mpaa'         : xbmc.getInfoLabel('ListItem.Mpaa'),
        'year'         : xbmc.getInfoLabel('ListItem.Year'),
        'tagline'      : xbmc.getInfoLabel('ListItem.Tagline'),
        'episode'      : xbmc.getInfoLabel('ListItem.Episode'),
        'aired'        : xbmc.getInfoLabel('ListItem.Premiered'),
        'tvshowtitle'  : xbmc.getInfoLabel('ListItem.TVShowTitle'),
        'votes'        : xbmc.getInfoLabel('ListItem.Votes'),
        'originaltitle': xbmc.getInfoLabel('ListItem.OriginalTitle'),
        'size'         : xbmc.getInfoLabel('ListItem.Size'),
        'season'       : xbmc.getInfoLabel('ListItem.Season')
    }
    item = xbmcgui.ListItem(details.get('title', 'Unknown'), thumbnailImage=xbmc.getInfoLabel('ListItem.Thumb'),
                            path=url)
    item.setInfo(type='Video', infoLabels=details)
    item.setProperty('IsPlayable', 'true')
    Player = xbmc.Player()
    try:
        Player.play(item=url, listitem=item, windowed=False)
        xbmcplugin.setResolvedUrl(handle, True, item)
    except:
        pass
    # wait for player (network issue etc)
    xbmc.sleep(1000)
    mark = float(addon.getSetting("watched_mark"))
    mark = mark / 100
    file_fin = False
    totalTime = 0
    currentTime = 0
    # hack for slow connection and buffering time
    xbmc.sleep(int(addon.getSetting("player_sleep")))
    while Player.isPlaying():
        try:
            xbmc.sleep(500)
            totalTime = Player.getTotalTime()
            currentTime = Player.getTime()
            if (totalTime * mark) < currentTime:
                file_fin = True
            if Player.isPlaying() == False:
                break
        except:
            xbmc.sleep(500)
            break
    if file_fin is True:
        xbmc.executebuiltin('RunScript(plugin.video.nakamoriplugin, %s, %s&cmd=watched)' % (sys.argv[1], sys.argv[2]))


def playPlaylist (data):
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


def TraktScrobble (data):
    xbmcgui.Dialog().ok('WIP', 'WIP')


def voteSeries (params):
    vote_list = ['Don\'t Vote', '10', '9', '8', '7', '6', '5', '4', '3', '2', '1', '0']
    myVote = xbmcgui.Dialog().select('myVote', vote_list)
    if myVote == -1:
        return
    elif myVote != 0:
        myLen = len(
                "http://" + addon.getSetting("ipaddress") + ":" + addon.getSetting("port") + addon.getSetting("userid"))
        vote_value = str(vote_list[myVote])
        vote_type = str(1)
        series_id = params['anime_id'][(myLen + 30):]
        getHtml("http://" + addon.getSetting("ipaddress") + ":" + addon.getSetting(
                "port") + "/jmmserverkodi/vote/" + addon.getSetting(
                "userid") + "/" + series_id + "/" + vote_value + "/" + vote_type, "")
        xbmc.executebuiltin("XBMC.Notification(%s, %s %s, 7500, %s)" % (
            'Vote saved', 'You voted', vote_value, addon.getAddonInfo('icon')))


def voteEpisode (params):
    vote_list = ['Don\'t Vote', '10', '9', '8', '7', '6', '5', '4', '3', '2', '1', '0']
    myVote = xbmcgui.Dialog().select('myVote', vote_list)
    if myVote == -1:
        return
    elif myVote != 0:
        vote_value = str(vote_list[myVote])
        vote_type = str(4)
        ep_id = params['ep_id']
        getHtml("http://" + addon.getSetting("ipaddress") + ":" + addon.getSetting(
                "port") + "/jmmserverkodi/vote/" + addon.getSetting(
                "userid") + "/" + ep_id + "/" + vote_value + "/" + vote_type, "")
        xbmc.executebuiltin("XBMC.Notification(%s, %s %s, 7500, %s)" % (
            'Vote saved', 'You voted', vote_value, addon.getAddonInfo('icon')))


def watchedMark (params):
    episode_id = params['ep_id']
    watched = bool(params['watched'])
    watched_msg = ""
    if watched is True:
        watched_msg = "watched"
    else:
        watched_msg = "unwatched"
    xbmc.executebuiltin('XBMC.Action(ToggleWatched)')
    sync = addon.getSetting("syncwatched")
    if sync == "true":
        getHtml("http://" + addon.getSetting("ipaddress") + ":" + addon.getSetting(
                "port") + "/jmmserverkodi/watch/" + addon.getSetting("userid") + "/" + episode_id + "/" + str(watched), "")
    box = addon.getSetting("watchedbox")
    if box == "true":
        xbmc.executebuiltin("XBMC.Notification(%s, %s %s, 2000, %s)" % (
            'Watched status changed', 'Mark as ', watched_msg, addon.getAddonInfo('icon')))


# Script run from here
if validUser() is True:
    try:
        parameters = util.parseParameters()
    except:
        xbmcgui.Dialog().ok('Forced mode=2', 'ERROR - This should be fixd')
        parameters = {
            "mode": 2
        }
    try:
        mode = int(parameters["mode"])
    except:
        mode = None
    try:
        cmd = parameters['cmd']
    except:
        cmd = None

    # xbmcgui.Dialog().ok("CMD", cmd)
    # xbmcgui.Dialog().ok("PARAMETERS", str(parameters))
    if cmd is not None:
        if cmd == "voteSer":
            voteSeries(parameters)
        elif cmd == "voteEp":
            voteEpisode(parameters)
        elif cmd == "watched":
            parameters['watched'] = True
            watchedMark(parameters)
            voting = addon.getSetting("voteallways")
            if voting == "true":
                voteEpisode(parameters)
        elif cmd == "unwatched":
            parameters['watched'] = False
            watchedMark(parameters)
        elif cmd == "playlist":
            playPlaylist(parameters)
    else:
        if mode == 1:  # VIDEO
            # xbmcgui.Dialog().ok('MODE=1','MODE')
            playVideo(parameters['file'])
            # playPlaylist()
        elif mode == 2:  # DIRECTORY
            xbmcgui.Dialog().ok('MODE=2', 'MODE')
        elif mode == 3:  # SEARCH
            # xbmcgui.Dialog().ok('MODE=3','MODE')
            buildSearch(parameters['url'])
        elif mode == 4:  # TVShows
            # xbmcgui.Dialog().ok('MODE=4','MODE')
            buildTVShows(parameters)
        elif mode == 5:  # TVSeasons
            # xbmcgui.Dialog().ok('MODE=5','MODE')
            buildTVSeasons(parameters)
        elif mode == 6:  # TVEpisodes
            # xbmcgui.Dialog().ok('MODE=6','MODE')
            buildTVEpisodes(parameters)
        elif mode == 7:  # Playlist continue
            # xbmcgui.Dialog().ok('MODE=7','MODE')
            playPlaylist(parameters)
        else:
            buildMainMenu()
else:
    Error("Wrong USER")
