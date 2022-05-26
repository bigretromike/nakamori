# -*- coding: utf-8 -*-
import time
import json
import datetime
import _strptime  # fix for import lockis held by another thread.
import re
import os

#from nakamori_utils import script_utils
#from nakamori_utils import model_utils
#from proxy.python_version_proxy import python_proxy as pyproxy
import xbmcgui
import xbmc
import xbmcaddon
import xbmcvfs

from models.kodi_models import *
from api.shoko.v2 import api2models

#from nakamori_utils.globalvars import *

# noinspection PyUnresolvedReferences
try:
    from PIL import ImageFont, ImageDraw, Image
except ImportError:
    pass
import textwrap

ADDON = xbmcaddon.Addon(id='plugin.video.nakamori')
CWD = ADDON.getAddonInfo('path')  # .decode('utf-8')

ACTION_PREVIOUS_MENU = 10
ACTION_NAV_BACK = 92

# lists
FIRST_DAY = 55

img = os.path.join(xbmcaddon.Addon(id='plugin.video.nakamori').getAddonInfo('path'), 'resources', 'media')
font_path = os.path.join(xbmcaddon.Addon(id='plugin.video.nakamori').getAddonInfo('path'), 'fonts')

# noinspection PyTypeChecker
profileDir = ADDON.getAddonInfo('profile')
profileDir = xbmcvfs.translatePath(profileDir)

color = ADDON.getSetting('ac_color')
font_ttf = ADDON.getSetting('ac_font')
font_size = ADDON.getSetting('ac_size')

# TODO
font_size = '20'
font_ttf = 'FiraMono-Bold.ttf'
color = '#222000'

# create profile dirs
if not os.path.exists(profileDir):
    os.makedirs(profileDir)
if not os.path.exists(os.path.join(profileDir, 'titles')):
    os.makedirs(os.path.join(profileDir, 'titles'))
if not os.path.exists(os.path.join(profileDir, 'titles', color)):
    os.makedirs(os.path.join(profileDir, 'titles', color))
if not os.path.exists(os.path.join(profileDir, 'titles', color, font_ttf + '-' + font_size)):
    os.makedirs(os.path.join(profileDir, 'titles', color, font_ttf + '-' + font_size))
if not os.path.exists(os.path.join(profileDir, 'json')):
    os.makedirs(os.path.join(profileDir, 'json'))


class Calendar2(xbmcgui.WindowXML):
    def __init__(self, strXMLname, strFallbackPath, strDefaultName, forceFallback, data, item_number=0, start_date=datetime.datetime.now().strftime('%Y%m%d'), fake_data=False):
        self.window_type = 'window'
        self.json_data = data
        self.data = data
        self._start_item = 0
        try:
            self._start_item = int(item_number)
        except:
            xbmc.log('E --->' + str(item_number), xbmc.LOGERROR)
        self.calendar_collection = {}
        self.day_of_week = {}
        self.used_dates = []
        self.day_count = 0
        self.serie_processed = int(item_number)
        self.first_process_date = start_date
        self.last_processed_date = start_date
        self.fake_data = fake_data
        self.scroll_down_refresh = False
        self.calendar_end = False
        self.last_process_json = ''

    def AddSeriesToCalendar(self, check_back_in_time: bool = False):
        self.json_data = None
        xbmc.log(f'self.calendar_end={self.calendar_end}, self.data={self.data}, len={len(self.used_dates)}, self.json_data={self.json_data}', xbmc.LOGINFO)
        if not self.calendar_end:
            busy = xbmcgui.DialogProgress()
            busy.create(ADDON.getLocalizedString(30317), ADDON.getLocalizedString(30318))

            if self.data is None and len(self.used_dates) >= 0:
                try:
                    from lib.external_calendar import return_only_few
                    if len(self.used_dates) == 0:
                        last_date = datetime.datetime.now() - datetime.timedelta(days=1)
                    else:
                        last_date = datetime.datetime(*(time.strptime(self.last_processed_date, '%Y%m%d')[0:6]))
                        last_date = last_date + datetime.timedelta(days=1)
                    self.last_processed_date = last_date.strftime('%Y%m%d')
                    when = self.last_processed_date
                    if check_back_in_time:
                        when = self.first_process_date
                    page = self._start_item
                    self.json_data = None
                    body = return_only_few(when=when, offset=page, url=str(ADDON.getSetting('calendar_url')), go_back_in_time=check_back_in_time)
                    self.json_data = body
                    if self.last_process_json != self.json_data:
                        self.last_process_json = self.json_data
                    else:
                        self.json_data = None
                        self.calendar_end = True
                except Exception as ex:
                    xbmcgui.Dialog().ok('error_235', str(ex))
                    self.json_data = None
                    self.calendar_end = True
            else:
                xbmc.log('------------ > data is not None ', xbmc.LOGINFO)

            _size = 0
            _json = None
            if self.json_data is not None:
                if self.data is None:
                    _json = json.loads(self.json_data)
                    _size = _json.get('size', 0)
                else:
                    _size = self.data.size

                _count = 0

                if _size > 0:
                    if self.data is None:
                        for series in _json['series']:
                            busy.update(int(_count / _size))
                            if self.process_series_json(series):
                                _count += 1
                                pass
                            else:
                                break
                    else:
                        for series in self.data.series:
                            busy.update(int(_count / _size))
                            if self.process_series_object(series):
                                _count += 1
                                pass
                            else:
                                break
            else:
                self.calendar_end = True
            self.json_data = None
            busy.close()

    def onInit(self):
        self.calendar_collection = {
            1: self.getControl(FIRST_DAY),
        }

        if self.day_count >= 3:
            xbmc.log(f'=== self.day_count={self.day_count}', xbmc.LOGINFO)
            pass
        else:
            self.AddSeriesToCalendar()
            self.data = None
            self.setFocus(self.getControl(901))

    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU:
            self.close()
        elif action == ACTION_NAV_BACK:
            self.close()
        elif action == xbmcgui.ACTION_MOVE_RIGHT:
            self.list_update_right()
        elif action == xbmcgui.ACTION_MOVE_LEFT:
            self.list_update_left()
        elif action == xbmcgui.ACTION_MOVE_DOWN:
            self.list_update_down()
        elif action == xbmcgui.ACTION_MOVE_UP:
            self.list_update_up()
        elif action == xbmcgui.ACTION_MOUSE_RIGHT_CLICK:
            pass
        elif action == xbmcgui.ACTION_CONTEXT_MENU:
            try:
                control_id = self.getFocus().getId()
                con = self.getControl(control_id)
                assert isinstance(con, xbmcgui.ControlList)
                aid = int(con.getSelectedItem().getProperty('aid'))
                serie = series_from_anidb(aid)

                content_menu = [
                    '- aid = ' + str(aid) + '-',
                    ADDON.getLocalizedString(30337),
                    ADDON.getLocalizedString(30338),
                    ADDON.getLocalizedString(30339),
                    ADDON.getLocalizedString(30340)
                ]
                my_pick = xbmcgui.Dialog().contextmenu(content_menu)
                if my_pick != -1:
                    if my_pick <= 1:
                        if serie.aid == -1:
                            # TODO
                            print('x')
                            #xbmc.executebuiltin(script_utils.series_info(aid=aid), True)
                        else:
                            # TODO
                            print('x')
                            #xbmc.executebuiltin(script_utils.series_info(id=id), True)
                    elif my_pick > 1:
                        # TODO
                        print('x')
                        # xbmcgui.Dialog().ok('soon', 'comming soon')
            except:
                # in case 404 for that series - thats possible !
                pass
        elif action == xbmcgui.ACTION_SELECT_ITEM:
            # TODO
            print('x')
            #xbmcgui.Dialog().ok('soon', 'show soon')
        elif action == xbmcgui.ACTION_MOUSE_LEFT_CLICK:
            if self.getFocus().getId() == 1:
                xbmc.executebuiltin('Action(Back)')
            elif self.getFocus().getId() == 2:
                pass
        elif action == xbmcgui.ACTION_SCROLL_DOWN or action == xbmcgui.ACTION_MOUSE_WHEEL_DOWN:
            _id = self.getFocus().getId()
            currentpage = xbmc.getInfoLabel('Container(%s).CurrentPage' % _id)
            numpages = xbmc.getInfoLabel('Container(%s).NumPages' % _id)

            if currentpage == numpages:
                self.scroll_down_refresh = True

            if self.scroll_down_refresh:
                self.scroll_down_refresh = False
                self.AddSeriesToCalendar()

    def onControl(self, control):
        pass

    def onFocus(self, control):
        pass

    def process_series_object(self, series: api2models.Serie):
        air_date = series.air
        if air_date not in self.used_dates:
            self.used_dates.append(air_date)
            self.day_count += 1
            if self.serie_processed > 60:
                return False

            try:  # python bug workaround
                day_date = datetime.datetime.strptime(air_date, '%Y-%m-%d')
            except TypeError:
                # often this (always)
                day_date = datetime.datetime(*(time.strptime(air_date, '%Y-%m-%d')[0:6]))

            string_day = day_date.strftime('%d/%m')
            name_of_day = day_date.weekday()

            self.last_processed_date = day_date.strftime('%Y%m%d')
            xbmc.log('---------> I SET self.last_processed_date: %s' % self.last_processed_date, xbmc.LOGINFO)

        fanart = os.path.join(img, 'icons', 'new-search.png')
        if series.art.thumb.__len__() > 0:
            fanart = series.art.thumb[0].url
            if fanart is not None and ':' not in fanart:
                fanart = return_used_server_address() + fanart

        title = series.titles[0].Title  # TODO support better format here, until then this is ok
        aid = series.aid
        is_movie = series.ismovie
        summary = make_text_nice(series.summary)

        ep = 0
        if ' - ep' in title:
            search = re.search(r'( \- ep )(\d*)', title)
            ep = search.group(2)
            title = title.replace(search.group(1) + ep, '')

        # generate description image
        new_image_url = os.path.join(profileDir, 'titles', color, font_ttf + '-' + font_size, str(aid) + '_d.png')
        if not os.path.exists(new_image_url):
            image_x = 241
            image_y = 105
            font_wide_mitigation = 6
            this_path = os.path.join(font_path, font_ttf)
            font = ImageFont.truetype(this_path, int(font_size), encoding='unic')
            if len(summary) == 0:
                summary = ' '
            text_width, text_height = font.getsize(summary)
            text_lenght_till_split = 30
            if text_width + font_wide_mitigation > image_x:
                char_width = text_width / float(len(summary))
                chars_width = 0
                char_count = 0
                while chars_width < image_x - font_wide_mitigation:
                    chars_width += char_width
                    char_count += 1
                chars_width -= char_width
                char_count -= 1
                text_lenght_till_split = char_count
                xbmc.log('--> we found that text_lenght_till_split is not correct, so we calculate %s'
                         % text_lenght_till_split, xbmc.LOGWARNING)

            list_of_lines = textwrap.wrap(summary, width=int(text_lenght_till_split))
            three_line_support = 1
            processed_line = []
            for line in list_of_lines:
                temp_text_width, temp_text_height = font.getsize(line)
                three_line_support += temp_text_height
                processed_line.append(line)
                if three_line_support > image_y:
                    three_line_support -= temp_text_height
                    del processed_line[-1]
                    break

            image = Image.new('RGBA', (image_x, image_y), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            line_x = 0
            last_line = True
            if len(processed_line) > 1:
                for line in reversed(processed_line):
                    if last_line:
                        last_line = False
                        if len(line) > 3:
                            line = line[:-3] + '...'
                    temp_text_width, temp_text_height = font.getsize(line)
                    three_line_support -= temp_text_height
                    draw.text((line_x, three_line_support), line, font=font, fill=color)
            else:
                draw.text((line_x, 70 - text_height), summary, font=font, fill=color)
            image.save(new_image_url, 'PNG')

        series_listitem = xbmcgui.ListItem(label=title)
        series_listitem.setArt({'thumb': fanart, 'fanart': fanart, 'poster': new_image_url})
        # series_listitem.setUniqueIDs({'anidb': aid}')
        series_listitem.setInfo('video', {'title': title, 'aired': air_date, 'plot': summary})
        series_listitem.setProperty('title', title)
        series_listitem.setProperty('aired', str(air_date))
        series_listitem.setProperty('aid', str(aid))
        series_listitem.setProperty('ep', str(ep))

        self.calendar_collection[1].addItem(series_listitem)
        self.serie_processed += 1
        return True

    def process_series_json(self, series):
        air_date = series.get('air', '')
        if air_date not in self.used_dates:
            self.used_dates.append(air_date)
            self.day_count += 1

        if self.serie_processed > 60:
            return False

        try:  # python bug workaround
            day_date = datetime.datetime.strptime(air_date, '%Y-%m-%d')
        except TypeError:
            day_date = datetime.datetime(*(time.strptime(air_date, '%Y-%m-%d')[0:6]))

        string_day = day_date.strftime('%d/%m')
        name_of_day = day_date.weekday()

        self.last_processed_date = day_date.strftime('%Y%m%d')
        if self.first_process_date is not None:
            try:  # python bug workaround
                new_date = datetime.datetime.strptime(self.first_process_date, '%Y%m%d')
            except TypeError:
                new_date = datetime.datetime(*(time.strptime(self.first_process_date, '%Y%m%d')[0:6]))
            except:
                xbmc.log(f'=== E: new_date ===== {new_date}', xbmc.LOGERROR)
            if type(new_date) == datetime:
                if new_date < day_date:
                    self.first_process_date = self.last_processed_date

        fanart = os.path.join(img, 'icons', 'new-search.png')
        if len(series['art']['thumb']) > 0:
            fanart = series['art']['thumb'][0]['url']
            if fanart is not None and ':' not in fanart:
                fanart = return_used_server_address() + fanart
        title = series['titles'][0]['Title']  # support better format here, until then this is ok
        aid = series.get('aid', 0)
        is_movie = series.get('ismovie', 0)
        summary = make_text_nice(str(series.get('summary', '')))
        ep = 0
        if ' - ep' in title:
            search = re.search(r'( \- ep )(\d*)', title)
            ep = search.group(2)
            title = title.replace(search.group(1) + ep, '')

        # generate description image
        new_image_url = os.path.join(profileDir, 'titles', color, font_ttf + '-' + font_size, str(aid) + '_d.png')
        if not os.path.exists(new_image_url):
            image_x = 241
            image_y = 105
            font_wide_mitigation = 6
            this_path = os.path.join(font_path, font_ttf)
            font = ImageFont.truetype(this_path, int(font_size), encoding='unic')
            if len(summary) == 0:
                summary = ' '
            text_width, text_height = font.getsize(summary)
            text_lenght_till_split = 30
            if text_width + font_wide_mitigation > image_x:
                char_width = text_width / float(len(summary))
                chars_width = 0
                char_count = 0
                while chars_width < image_x - font_wide_mitigation:
                    chars_width += char_width
                    char_count += 1
                chars_width -= char_width
                char_count -= 1
                text_lenght_till_split = char_count
                xbmc.log('--> we found that text_lenght_till_split is not correct, so we calculate %s'
                         % text_lenght_till_split, xbmc.LOGWARNING)

            list_of_lines = textwrap.wrap(summary, width=int(text_lenght_till_split))
            three_line_support = 1
            processed_line = []
            for line in list_of_lines:
                temp_text_width, temp_text_height = font.getsize(line)
                three_line_support += temp_text_height
                processed_line.append(line)
                if three_line_support > image_y:
                    three_line_support -= temp_text_height
                    del processed_line[-1]
                    break

            image = Image.new('RGBA', (image_x, image_y), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            line_x = 0
            last_line = True
            if len(processed_line) > 1:
                for line in reversed(processed_line):
                    if last_line:
                        last_line = False
                        if len(line) > 3:
                            line = line[:-3] + '...'
                    temp_text_width, temp_text_height = font.getsize(line)
                    three_line_support -= temp_text_height
                    draw.text((line_x, three_line_support), line, font=font, fill=color)
            else:
                draw.text((line_x, 70 - text_height), summary, font=font, fill=color)
            image.save(new_image_url, 'PNG')

        series_listitem = xbmcgui.ListItem(label=title)
        series_listitem.setArt({'thumb': fanart, 'fanart': fanart, 'poster': new_image_url})
        # series_listitem.setUniqueIDs({'anidb': aid}')
        series_listitem.setInfo('video', {'title': title, 'aired': air_date, 'plot': summary})
        series_listitem.setProperty('title', title)
        series_listitem.setProperty('aired', str(air_date))
        series_listitem.setProperty('aid', str(aid))
        series_listitem.setProperty('ep', str(ep))

        self.calendar_collection[1].addItem(series_listitem)
        self.serie_processed += 1
        return True

    def list_update_right(self):
        pass

    def list_update_left(self):
        pass

    def list_update_up(self):
        if False:
            try:
                if self.getFocus().getId() > -1:
                    _id = self.getFocus().getId()
                    position = xbmc.getInfoLabel('Container(%s).Position' % _id)
                    row = xbmc.getInfoLabel('Container(%s).Row' % _id)
                    column = xbmc.getInfoLabel('Container(%s).Column' % _id)
                    currentpage = xbmc.getInfoLabel('Container(%s).CurrentPage' % _id)
                    numpages = xbmc.getInfoLabel('Container(%s).NumPages' % _id)
                    numitems = xbmc.getInfoLabel('Container(%s).NumItems' % _id)
                    numallitems = xbmc.getInfoLabel('Container(%s).NumAllItems' % _id)

                    _position = self.calendar_collection[1].getSelectedPosition()  # absolute
                    _size = self.calendar_collection[1].size()
                    if _position - 3 <= _size:
                        self.AddSeriesToCalendar(check_back_in_time=True)
                        self.calendar_collection[1].selectItem(_position)

            except Exception as ex:
                xbmcgui.Dialog().ok('error_up', str(ex))
        pass

    def list_update_down(self):
        try:
            if self.getFocus().getId() > -1:
                _id = self.getFocus().getId()
                position = xbmc.getInfoLabel('Container(%s).Position' % _id)
                row = xbmc.getInfoLabel('Container(%s).Row' % _id)
                column = xbmc.getInfoLabel('Container(%s).Column' % _id)
                currentpage = xbmc.getInfoLabel('Container(%s).CurrentPage' % _id)
                numpages = xbmc.getInfoLabel('Container(%s).NumPages' % _id)
                numitems = xbmc.getInfoLabel('Container(%s).NumItems' % _id)
                numallitems = xbmc.getInfoLabel('Container(%s).NumAllItems' % _id)

                _position = self.calendar_collection[1].getSelectedPosition()  # absolute
                _size = self.calendar_collection[1].size()
                if _position + 3 >= _size:
                    self.AddSeriesToCalendar()
                    self.calendar_collection[1].selectItem(_position)

        except Exception as ex:
            xbmcgui.Dialog().ok('error_down', str(ex))


def open_calendar(date=0, starting_item=0, json_respons=''):
    xbmc.executebuiltin('Dialog.Close(busydialog)')
    ui = Calendar2('ac_calendar.xml', CWD, 'Default', '1080i', data=None, item_number=starting_item, fake_data=False)
    ui.doModal()
    del ui


def clear_cache():
    if os.path.exists(os.path.join(profileDir, 'titles')):
        clear = xbmcgui.Dialog().yesno(ADDON.getLocalizedString(30319), ADDON.getLocalizedString(30320))
        if clear:
            files_to_delete = [os.path.join(path, file)
                               for (path, dirs, files) in os.walk(os.path.join(profileDir, 'titles'))
                               for file in files]
            for f in files_to_delete:
                os.remove(f)
                xbmc.log('clear-cache deleted: ' + str(f), xbmc.LOGINFO)
    if os.path.exists(os.path.join(profileDir, 'json')):
        clear = xbmcgui.Dialog().yesno(ADDON.getLocalizedString(30019), ADDON.getLocalizedString(30020))
        if clear:
            files_to_delete = [os.path.join(path, file)
                               for (path, dirs, files) in os.walk(os.path.join(profileDir, 'json'))
                               for file in files]
            for f in files_to_delete:
                os.remove(f)
                xbmc.log('clear-cache deleted: ' + str(f), xbmc.LOGINFO)

