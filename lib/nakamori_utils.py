# -*- coding: utf-8 -*-

import xbmcaddon
import xbmc

from urllib.parse import urlparse, quote, unquote_plus, quote_plus, urlencode
from urllib.request import urlopen, Request
from io import BytesIO
import gzip
from urllib.error import HTTPError
import json
import time

plugin_addon = xbmcaddon.Addon('plugin.video.nakamori')


def get_data(url: str, referer, timeout: int, apikey: str):
    try:
        headers = {
            'Accept': 'application/json',
            'apikey': apikey,
        }

        if referer is not None:
            referer = quote(referer).replace('%3A', ':')
            if len(referer) > 1:
                headers['Referer'] = referer

        # enable gzip for communication if its not localhost
        if '127.0.0.1' not in url and 'localhost' not in url:
            headers['Accept-Encoding'] = 'gzip'

        # force api-version=1.0 because /Stream/ wont work.
        if '/Stream/' in url:
            headers['api-version'] = '1.0'

        req = Request(url, headers=headers)
        data = None

        response = urlopen(req, timeout=int(timeout))

        if response.info().get('Content-Encoding') == 'gzip':
            try:
                buf = BytesIO(response.read())
                f = gzip.GzipFile(fileobj=buf)
                data = f.read()
            except Exception as e:
                print('Failed to decompress.', e)
        else:
            data = response.read()
        response.close()

        if data is not None and data != '':
            stream = json.loads(data)
            if 'StatusCode' in stream:
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
                        error_msg = 'The connection was refused as unauthorized'

                    code = int(code)
                    raise HTTPError(req.get_full_url(), code, error_msg, req.headers, None)
        return data
    except Exception as ex:
        xbmc.log(' === get_data error === %s -> %s' % (url, ex), xbmc.LOGINFO)


def get_json(url_in: str, direct: bool = False, force_cache: bool = False, cache_time: int = 0, new_apikey: str = None):
    try:
        timeout = plugin_addon.getSettingInt(id='timeout')
        if new_apikey is not None:
            plugin_addon.setSettingString(id='apikey', value=new_apikey)

        apikey = plugin_addon.getSetting(id='apikey')

        # if cache is disabled, force direct connection
        if not plugin_addon.getSettingBool('enableCache'):
            direct = True

        if direct and not force_cache:
            body = get_data(url_in, None, timeout, apikey)
        else:
            from lib import cache
            xbmc.log('-------------> Getting a Cached Response ---', xbmc.LOGINFO)
            db_row = cache.get_data_from_cache(url_in)
            if db_row is not None:
                valid_until = cache_time if cache_time > 0 else int(plugin_addon.getSetting('expireCache'))
                expire_second = time.time() - float(db_row[1])
                if expire_second > valid_until:
                    # expire, get new date
                    body = get_data(url_in, None, timeout, apikey)
                    cache.remove_cache(url_in)
                    cache.add_cache(url_in, body)
                else:
                    body = db_row[0]
            else:
                body = get_data(url_in, None, timeout, apikey)
                cache.add_cache(url_in, body)
    except Exception as ex:
        xbmc.log(' ========= ERROR JSON ============  %s' % ex, xbmc.LOGINFO)
        body = None
    return body


def post_json(url_in: str, body: str, custom_timeout: int = plugin_addon.getSettingInt('timeout')):
    """
    Push data to server using 'POST' method
    :param url_in:
    :param body:
    :param custom_timeout: if not given timeout from plugin setting will be used
    :return:
    """
    if len(body) > 3:
        proper_body = '{' + body + '}'
        return post_data(url=url_in, data_in=proper_body, custom_timeout=custom_timeout)
    else:
        return None


def post_data(url: str, data_in: str, custom_timeout=plugin_addon.getSettingInt('timeout')):
    """
    Send a message to the server and wait for a response
    Args:
        url: the URL to send the data to
        data_in: the message to send (in json)
        custom_timeout: if not given timeout from plugin setting will be used
    Returns: The response from the server
    """

    if data_in is None:
        data_in = b''
    else:
        data_in = data_in.encode(encoding='utf-8')

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    apikey = plugin_addon.getSetting('apikey')
    if apikey is not None and apikey != '':
        headers['apikey'] = apikey

    data_out = None
    try:
        req = Request(url, data_in, headers)

        response = urlopen(req, timeout=custom_timeout)
        data_out = response.read()
        response.close()
        if data_out is not None and data_out != '':
            stream = json.loads(data_out)
            if 'StatusCode' in stream:
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
                        error_msg = 'The connection was refused as unauthorized'

                    code = int(code)
                    raise HTTPError(req.get_full_url(), code, error_msg, req.headers, None)
    except Exception as ex:
        xbmc.log('==== post_data error ==== %s ' % ex, xbmc.LOGINFO)

    return data_out
