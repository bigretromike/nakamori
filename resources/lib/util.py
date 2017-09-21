#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import urllib
import urllib2
import re
import gzip
import traceback
import json
import time
from distutils.version import LooseVersion

import collections

import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin

from StringIO import StringIO
import xml.etree.ElementTree as Tree

import resources.lib.cache as cache

# get addon info
__addon__ = xbmcaddon.Addon(id='plugin.video.nakamori')
__addonversion__ = __addon__.getAddonInfo('version')
__addonid__ = __addon__.getAddonInfo('id')
__addonname__ = __addon__.getAddonInfo('name')
__icon__ = __addon__.getAddonInfo('icon')
__localize__ = __addon__.getLocalizedString
_server_ = "http://" + __addon__.getSetting("ipaddress") + ":" + __addon__.getSetting("port")
ADDON_ID = 'plugin.video.nakamori'

try:
    # kodi 17+
    UA = xbmc.getUserAgent()
except:
    # kodi < 17
    UA = 'Mozilla/6.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.5) Gecko/2008092417 Firefox/3.0.3'
pDialog = ''


def valid_user():
    """
    Logs into the server and stores the apikey, then checks if the userid is valid
    reset apikey if user enters new login info
    if apikey is present login should be empty as its not needed anymore
    :return: bool True if all completes successfully
    """

    if __addon__.getSetting("apikey") != "" and __addon__.getSetting("login") == "":
        return True
    else:
        xbmc.log('-- apikey empty --')
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
    if window_name == 'Continue Watching (SYSTEM)':
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


def populate_tag_setting_flags():
    """
    Get user settings from local Kodi, and use them with Nakamori
    :return: setting_flags
    """
    tag_setting_flags = 0
    tag_setting_flags = tag_setting_flags | (0b00001 if __addon__.getSetting('hideMiscTags') == 'true' else 0)
    tag_setting_flags = tag_setting_flags | (0b00010 if __addon__.getSetting('hideArtTags') == 'true' else 0)
    tag_setting_flags = tag_setting_flags | (0b00100 if __addon__.getSetting('hideSourceTags') == 'true' else 0)
    tag_setting_flags = tag_setting_flags | (0b01000 if __addon__.getSetting('hideUsefulMiscTags') == 'true' else 0)
    tag_setting_flags = tag_setting_flags | (0b10000 if __addon__.getSetting('hideSpoilerTags') == 'true' else 0)
    return tag_setting_flags


def refresh():
    """
    Refresh and re-request data from server
    refresh watch status as we now mark episode and refresh list so it show real status not kodi_cached
    Allow time for the ui to reload
    """
    xbmc.executebuiltin('Container.Refresh')
    xbmc.sleep(int(__addon__.getSetting('refresh_wait')))


def dump_dictionary(details, name):
    if __addon__.getSetting("spamLog") == 'true':
        if details is not None:
            xbmc.log("---- " + name + ' ----', xbmc.LOGWARNING)

            for i in details:
                temp_log = ""
                a = details.get(encode(i))
                if a is None:
                    temp_log = "\'unset\'"
                elif isinstance(a, collections.Iterable):
                    # easier for recursion and pretty
                    temp_log = json.dumps(a, sort_keys=True, indent=4, separators=(',', ': '))
                else:
                    temp_log = str(a)
                xbmc.log("-" + str(i) + "- " + temp_log, xbmc.LOGWARNING)


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


# json
def dbg(msg):
    """
    simple log message into kodi.log
    :param msg: the message to print to log
    :return:
    """
    xbmc.log(str(msg), xbmc.LOGDEBUG)


# json
def safeInt(object_body):
    """
    safe convert type to int to avoid NoneType
    :param object_body:
    :return: int
    """
    try:
        if object_body is not None and object_body != '':
            return int(object_body)
        else:
            return 0
    except:
        return 0


# json
def error(msg, error_type='Error', silent=False):
    """
    Log and notify the user of an error
    Args:
        msg: the message to print to log and user notification
        error_type: Type of Error
        silent: disable visual notification
    """
    xbmc.log("Nakamori " + str(__addonversion__) + " id: " + str(__addonid__), xbmc.LOGERROR)
    xbmc.log('---' + msg + '---', xbmc.LOGERROR)
    key = sys.argv[0]
    if len(sys.argv) > 2 and sys.argv[2] != '':
        key += sys.argv[2]
    xbmc.log('On url: ' + urllib.unquote(key), xbmc.LOGERROR)
    try:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        if exc_type is not None and exc_obj is not None and exc_tb is not None:
            xbmc.log(str(exc_type) + " at line " + str(exc_tb.tb_lineno) + " in file " + str(
                os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]), xbmc.LOGERROR)
            traceback.print_exc()
    except Exception as e:
        xbmc.log("There was an error catching the error. WTF.", xbmc.LOGERROR)
        xbmc.log("The error message: " + str(e), xbmc.LOGERROR)
        traceback.print_exc()
    if not silent:
        xbmc.executebuiltin('XBMC.Notification(%s, %s %s, 2000, %s)' % (error_type, ' ', msg, __addon__.getAddonInfo('icon')))


def parse_possible_error(data, data_type):
    if data_type == 'json':
        stream = json.loads(data)
        if "StatusCode" in stream:
            code = stream.get('StatusCode')
            if code != '200':
                error_msg = code
                if code == '500':
                    error_msg = 'Server Error'
                elif code == '404':
                    error_msg = 'Invalid URL: Endpoint not Found in Server'
                elif code == '503':
                    error_msg = 'Service Unavailable: Check netsh http'
                elif code == '401' or code == '403':
                    error_msg = 'The was refused as unauthorized'
                error(error_msg, error_type='Network Error: ' + code)
                if stream.get('Details', '') != '':
                    xbmc.log(encode(stream.get('Details')), xbmc.LOGERROR)
    elif data_type == 'xml':
        stream = xml(data)
        if stream.get('Code', '') != '':
            code = stream.get('Code')
            if code != '200':
                error_msg = code
                if code == '500':
                    error_msg = 'Server Error'
                elif code == '404':
                    error_msg = 'Invalid URL: Endpoint not Found in Server'
                elif code == '503':
                    error_msg = 'Service Unavailable: Check netsh http'
                elif code == '401' or code == '403':
                    error_msg = 'The was refused as unauthorized'
                error(error_msg, error_type='Network Error: ' + code)
                if stream.get('Message', '') != '':
                    xbmc.log(encode(stream.get('Message')), xbmc.LOGERROR)


# Internal function
# json
def get_json(url_in, direct=False):
    body = ""
    if direct:
        body = get_data(url_in, None, "json")
        # xbmcgui.Dialog().ok("direct", str(body))
    else:
        if __addon__.getSetting("enableCache") == "true":
            # xbmcgui.Dialog().ok("cache", "ENABLED")
            # xbmcgui.Dialog().ok("cache url", str(url_in))
            db_row = cache.check_in_database(url_in)
            if db_row is None:
                db_row = 0
            # xbmcgui.Dialog().ok("cache db_row", str(db_row))
            if db_row > 0:
                expire_second = time.time() - float(db_row)
                if expire_second > int(__addon__.getSetting("expireCache")):
                    # expire, get new date
                    # xbmcgui.Dialog().ok("cache", "data expired")
                    body = get_data(url_in, None, "json")
                    params = {}
                    params['extras'] = 'single-delete'
                    params['name'] = url_in
                    cache.remove_cache(params)
                    cache.add_cache(url_in, json.dumps(body))
                else:
                    # xbmcgui.Dialog().ok("cache", "not expire")
                    body = cache.get_data_from_cache(url_in)
                    # xbmcgui.Dialog().ok("cache-body", str(body))
                    # body = str(body)
                    # why I get response as ({},) I dont know i leave this as
                    # body = body[4:]
                    # body = body[:-4]
                    # xbmcgui.Dialog().ok("cache-body", str(body))
            else:
                # xbmcgui.Dialog().ok("cache", "not cached")
                body = get_data(url_in, None, "json")
                cache.add_cache(url_in, json.dumps(body))
        else:
            body = get_data(url_in, None, "json")
    return body


# legacy
def get_xml(url_in):
    # return get_data(url_in, None, "xml")
    return get_data(url_in, None, "")


# json + legacy
def get_data(url_in, referer, data_type):
    """
    Send a message to the server and wait for a response
    Args:
        url_in: the URL to get data from
        referer: currently not used always should be None
        data_type: extension for url (.json or .xml) to force return type

    Returns: The response from the server in forced type (.json or .xml)
    """
    try:
        if data_type != "json":
            data_type = "xml"

        url = url_in

        req = urllib2.Request(encode(url))
        req.add_header('Accept', 'application/' + data_type)
        req.add_header('apikey', __addon__.getSetting("apikey"))

        if referer is not None:
            referer = urllib2.quote(encode(referer)).replace("%3A", ":")
            if len(referer) > 1:
                req.add_header('Referer', referer)
        use_gzip = __addon__.getSetting("use_gzip")
        if "127.0.0.1" not in url and "localhost" not in url:
            if use_gzip == "true":
                req.add_header('Accept-encoding', 'gzip')
        data = None
        try:
            response = urllib2.urlopen(req, timeout=int(__addon__.getSetting('timeout')))
            if response.info().get('Content-Encoding') == 'gzip':
                try:
                    buf = StringIO(response.read())
                    f = gzip.GzipFile(fileobj=buf)
                    data = f.read()
                except Exception as ex:
                    error('Decompresing gzip respond failed', str(ex))
            else:
                data = response.read()
            response.close()
        except Exception as ex:
            xbmc.log("url: " + str(url), xbmc.LOGERROR)
            error('Connection Failed', str(ex))
            data = None
    except Exception as ex:
        error('Get_Data Error', str(ex))
        data = None

    if data is not None and data != '':
        parse_possible_error(data, data_type)
    return data


def post_dict(url, body):
    json = ''
    try:
        json = json.dumps(body)
    except:
        error('Failed to send data')
    post_data(url, json)


# json
def post_json(url_in, body):
    if len(body) > 3:
        proper_body = '{' + body + '}'
        return post_data(url_in, proper_body)
    else:
        return None


# json
def post_data(url, data_in):
    """
    Send a message to the server and wait for a response
    Args:
        url: the URL to send the data to
        data_in: the message to send (in json)

    Returns: The response from the server
    """
    if data_in is not None:
        req = urllib2.Request(encode(url), data_in, {'Content-Type': 'application/json'})
        req.add_header('apikey', __addon__.getSetting("apikey"))
        req.add_header('Accept', 'application/json')
        data_out = None
        try:
            response = urllib2.urlopen(req, timeout=int(__addon__.getSetting('timeout')))
            data_out = response.read()
            response.close()
        except Exception as ex:
            error('url:' + str(url))
            error('Connection Failed in post_data', str(ex))
        return data_out
    else:
        error('post_data body is None')
        return None


# legacy
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


def decode(i=''):
    """
    decode a string to UTF-8
    Args:
        i: string to decode

    Returns: decoded string

    """
    try:
        if isinstance(i, str):
            return i.decode('utf-8')
        elif isinstance(i, unicode):
            return i
    except:
        error("Unicode Error", error_type='Unicode Error')
        return ''


def encode(i=''):
    """
    encode a string from UTF-8
    Args:
        i: string to encode

    Returns: encoded string

    """
    try:
        if isinstance(i, str):
            return i
        elif isinstance(i, unicode):
            return i.encode('utf-8')
    except:
        error("Unicode Error", error_type='Unicode Error')
        return ''


def post(url, data, headers={}):
    postdata = urllib.urlencode(data)
    req = urllib2.Request(url, postdata, headers)
    req.add_header('User-Agent', UA)
    response = urllib2.urlopen(req)
    data = response.read()
    response.close()
    return data


def get_server_status():
    """
    Try to query server for version, if kodi get version respond then shoko server is running
    :return: bool
    """
    try:
        if get_version() != LooseVersion('0.0'):
            return True
        else:
            return False
    except:
        return False


# json - ok
def get_version():
    legacy = LooseVersion('0.0')
    json_file = get_json("http://" + __addon__.getSetting("ipaddress") + ":" + __addon__.getSetting("port") + "/api/version", direct=True)
    if json_file is None:
        return legacy
    try:
        data = json.loads(json_file)
    except:
        return legacy

    for module in data:
        if module["name"] == "server":
            version = module["version"]
            break

    if version != '':
        return LooseVersion(version)
    return legacy


def getURL(url, header):
    try:
        req = urllib2.Request(url, headers=header)
        response = urllib2.urlopen(req)
        if response and response.getcode() == 200:
            if response.info().get('Content-Encoding') == 'gzip':
                buf = StringIO.StringIO(response.read())
                gzip_f = gzip.GzipFile(fileobj=buf)
                content = gzip_f.read()
            else:
                content = response.read()
            content = content.decode('utf-8', 'ignore')
            return content
        return False
    except:
        xbmc.log('Error Loading URL (Error: ' + str(response.getcode()) +
                 ' Encoding:' + response.info().get('Content-Encoding') + '): ' + url, xbmc.LOGERROR)
        xbmc.log('Content: ' + response.read(), xbmc.LOGERROR)
        return False


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


def get_kodi_setting_bool(setting):
    try:
        parent_setting = xbmc.executeJSONRPC(
            '{"jsonrpc": "2.0", "method": "Settings.GetSettingValue", "params":' +
            '{"setting": "' + setting + '"}, "id": 1}')
        # {"id":1,"jsonrpc":"2.0","result":{"value":false}} or true if ".." is displayed on list

        result = json.loads(parent_setting)
        if "result" in result:
            if "value" in result["result"]:
                return result["result"]["value"]
    except Exception as exc:
        error("jsonrpc_error: " + str(exc))
    return False


def safeName(name):
    return re.sub(r'[^a-zA-Z0-9 ]', '', name.lower()).replace(" ", "_")


def stripInvalid(name):
    return re.sub(r'[^a-zA-Z0-9 ]', ' ', name.lower())


def urlSafe(name):
    return re.sub(r'[^a-zA-Z0-9 ]', '', name.lower())


def alert(alertText):
    dialog = xbmcgui.Dialog()
    ret = dialog.ok(ADDON_ID, alertText)


def fakeError(alertText):
    dialog = xbmcgui.Dialog()
    ret = dialog.ok(ADDON_ID + " [COLOR red]ERROR (1002)[/COLOR]", alertText)


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


def set_parameter(url, parameter, value):
    value = str(value)
    if value is None or value == '':
        if '?' not in url:
            return url
        array1 = url.split('?')
        if (parameter+'=') not in array1[1]:
            return url
        url = array1[0] + '?'
        array2 = array1[1].split('&')
        for key in array2:
            array3 = key.split('=')
            if array3[0] == parameter:
                continue
            url += array3[0] + '=' + array3[1] + '&'
        return url[:-1]
    value = urllib.quote_plus(value)
    if '?' not in url:
        return url + '?' + parameter + '=' + value

    array1 = url.split('?')
    if (parameter+'=') not in array1[1]:
        return url + "&" + parameter + '=' + value

    url = array1[0] + '?'
    array2 = array1[1].split('&')
    for key in array2:
        array3 = key.split('=')
        if array3[0] == parameter:
            array3[1] = value
        url += array3[0] + '=' + array3[1] + '&'
    return url[:-1]


# plugin://plugin.video.nakamori/?url=D:\\Media\\Video\\Tv Shows\\Animated\\Anime\\Okusama ga Seitokaichou! Plus!\\[HorribleSubs] Okusama ga Seitokaichou! S2 (Uncensored) - 01 [720p].mkv&mode=1&file=D:\\Media\\Video\\Tv Shows\\Animated\\Anime\\Okusama ga Seitokaichou! Plus!\\[HorribleSubs] Okusama ga Seitokaichou! S2 (Uncensored) - 01 [720p].mkv&ep_id=13500&ui_index=0?url=D:\\Media\\Video\\Tv Shows\\Animated\\Anime\\Okusama ga Seitokaichou! Plus!\\[HorribleSubs] Okusama ga Seitokaichou! S2 (Uncensored) - 02 [720p].mkv&mode=1&file=D:\\Media\\Video\\Tv Shows\\Animated\\Anime\\Okusama ga Seitokaichou! Plus!\\[HorribleSubs] Okusama ga Seitokaichou! S2 (Uncensored) - 02 [720p].mkv&ep_id=13499&ui_index=1

def searchBox():
    """
    Shows a keyboard, and returns the text entered
    :return: the text that was entered
    """
    keyb = xbmc.Keyboard('', 'Enter search text')
    keyb.doModal()
    searchText = ''

    if keyb.isConfirmed():
        searchText = keyb.getText()
    return searchText


def addDir(name, url, mode, iconimage='DefaultTVShows.png', plot="", poster="DefaultVideo.png", filename="none",
           offset=''):
    # u=sys.argv[0]+"?url="+url+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&poster_file="+urllib.quote_plus(poster)+"&filename="+urllib.quote_plus(filename)
    u = sys.argv[0]
    if mode is not '':
        u = set_parameter(u, 'mode', str(mode))
    if name is not '':
        u = set_parameter(u, 'name', urllib.quote_plus(name))
    u = set_parameter(u, 'poster_file', urllib.quote_plus(poster))
    u = set_parameter(u, 'filename', urllib.quote_plus(filename))
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


def parseParameters(input_string=sys.argv[2]):
    """Parses a parameter string starting at the first ? found in inputString
    
    Argument:
    input_string: the string to be parsed, sys.argv[2] by default
    
    Returns a dictionary with parameter names as keys and parameter values as values
    """
    parameters = {}
    p1 = input_string.find('?')
    if p1 >= 0:
        split_parameters = input_string[p1 + 1:].split('&')
        for name_value_pair in split_parameters:
            # xbmc.log("parseParameter detected Value: " + str(name_value_pair))
            if (len(name_value_pair) > 0) & ("=" in name_value_pair):
                pair = name_value_pair.split('=')
                key = pair[0]
                value = decode(urllib.unquote_plus(pair[1]))
                parameters[key] = value
    return parameters


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


def request(url, headers={}):
    debug('request: %s' % url)
    req = urllib2.Request(url, headers=headers)
    req.add_header('User-Agent', UA)
    response = urllib2.urlopen(req)
    data = response.read()
    response.close()
    debug('len(data) %s' % len(data))
    return data


def debug(text):
    xbmc.log(str([text]), xbmc.LOGDEBUG)


def makeLink(params, baseUrl=sys.argv[0]):
    """
    Build a link with the specified base URL and parameters
    
    Parameters:
    params: the params to be added to the URL
    BaseURL: the base URL, sys.argv[0] by default
    """
    return baseUrl + '?' + urllib.urlencode(
        dict([encode(k), encode(decode(v))] for k, v in params.items()))


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


def makeAscii(data):
    # log(repr(data), 5)
    # if sys.hexversion >= 0x02050000:
    #        return data

    try:
        return data.encode('ascii', "ignore")
    except:
        # log("Hit except on : " + repr(data))
        s = u""
        for i in data:
            try:
                i.encode("ascii", "ignore")
            except:
                # log("Can't convert character", 4)
                continue
            else:
                s += i

        # log(repr(s), 5)
        return s


def replaceHTMLCodes(txt):
    return txt


# This function handles stupid utf handling in python.
def makeUTF8(data):
    # log(repr(data), 5)
    # return data
    try:
        return data.decode('utf8', 'xmlcharrefreplace')  # was 'ignore'
    except:
        # log("Hit except on : " + repr(data))
        s = u""
        for i in data:
            try:
                i.decode("utf8", "xmlcharrefreplace")
            except:
                # log("Can't convert character", 4)
                continue
            else:
                s += i
        # log(repr(s), 5)
        return s
