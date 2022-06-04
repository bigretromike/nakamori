# -*- coding: utf-8 -*-
import datetime
import time
import json
import os
import re
from lib.kodi_utils import debug
from urllib.error import HTTPError
from models.kodi_models import make_text_nice

import xbmc
import xbmcaddon
import xbmcvfs
from urllib import request

ADDON = xbmcaddon.Addon(id='plugin.video.nakamori')
x = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))
x = os.path.join(x, 'json')
x = os.path.join(x, '%s' % ADDON.getSetting('url_type'))
is_seasons = True
if ADDON.getSetting('url_type') == 'calendar':
    is_seasons = False

if not os.path.exists(x):
    os.makedirs(x)


def pack_json(new_list):
    fake_json = dict()
    fake_json['art'] = {'thumb': [], 'banner': [], 'fanart': []}
    fake_json['id'] = 0
    fake_json['name'] = 'Airing Soon'
    fake_json['roles'] = None
    fake_json['summary'] = ''
    fake_json['tags'] = None
    fake_json['type'] = 'group'
    fake_json['url'] = ''
    fake_json['series'] = new_list
    fake_json['size'] = len(new_list)
    return fake_json


def process_month(year, month, day, day_already_processed, url):
    debug(f'== process_month == {year}/{month}/{day} : already = {day_already_processed} - url={url} ')
    day_is = datetime.date(year, month, day)
    week = day_is.isocalendar()[1]
    if is_seasons:
        y = os.path.join(x, '%s-%02d.json' % (year, month))
    else:
        y = os.path.join(x, '%s-%02d.json' % (year, week))

    if os.path.exists(y):
        # more than 24h
        if int(time.time()) - int(os.path.getmtime(y)) > 86400:
            os.remove(y)

    if not os.path.exists(y) and not download_external_source(url, year, month, week):
        return None
    if not os.path.exists(y):
        debug('=== 404 calendar and no file')
        return None

    content = open(y, 'r').read()
    pre_body = json.loads(content)
    body = []

    for pre in pre_body:
        # eh.spam('process_month.pre item: %s' % pre)
        if int(pre['air'][8:10]) >= day:
            if pre['air'] not in day_already_processed:
                if len(day_already_processed) > 7:
                    break
                day_already_processed.append(pre['air'])
            body.append(pre)

    return body


def return_only_few(when: str, offset: int = 0, url: str = '', day_limits: int = 7, go_back_in_time: bool = False):
    # TODO do I need offset? should I use offset?
    time_machine = 1
    if go_back_in_time:
        time_machine = -1
    offset = int(offset)
    when = str(when)
    if len(when) == 8:
        year = int(when[0:4])
        month = int(when[4:6])
        day = int(when[6:8])
    else:
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        day = datetime.datetime.now().day

    day_already_processed = []
    body = process_month(year, month, day, day_already_processed, url)

    if body is not None:
        if len(day_already_processed) < day_limits:
            # process next month
            month += time_machine
            day = 1
            if month == 13:
                month = 1
                year += time_machine
            next_body = process_month(year, month, day, day_already_processed, url)
            if next_body is not None:
                body = body + next_body
        return json.dumps(pack_json(body))
    else:
        return None


def download_external_source(url, year=datetime.datetime.now().year, month=datetime.datetime.now().month, week=datetime.datetime.now().isocalendar()[1]):
    # eh.spam('download_external_source(url=%s, year=%s, month=%s, weekofyear=%s)' % (url, year, month, week))
    if is_seasons:
        y = os.path.join(x, '%s-%02d-tmp.json' % (year, month))
        url = url % (year, month)
        z = os.path.join(x, '%s-%02d.json' % (year, month))
    else:
        y = os.path.join(x, '%s-%02d-tmp.json' % (year, week))
        url = url % (year, week)
        z = os.path.join(x, '%s-%02d.json' % (year, week))

    debug('URL===> ' + url)
    try:
        content = request.urlopen(url).read().decode('utf-8')

        if os.path.exists(y):
            os.remove(y)
        open(y, 'wb').write(content.encode('utf-8'))
        try:
            response = json.loads(content)
            series_list = []
            series_item = {}
            for dates in response.get('calendar'):
                for series in response['calendar'][dates]:
                    try:
                        img = ''
                        x1 = ''
                        number = 0
                        img_number = re.search(r'65x100\/(.*)\.jpg-thumb', str(series['image']))
                        if img_number is None:
                            if "images/150" in str(series['image']):
                                # "images/150/221366.jpg-thumb.jpg"
                                img_number = re.search(r'images\/150\/(.*)\.jpg-thumb', str(series['image']))
                                number = img_number.group(1)
                                x1 = 'images/65x100/' + number + '.jpg-thumb.jpg'
                            elif "thumbs/150" in str(series['image']):
                                img_number = re.search(r'thumbs\/150\/(.*)\.jpg-thumb', str(series['image']))
                                number = img_number.group(1)
                                x1 = 'thumbs/65x100/' + number + '.jpg-thumb.jpg'
                        if img_number is not None:
                            if number == 0:
                                number = img_number.group(1)
                            if x1 == '':
                                x1 = 'thumbs/65x100/' + number + '.jpg-thumb.jpg'
                            x2 = number + '.jpg'
                            img = str(series['image']).replace(x1, x2)

                        series_item['aid'] = series['aid']
                        series_item['air'] = dates
                        series_item['date'] = dates
                        series_item['art'] = {'thumb': [{'index': 0, 'url': img}], 'banner': [], 'fanart': []}
                        series_item['id'] = -1
                        series_item['ismovie'] = 0
                        series_item['name'] = series['name']
                        series_item['rating'] = 0
                        series_item['roles'] = []
                        series_item['size'] = 0
                        series_item['summary'] = make_text_nice(series['desc'])
                        series_item['tags'] = None
                        series_item['titles'] = [{'Language': 'x-jat', 'Title': series['name'], 'Type': 'main'},
                                                 {'Language': 'ja', 'Title': series['kanji'], 'Type': 'official'}]
                        series_item['type'] = 'serie'
                        series_item['votes'] = 0
                        series_item['year'] = year
                        # series['general']
                        series_list.append(series_item)
                        series_item = {}  # do this because shit get duplicate ?!
                    except Exception as e:
                        # noinspection PyUnresolvedReferences
                        xbmc.log('Error in download_external_source.series: %s' % e, xbmc.LOGERROR)

            if os.path.exists(z):
                os.remove(z)
            series_list = sorted(series_list, key=lambda i: (i['air'], i['name']))
            con = json.dumps(series_list)
            open(z, 'wb').write(con.encode('utf-8'))
            # clean tmp
            os.remove(y)
            return True
        except Exception as es:
            xbmc.log('error: ' + str(es), xbmc.LOGERROR)
            return False
    except HTTPError as ex:
        if ex.code == 404:
            debug('calendar data was found more, 404')
            return True
        else:
            return False
