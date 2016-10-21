import os
import sys, urllib, urllib2, re, gzip
import traceback

import xbmc, xbmcgui, xbmcaddon, xbmcplugin
from StringIO import StringIO
import xml.etree.ElementTree as Tree

# get addon info
__addon__ = xbmcaddon.Addon(id='plugin.video.nakamori')
__addonversion__ = __addon__.getAddonInfo('version')
__addonid__ = __addon__.getAddonInfo('id')
__addonname__ = __addon__.getAddonInfo('name')
__icon__ = __addon__.getAddonInfo('icon')
__localize__ = __addon__.getLocalizedString

ADDON_ID = 'plugin.video.nakamori'
UA = 'Mozilla/6.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.5) Gecko/2008092417 Firefox/3.0.3'
pDialog = ''


def error(msg, error_type='Error'):
    """
    Log and notify the user of an error
    Args:
        msg: the message to print to log and user notification
        error_type: Type of Error
    """
    xbmc.log("Nakamori " + str(__addonversion__) + " id: " + str(__addonid__))
    xbmc.log('---' + msg + '---', xbmc.LOGERROR)
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

    xbmc.executebuiltin('XBMC.Notification(%s, %s %s, 2000, %s)' % (error_type, ' ', msg, __addon__.getAddonInfo('icon')))


def parse_possible_error(data, data_type):
    if data_type == 'json':
        # TODO actually support this
        pass
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
def get_json(url_in):
    return get_data(url_in, None, "json")


def get_xml(url_in):
    # return get_data(url_in, None, "xml")
    return get_data(url_in, None, "")


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
        if not url_in.lower().startswith("http://" + __addon__.getSetting("ipaddress") + ":"
                                                 + __addon__.getSetting("port")):
            if url_in.lower().startswith('/jmmserverkodi'):
                url_in = 'http://' + __addon__.getSetting("ipaddress") + ":" \
                         + __addon__.getSetting("port") + url_in
            if url_in.lower().startswith(':'):
                url_in = 'http://' + __addon__.getSetting("ipaddress") + url_in

        # TODO: Remove with get_legacy
        if len(data_type) > 1:
            url = url_in + "." + data_type
        else:
            url = url_in
            data_type = "xml"
        req = urllib2.Request(encode(url),
                              headers={'Accept': 'application/' + data_type,
                                       'apikey': __addon__.getSetting("apikey")})
        if referer is not None:
            referer = urllib2.quote(encode(referer)).replace("%3A", ":")
            if len(referer) > 1:
                req.add_header('Referer', referer)
        use_gzip = __addon__.getSetting("use_gzip")
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
            xbmc.log("url: " + str(url))
            error('Connection Failed', str(ex))
            data = None
    except Exception as ex:
        error('Get_Data Error', str(ex))
        data = None

    if data is not None:
        parse_possible_error(data, data_type)
    return data


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
        xbmc.log('Error Loading URL (Error: ' + str(response.getcode()) + ' Encoding:' + response.info().get(
            'Content-Encoding') + '): ' + url, xbmc.LOGERROR)
        xbmc.log('Content: ' + response.read(), xbmc.LOGERROR)
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


def error(heading, message):
    dialog = xbmcgui.Dialog()
    dialog.notification(heading, message, xbmcgui.NOTIFICATION_ERROR, 5000)


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
    value = urllib.quote_plus(value)
    if '?' not in url:
        return url + '?' + parameter + '=' + value

    array1 = url.split('?')
    if ('&' + parameter) not in array1[1]:
        return url + array1[1] + "&" + parameter + '=' + value

    url = array1[0] + '?'
    array2 = array1[1].split('&')
    for key in array2:
        array3 = key.split('=')
        if array3[0] == parameter:
            array3[1] = value
        url += array3[0] + '=' + array3[1] + '&'
    return url[:-1]


#plugin://plugin.video.nakamori/?url=D:\\Media\\Video\\Tv Shows\\Animated\\Anime\\Okusama ga Seitokaichou! Plus!\\[HorribleSubs] Okusama ga Seitokaichou! S2 (Uncensored) - 01 [720p].mkv&mode=1&file=D:\\Media\\Video\\Tv Shows\\Animated\\Anime\\Okusama ga Seitokaichou! Plus!\\[HorribleSubs] Okusama ga Seitokaichou! S2 (Uncensored) - 01 [720p].mkv&ep_id=13500&ui_index=0?url=D:\\Media\\Video\\Tv Shows\\Animated\\Anime\\Okusama ga Seitokaichou! Plus!\\[HorribleSubs] Okusama ga Seitokaichou! S2 (Uncensored) - 02 [720p].mkv&mode=1&file=D:\\Media\\Video\\Tv Shows\\Animated\\Anime\\Okusama ga Seitokaichou! Plus!\\[HorribleSubs] Okusama ga Seitokaichou! S2 (Uncensored) - 02 [720p].mkv&ep_id=13499&ui_index=1

def searchBox():
    """
    Shows a keyboard, and returns the text entered
    :return: the text that was entered
    """
    keyb = xbmc.Keyboard('', 'Enter search text')
    keyb.doModal()
    searchText = ''
    if (keyb.isConfirmed()):
        searchText = keyb.getText()
    if searchText != '':
        return searchText


def addDir(name, url, mode, iconimage, plot="", poster="DefaultVideo.png", filename="none"):
    # u=sys.argv[0]+"?url="+url+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&poster_file="+urllib.quote_plus(poster)+"&filename="+urllib.quote_plus(filename)
    u = sys.argv[0]
    u = set_parameter(u, 'mode', str(mode))
    u = set_parameter(u, 'name', urllib.quote_plus(name))
    u = set_parameter(u, 'poster_file', urllib.quote_plus(poster))
    u = set_parameter(u, 'filename', urllib.quote_plus(filename))
    u = set_parameter(u, 'url', url)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": plot})
    liz.setProperty("Poster_Image", iconimage)
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


def parseParameters(inputString=sys.argv[2]):
    """Parses a parameter string starting at the first ? found in inputString
    
    Argument:
    inputString: the string to be parsed, sys.argv[2] by default
    
    Returns a dictionary with parameter names as keys and parameter values as values
    """
    parameters = {}
    p1 = inputString.find('?')
    if p1 >= 0:
        splitParameters = inputString[p1 + 1:].split('&')
        for nameValuePair in splitParameters:
            if (len(nameValuePair) > 0):
                pair = nameValuePair.split('=')
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


### Define dialogs
def dialog_msg(action,
               percentage=0,
               line0='',
               line1='',
               line2='',
               line3='',
               background=False,
               nolabel="no",
               yeslabel="tak_nie"):
    # Fix possible unicode errors
    line0 = line0.encode('utf-8', 'ignore')
    line1 = line1.encode('utf-8', 'ignore')
    line2 = line2.encode('utf-8', 'ignore')
    line3 = line3.encode('utf-8', 'ignore')

    # Dialog logic
    __addonname__ = "XYZ"
    if not line0 == '':
        line0 = __addonname__ + line0
    else:
        line0 = __addonname__
    if not background:
        if action == 'create':
            dialog.create(__addonname__, line1, line2, line3)
        if action == 'update':
            dialog.update(percentage, line1, line2, line3)
        if action == 'close':
            dialog.close()
        if action == 'iscanceled':
            if dialog.iscanceled():
                return True
            else:
                return False
        if action == 'okdialog':
            xbmcgui.Dialog().ok(line0, line1, line2, line3)
        if action == 'yesno':
            return xbmcgui.Dialog().yesno(line0, line1, line2, line3, nolabel, yeslabel)
    if background:
        if (action == 'create' or action == 'okdialog'):
            if line2 == '':
                msg = line1
            else:
                msg = line1 + ': ' + line2
            xbmc.executebuiltin("XBMC.Notification(%s, %s, 7500, %s)" % (line0, msg, __icon__))
