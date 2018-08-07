#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import re

import json
from distutils.version import LooseVersion
import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin
import xml.etree.ElementTree as Tree

if sys.version_info < (3, 0):
    from urllib2 import urlopen
    from urllib import quote, quote_plus, unquote, unquote_plus, urlencode
    from urllib2 import Request
    from urllib2 import HTTPError, URLError
    from StringIO import StringIO
else:
    # For Python 3.0 and later
    from urllib.request import urlopen
    from urllib.parse import quote, quote_plus, unquote, unquote_plus, urlencode
    from urllib.request import Request
    from urllib.error import HTTPError, URLError
    from io import StringIO, BytesIO

# __ is public, _ is protected
global __addon__
global __addonversion__
global __addonid__
global __addonname__
global __icon__
global __localize__
global __server__
global __home__
global __python_two__


__python_two__ = sys.version_info < (3, 0)
__addon__ = xbmcaddon.Addon()
__addonversion__ = __addon__.getAddonInfo('version')
__addonid__ = __addon__.getAddonInfo('id')
__addonname__ = __addon__.getAddonInfo('name')
__icon__ = __addon__.getAddonInfo('icon')
__localize__ = __addon__.getLocalizedString
__server__ = "http://" + __addon__.getSetting("ipaddress") + ":" + __addon__.getSetting("port")




def move_position_on_list(control_list, position=0, force=False):
    """
    Move to the position in a list - use episode number for position
    Args:
        control_list: the list control
        position: the index of the item not including settings
        force: bypass setting and set position directly
    """
    if not force:
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








# json
def dbg(msg):
    """
    simple log message into kodi.log
    :param msg: the message to print to log
    :return:
    """
    xbmc.log(str(msg), xbmc.LOGDEBUG)


# json



# json

# Internal function

def head(url_in):
    try:
        urlopen(url_in)
        return True
    except HTTPError, e:
        # error('HTTPError', e.code)
        return False
    except URLError, e:
        # error('URLError', str(e.args))
        return False
    except Exception, e:
        # error('Exceptions', str(e.args))
        return False


def xml(xml_string):
    """
    return an xml tree from string with error catching
    Args:
        xml_string: the string containing the xml data

    Returns: ElementTree equivalentof Tree.XML()

    """
    e = Tree.XML(xml_string)
    if e.get('ErrorString', '') != '':
        error(e.get('ErrorString'), 'JMM Error')
    return e


def get_kodi_version():
    """
    This returns a LooseVersion instance containing the kodi version (16.0, 16.1, 17.0, etc)
    """
    version_string = xbmc.getInfoLabel('System.BuildVersion')
    version_string = version_string.split(' ')[0]
    return LooseVersion(version_string)


def kodi_jsonrpc(request):
    try:
        return_data = xbmc.executeJSONRPC(request)
        result = json.loads(return_data)
        return result
    except Exception as exc:
        error("jsonrpc_error: " + str(exc))


def get_kodi_setting_int(setting):
    try:
        parent_setting = xbmc.executeJSONRPC(
            '{"jsonrpc": "2.0", "method": "Settings.GetSettingValue", "params":' +
            '{"setting": "' + setting + '"}, "id": 1}')
        # {"id":1,"jsonrpc":"2.0","result":{"value":false}} or true if ".." is displayed on list

        result = json.loads(parent_setting)
        if "result" in result:
            if "value" in result["result"]:
                return int(result["result"]["value"])
    except Exception as exc:
        error("jsonrpc_error: " + str(exc))
    return -1





def safeName(name):
    return re.sub(r'[^a-zA-Z0-9 ]', '', name.lower()).replace(" ", "_")


def stripInvalid(name):
    return re.sub(r'[^a-zA-Z0-9 ]', ' ', name.lower())


def urlSafe(name):
    return re.sub(r'[^a-zA-Z0-9 ]', '', name.lower())


def alert(alertText):
    dialog = xbmcgui.Dialog()
    ret = dialog.ok(__addonid__, alertText)


def fakeError(alertText):
    dialog = xbmcgui.Dialog()
    ret = dialog.ok(__addonid__ + " [COLOR red]ERROR (1002)[/COLOR]", alertText)


def progressStart(title, status):
    pDialog = xbmcgui.DialogProgress()
    ret = pDialog.create(title, status)
    progressUpdate(pDialog, 1, status)
    return pDialog


def progressStop(pDialog):
    pDialog.close


def progressUpdate(pDialog, progress, status):
    pDialog.update(progress, status)


def relevanceCheck(title, animeList):
    returnList = []
    for anime in animeList:
        if title.lower() in anime.lower():
            returnList.append(anime)
    return returnList




# plugin://plugin.video.nakamori/?url=D:\\Media\\Video\\Tv Shows\\Animated\\Anime\\Okusama ga Seitokaichou! Plus!\\[HorribleSubs] Okusama ga Seitokaichou! S2 (Uncensored) - 01 [720p].mkv&mode=1&file=D:\\Media\\Video\\Tv Shows\\Animated\\Anime\\Okusama ga Seitokaichou! Plus!\\[HorribleSubs] Okusama ga Seitokaichou! S2 (Uncensored) - 01 [720p].mkv&ep_id=13500&ui_index=0?url=D:\\Media\\Video\\Tv Shows\\Animated\\Anime\\Okusama ga Seitokaichou! Plus!\\[HorribleSubs] Okusama ga Seitokaichou! S2 (Uncensored) - 02 [720p].mkv&mode=1&file=D:\\Media\\Video\\Tv Shows\\Animated\\Anime\\Okusama ga Seitokaichou! Plus!\\[HorribleSubs] Okusama ga Seitokaichou! S2 (Uncensored) - 02 [720p].mkv&ep_id=13499&ui_index=1



def addDir(name, url, mode, iconimage='DefaultTVShows.png', plot="", poster="DefaultVideo.png", filename="none",
           offset=''):
    # u=sys.argv[0]+"?url="+url+"&mode="+str(mode)+"&name="+quote_plus(name)+"&poster_file="+quote_plus(poster)+"&filename="+quote_plus(filename)
    u = sys.argv[0]
    if mode is not '':
        u = set_parameter(u, 'mode', str(mode))
    if name is not '':
        u = set_parameter(u, 'name', quote_plus(name))
    u = set_parameter(u, 'poster_file', quote_plus(poster))
    u = set_parameter(u, 'filename', quote_plus(filename))
    if offset is not '':
        u = set_parameter(u, 'offset', offset)
    if url is not '':
        u = set_parameter(u, 'url', url)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": plot})
    liz.setProperty("Poster_Image", iconimage)
    if mode is not '':
        if mode == 7:
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=False)
        else:
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    else:
        # should this even possible ? as failsafe I leave it.
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def playMedia(title, thumbnail, link, mediaType='Video'):
    """Plays a video

    Arguments:
    title: the title to be displayed
    thumbnail: the thumnail to be used as an icon and thumbnail
    link: the link to the media to be played
    mediaType: the type of media to play, defaults to Video. Known values are Video, Pictures, Music and Programs
    """
    try:
        li = xbmcgui.ListItem(label=title, iconImage=thumbnail, thumbnailImage=thumbnail, path=link)
        li.setInfo(type=mediaType, infoLabels={"Title": title})
        xbmc.Player().play(item=link, listitem=li)
    except:
        alert("Unable to play stream.")


def notify(addonId, message, timeShown=5000):
    """Displays a notification to the user
    
    Parameters:
    addonId: the current addon id
    message: the message to be shown
    timeShown: the length of time for which the notification will be shown, in milliseconds, 5 seconds by default
    """
    addon = xbmcaddon.Addon(addonId)
    xbmc.executebuiltin(
        'Notification(%s, %s, %d, %s)' % (addon.getAddonInfo('name'), message, timeShown, addon.getAddonInfo('icon')))


def showError(addonId, errorMessage):
    """
    Shows an error to the user and logs it
    
    Parameters:
    addonId: the current addon id
    message: the message to be shown
    """
    notify(addonId, errorMessage)
    xbmc.log(errorMessage, xbmc.LOGERROR)


def extractAll(text, startText, endText):
    """
    Extract all occurences of a string within text that start with startText and end with endText
    
    Parameters:
    text: the text to be parsed
    startText: the starting tokem
    endText: the ending token
    
    Returns an array containing all occurences found, with tabs and newlines removed and leading whitespace removed
    """
    result = []
    start = 0
    pos = text.find(startText, start)
    while pos != -1:
        start = pos + startText.__len__()
        end = text.find(endText, start)
        result.append(text[start:end].replace('\n', '').replace('\t', '').lstrip())
        pos = text.find(startText, end)
    return result


def extract(text, startText, endText):
    """
    Extract the first occurence of a string within text that start with startText and end with endText
    
    Parameters:
    text: the text to be parsed
    startText: the starting tokem
    endText: the ending token
    
    Returns the string found between startText and endText, or None if the startText or endText is not found
    """
    start = text.find(startText, 0)
    if start != -1:
        start = start + startText.__len__()
        end = text.find(endText, start + 1)
        if end != -1:
            return text[start:end]
    return None


def addMenuItem(caption, link, icon=None, thumbnail=None, folder=False):
    """
    Add a menu item to the xbmc GUI
    
    Parameters:
    caption: the caption for the menu item
    icon: the icon for the menu item, displayed if the thumbnail is not accessible
    thumbail: the thumbnail for the menu item
    link: the link for the menu item
    folder: True if the menu item is a folder, false if it is a terminal menu item
    
    Returns True if the item is successfully added, False otherwise
    """
    listItem = xbmcgui.ListItem(unicode(caption), iconImage=icon, thumbnailImage=thumbnail)
    listItem.setInfo(type="Video", infoLabels={"Title": caption})
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=link, listitem=listItem, isFolder=folder)


def endListing():
    """
    Signals the end of the menu listing
    """
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def replaceHTMLCodes(txt):
    return txt
