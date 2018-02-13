#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyxbmct
import xbmc
import xbmcaddon
import xbmcgui
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


class Calendar(pyxbmct.BlankFullWindow):
    global items
    global items_cord

    def __init__(self, data):
        """Class constructor"""
        # Call the base class' constructor.
        super(Calendar, self).__init__()
        # Set width, height and the grid parameters (row, columns)
        self.setGeometry(1280, 720, max_row_count, max_col_count)
        self.items = []
        self.items_cord = []
        # Call set controls method
        self.set_active_controls(data)
        # Call set navigation method.
        self.set_navigation()
        # Connect Backspace button to close our addon.
        self.connect(pyxbmct.ACTION_NAV_BACK, self.close)

    def set_active_controls(self, _data):
        """Set up UI controls"""
        day_count = 0
        row_idx = 0
        col_idx = 0
        used_dates = []
        continue_day = False
        eee = False

        for sers in _data['series']:
            air_date = sers.get('air', '')

            if row_idx > max_row_count - image_row_span:
                row_idx = 0
                # col_idx += 2
                continue_day = True

            if air_date in used_dates:
                if continue_day:
                    continue_day = False
                    image01 = pyxbmct.Image(os.path.join(_home_, 'resources/media', day_images[day_count]), aspectRatio=0)
                    row_idx += 1
                    self.placeControl(image01, row_idx, col_idx, rowspan=1, columnspan=image_col_span, pad_x=0, pad_y=0)
                    row_idx += 1
                pass
            else:
                continue_day = False
                if day_count != 0:
                    col_idx += 2  # was 3
                    row_idx = 0
                day_count += 1
                if day_count > 2:
                    day_count = 1
                used_dates.append(air_date)
                label = pyxbmct.Label(air_date)
                self.placeControl(label, row_idx, col_idx, rowspan=1, columnspan=image_col_span)
                image0 = pyxbmct.Image(os.path.join(_home_, 'resources/media', day_images[day_count]), aspectRatio=0)
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
            u = set_parameter(u, 'mode', 5)
            u = set_parameter(u, 'movie', sers.get('ismovie', '0'))
            u = "plugin://plugin.video.nakamori"
            self.connect(imageclick, lambda: self.serie(u))
            # endregion

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
                if item_idx < len(self.items):
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
                if int(max_cords[1]) > max_col_count - 2:
                    max_cords[1] = max_col_count - 2

                if new_c >= int(max_cords[1]):
                    new_c -= 2
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

                if new_c < 0:
                    new_c = 2
                new_c -= 2

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
        self.setFocus(self.items[0])

    def serie(self, url):
        xbmc.executebuiltin('Notification(URL,{0})'.format(url))
        xbmc.executebuiltin('RunPlugin("plugin://plugin.video.nakamori")')  # not working

