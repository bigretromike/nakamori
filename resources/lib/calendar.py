#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyxbmct
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
from resources.lib.util import *

_addon = xbmcaddon.Addon()
_addon_path = _addon.getAddonInfo('path')
_home_ = decode_utf8(xbmc.translatePath(_addon.getAddonInfo('path')))
_server_ = "http://" + _addon.getSetting("ipaddress") + ":" + _addon.getSetting("port")
day_images = {1: "day1.jpg", 2: "day2.jpg"}

max_row_count = 18
max_col_count = 20
image_row_span = 4
image_col_span = 2


class Calendar(pyxbmct.BlankDialogWindow):
    def __init__(self, data, handle, page=0):
        super(Calendar, self).__init__()
        self.setGeometry(1280, 720, max_row_count, max_col_count)
        self.__draw = False
        self.controls = []
        self.items = []
        self.items_cord = []
        self.window_handle = handle
        self.json_data = data
        self.start_page = 0
        self.prev_count = page
        self.urls = []
        self.draw()

    def setAnimation(self, control):
        control.setAnimations([('WindowOpen', 'effect=fade start=0 end=100 time=200'),
                               ('WindowClose', 'effect=fade start=100 end=0 time=200')])

    def draw(self):
        """ Function draw
            initialize built-in functions
            this automatically called.
        """
        bg = pyxbmct.Image(os.path.join(_home_, 'resources/media', 'black_dot.png'), aspectRatio=0)
        self.placeControl(bg, 0, 0, rowspan=max_row_count, columnspan=max_col_count, pad_x=0, pad_y=0)
        self.set_active_controls(self.json_data, self.start_page)
        self.set_navigation()

    def _cancel(self):
        self.close()

    def add_control_items(self, _data, _start_page):
        day_count = 0
        row_idx = 0
        col_idx = 0
        used_dates = []
        continue_day = False
        page_count_ = 0
        # test = 1
        for sers in _data['series']:
            # if test == 2:
            #     break
            # else:
            #     test = 2
            if page_count_ < _start_page:
                page_count_ += 1
            else:
                page_count_ += 1
                air_date = sers.get('air', '')
                if col_idx > max_col_count - image_col_span:
                    break

                if row_idx > max_row_count - image_row_span:
                    row_idx = 0
                    continue_day = True
                if air_date in used_dates:
                    if continue_day:
                        continue_day = False
                        image01 = pyxbmct.Image(os.path.join(_home_, 'resources/media', day_images[day_count]), aspectRatio=0)
                        self.controls.append(image01)
                        row_idx += 1
                        self.placeControl(image01, row_idx, col_idx, rowspan=1, columnspan=image_col_span, pad_x=0, pad_y=0)
                        row_idx += 1
                    pass
                else:
                    continue_day = False
                    if day_count != 0:
                        col_idx += 2  # was 3
                        row_idx = 0
                        if col_idx > max_col_count - image_col_span:
                            break
                    day_count += 1
                    if day_count > 2:
                        day_count = 1
                    used_dates.append(air_date)
                    label = pyxbmct.Label(air_date)
                    self.controls.append(label)
                    self.placeControl(label, row_idx, col_idx, rowspan=1, columnspan=image_col_span)
                    image0 = pyxbmct.Image(os.path.join(_home_, 'resources/media', day_images[day_count]), aspectRatio=0)
                    self.controls.append(image0)
                    row_idx += 1
                    self.placeControl(image0, row_idx, col_idx, rowspan=1, columnspan=image_col_span, pad_x=0, pad_y=0)
                    row_idx += 1

                # region anime
                fanart = os.path.join(_home_, 'resources/media', 'new-search.jpg')
                if len(sers["art"]["thumb"]) > 0:
                    fanart = sers["art"]["thumb"][0]["url"]
                    if fanart is not None and ":" not in fanart:
                        fanart = _server_ + fanart
                imageclick = pyxbmct.Button(label=sers["titles"][0]["Title"], focusTexture=fanart, noFocusTexture=fanart, focusedColor='0xFF00FFFF', font='font10', alignment=pyxbmct.ALIGN_CENTER)
                self.controls.append(imageclick)
                self.items.append(imageclick)
                self.items_cord.append(str(row_idx) + ";" + str(col_idx))
                self.placeControl(imageclick, row_idx, col_idx, rowspan=image_row_span, columnspan=image_col_span)
                row_idx += image_row_span
                # endregion

                # region anime-url
                key_id = str(sers.get('id', ''))
                key = _server_ + "/api/serie"
                key = set_parameter(key, 'id', key_id)
                key = set_parameter(key, 'level', 2)
                if _addon.getSetting('request_nocast') == 'true':
                    key = set_parameter(key, 'nocast', 1)

                u = sys.argv[0]
                u = set_parameter(u, 'url', key)
                u = set_parameter(u, 'mode', 6)
                u = set_parameter(u, 'fake', 1)
                u = set_parameter(u, 'movie', sers.get('ismovie', '0'))
                self.connect(imageclick, lambda: self.serie())
                self.urls.append(str(u))
                # endregion

    def set_active_controls(self, _data, _start_page):
        """Set up UI controls"""
        self.add_control_items(_data, _start_page)

        self.connectEventList(
            [pyxbmct.ACTION_MOVE_DOWN,
             pyxbmct.ACTION_MOUSE_WHEEL_DOWN],
            self.list_update_down)

        self.connectEventList(
            [pyxbmct.ACTION_MOVE_UP,
             pyxbmct.ACTION_MOUSE_WHEEL_UP],
            self.list_update_up)

        self.connectEventList(
            [pyxbmct.ACTION_MOVE_RIGHT],
            self.list_update_right)

        self.connectEventList(
            [pyxbmct.ACTION_MOVE_LEFT],
            self.list_update_left)

        self.connectEventList(
            [pyxbmct.ACTION_PREVIOUS_MENU,
             pyxbmct.ACTION_NAV_BACK],
            self._cancel)

    def list_update_up(self):
        try:
            if self.items.index(self.getFocus()) > -1:
                item_idx = self.items.index(self.getFocus())
                if item_idx > 0:
                    item_idx -= 1
                self.setFocus(self.items[item_idx])
        except (RuntimeError, SystemError):
            pass

    def list_update_down(self):
        try:
            if self.items.index(self.getFocus()) > -1:
                item_idx = self.items.index(self.getFocus())
                if item_idx < len(self.items) - 1:
                    item_idx += 1
                self.setFocus(self.items[item_idx])
        except (RuntimeError, SystemError):
            pass

    def list_update_right(self):
        try:
            if self.items.index(self.getFocus()) > -1:
                item_idx = self.items.index(self.getFocus())
                max_cords = str.split(self.items_cord[len(self.items_cord) - 1], ';')
                cords = str.split(self.items_cord[item_idx], ';')
                new_r = int(cords[0])
                new_c = int(cords[1])
                # xbmc.log('-------->>>---------- (max_cords[1] {0} max_col_count {1})'.format(str(max_cords[1]), str(max_col_count)), xbmc.LOGWARNING)
                if int(max_cords[1]) > max_col_count - 2:  # 18 > 20-2
                    max_cords[1] = max_col_count - 2

                if new_c >= int(max_cords[1]):
                    for c in self.controls:
                        self.removeControl(c)
                        del c
                    self.controls = []
                    self.prev_count = len(self.items)
                    self.start_page += self.prev_count
                    self.items = []
                    self.items_cord = []
                    self.add_control_items(self.json_data, self.start_page)
                    item_idx = 0
                else:
                    new_c += 2

                    while new_r > 0:
                        try:
                            item_idx = self.items_cord.index(str(new_r) + ';' + str(new_c))
                            break
                        except:
                            new_r -= 1
                    item_idx = self.items_cord.index(str(new_r) + ';' + str(new_c))
                self.setFocus(self.items[item_idx])
        except (RuntimeError, SystemError):
            pass

    def list_update_left(self):
        try:
            if self.items.index(self.getFocus()) > -1:
                item_idx = self.items.index(self.getFocus())
                cords = str.split(self.items_cord[item_idx], ';')
                new_r = int(cords[0])
                new_c = int(cords[1])
                new_c -= 2
                # xbmc.log('--------<<<---------- ((new_c {0} items {1} start_page {2})'.format(str(new_c), str(len(self.items)), str(self.start_page)), xbmc.LOGWARNING)
                if new_c < 0:
                    for c in self.controls:
                        self.removeControl(c)
                        del c
                    self.controls = []
                    # self.prev_count = len(self.items)
                    self.start_page -= self.prev_count
                    if self.start_page < 0:
                        self.start_page = 0
                    self.items = []
                    self.items_cord = []
                    self.add_control_items(self.json_data, self.start_page)
                    item_idx = len(self.items) - 1
                else:
                    while new_r > 0:
                        try:
                            item_idx = self.items_cord.index(str(new_r) + ';' + str(new_c))
                            break
                        except:
                            new_r -= 1
                    item_idx = self.items_cord.index(str(new_r) + ';' + str(new_c))
                self.setFocus(self.items[item_idx])
        except (RuntimeError, SystemError):
            pass

    def set_navigation(self):
        """Set up keyboard/remote navigation between controls."""
        self.connect(pyxbmct.ACTION_NAV_BACK, self._cancel)
        self.connect(pyxbmct.ACTION_PREVIOUS_MENU, self._cancel)
        self.setFocus(self.items[0])

    def serie(self):
        try:
            url = self.items.index(self.getFocus())
            xbmc.log('---------- oooo -----> url {0}'.format(self.urls[url]), xbmc.LOGWARNING)
            handle = xbmcgui.getCurrentWindowId()
            win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
            ctl = win.getControl(win.getFocusId())
            self.close()
            xbmc.executebuiltin('ActivateWindow({1},"{0}")'.format(self.urls[url], handle))
            xbmc.sleep(2000)
            xbmc.executebuiltin('Action(Info)')
        except Exception as ex:
            xbmc.log('>>>>>>>>>>>>>>>>>>not working {0}'.format(str(ex.message)), xbmc.LOGWARNING)
