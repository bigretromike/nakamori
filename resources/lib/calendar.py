#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyxbmct
import datetime
import os
import sys
import time
import xbmc
import xbmcgui
import resources.lib.util as util 

day_images = {1: "day1.png", 2: "day2.png", 3: "day3.png", 4: "day4.png", 5: "day5.png"}

if str(util.__addon__.getSetting("calendar_adv")) == "True":
    image_row_span = int(util.__addon__.getSetting("calendar_rows_span"))
    image_col_span = int(util.__addon__.getSetting("calendar_cols_span"))
else:
    image_row_span = 8
    image_col_span = 4
max_row_count = (image_row_span * int(util.__addon__.getSetting("calendar_rows"))) + 2
max_col_count = (image_col_span * int(util.__addon__.getSetting("calendar_cols")))


class Context(pyxbmct.AddonDialogWindow):
    def __init__(self, title, serie_id):
        super(Context, self).__init__(serie_id)
        self.setGeometry(640, 360, 6, 8)
        self.setWindowTitle(title=title)
        self.__draw = False
        self.serie_id = serie_id
        self.button_add = pyxbmct.Button(label='Add', textColor='0xFFFFFFFF', focusedColor='0xFF00FFFF')
        self.button_del = pyxbmct.Button(label='Del', textColor='0xFFFFFFFF', focusedColor='0xFF00FFFF')
        self.button_close = pyxbmct.Button(label='Close', textColor='0xFFFFFFFF', focusedColor='0xFF00FFFF')
        self.label_id = pyxbmct.Label(label=serie_id, textColor='0xFFFFFFFF')
        self.draw()

    def setAnimation(self, control):
        control.setAnimations([('WindowOpen', 'effect=fade start=0 end=100 time=200'),
                               ('WindowClose', 'effect=fade start=100 end=0 time=200')])

    def draw(self):
        self.set_active_controls()
        self.set_navigation()

    def _cancel(self):
        self.close()

    def set_active_controls(self):
        self.placeControl(self.button_add, 1, 1, rowspan=2, columnspan=2)
        self.placeControl(self.label_id, 4, 1, rowspan=2, columnspan=2)
        self.placeControl(self.button_del, 1, 5, rowspan=2, columnspan=2)
        self.placeControl(self.button_close, 4, 5, rowspan=2, columnspan=2)
        self.connect(self.button_add, lambda: self.btn_add())
        self.connect(self.button_del, lambda: self.btn_del())
        self.connect(self.button_close, lambda: self._cancel())

    def btn_add(self):
        return

    def btn_dell(self):
        return

    def set_navigation(self):
        """Set up keyboard/remote navigation between controls."""
        self.connect(pyxbmct.ACTION_NAV_BACK, self._cancel)
        self.connect(pyxbmct.ACTION_PREVIOUS_MENU, self._cancel)
        self.connect(pyxbmct.ACTION_MOVE_UP, self.list_update_up)
        self.connect(pyxbmct.ACTION_MOVE_DOWN, self.list_update_down)
        self.connect(pyxbmct.ACTION_MOVE_RIGHT, self.list_update_right)
        self.connect(pyxbmct.ACTION_MOVE_LEFT, self.list_update_left)
        self.setFocus(self.button_add)

    def list_update_up(self):
        self.setFocus(self.button_add)

    def list_update_down(self):
        self.setFocus(self.button_close)

    def list_update_left(self):
        self.setFocus(self.button_add)

    def list_update_right(self):
        self.setFocus(self.button_del)


class Calendar(pyxbmct.BlankDialogWindow):
    def __init__(self, data, handle, page=0):
        super(Calendar, self).__init__()
        self.setGeometry(1280, 720, max_row_count, max_col_count)
        self.__draw = False
        self.controls = []
        self.items = []
        self.items_cord = []
        self.serie_index = []
        self.window_handle = handle
        self.json_data = data
        self.start_page = 0
        self.prev_count = page
        self.urls = []
        self.draw()
        if len(self.items) > 0:
            self.setFocus(self.items[0])

    def setAnimation(self, control):
        control.setAnimations([('WindowOpen', 'effect=fade start=0 end=100 time=200'),
                               ('WindowClose', 'effect=fade start=100 end=0 time=200')])

    def draw(self):
        bg = pyxbmct.Image(os.path.join(util._home_, 'resources/media', 'black_dot.png'), aspectRatio=0)
        self.placeControl(bg, 0, 0, rowspan=max_row_count, columnspan=max_col_count, pad_x=0, pad_y=0)
        self.set_active_controls(self.json_data, self.start_page)
        self.set_navigation()

    def _cancel(self):
        self.close()

    def _run_context(self):
        idx = self.items.index(self.getFocus())
        window = Context(title='Add to wanted', serie_id=self.serie_index[idx])
        window.doModal()
        del window

    def add_control_items(self, _data, _start_page):
        day_count = 0
        row_idx = 0
        col_idx = 0
        used_dates = []
        continue_day = False
        page_count_ = 0

        for sers in _data['series']:
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
                        image01 = pyxbmct.Image(os.path.join(util._home_, 'resources/media', day_images[day_count]), aspectRatio=0)
                        self.controls.append(image01)
                        row_idx += 1
                        self.placeControl(image01, row_idx, col_idx, rowspan=1, columnspan=image_col_span, pad_x=0, pad_y=0)
                        row_idx += 1
                    pass
                else:
                    continue_day = False
                    if day_count != 0:
                        col_idx += image_col_span
                        row_idx = 0
                        if col_idx > max_col_count - image_col_span:
                            break
                    day_count += 1
                    if day_count > len(day_images):
                        day_count = 1
                    used_dates.append(air_date)

                    try:  # python bug workaround
                        your_label = datetime.datetime.strptime(air_date, '%Y-%m-%d')
                    except TypeError:
                        your_label = datetime.datetime(*(time.strptime(air_date, '%Y-%m-%d')[0:6]))

                    your_label = your_label.strftime(util.__addon__.getSetting("calendar_format"))
                    label = pyxbmct.Label(your_label)
                    self.controls.append(label)
                    self.placeControl(label, row_idx, col_idx, rowspan=1, columnspan=image_col_span)
                    image0 = pyxbmct.Image(os.path.join(util._home_, 'resources/media', day_images[day_count]), aspectRatio=2)
                    self.controls.append(image0)
                    row_idx += 1
                    self.placeControl(image0, row_idx, col_idx, rowspan=1, columnspan=image_col_span, pad_x=0, pad_y=0)
                    row_idx += 1

                # region anime
                fanart = os.path.join(util._home_, 'resources/media', 'new-search.jpg')
                if len(sers["art"]["thumb"]) > 0:
                    fanart = sers["art"]["thumb"][0]["url"]
                    if fanart is not None and ":" not in fanart:
                        fanart = util._server_ + fanart
                imageclick = pyxbmct.Button(label=sers["titles"][0]["Title"],
                                            focusTexture=fanart, noFocusTexture=fanart,
                                            focusedColor='0xFF000000', font='font10', alignment=pyxbmct.ALIGN_CENTER)
                self.controls.append(imageclick)
                self.items.append(imageclick)
                self.items_cord.append(str(row_idx) + ";" + str(col_idx))
                self.placeControl(imageclick, row_idx, col_idx, rowspan=image_row_span, columnspan=image_col_span)
                row_idx += image_row_span
                # endregion

                # region anime-url
                key_id = str(sers.get('id', ''))
                key = util._server_ + "/api/serie"
                key = util.set_parameter(key, 'id', key_id)
                key = util.set_parameter(key, 'level', 2)
                if util.__addon__.getSetting('request_nocast') == 'true':
                    key = util.set_parameter(key, 'nocast', 1)

                u = sys.argv[0]
                u = util.set_parameter(u, 'url', key)
                u = util.set_parameter(u, 'mode', 6)
                u = util.set_parameter(u, 'fake', 1)
                u = util.set_parameter(u, 'movie', sers.get('ismovie', '0'))
                self.connect(imageclick, lambda: self.serie())
                imageclick.setAnimations([('focus', 'effect=zoom center=auto start=100 end=110 time=100 delay=10',)])
                self.urls.append(str(u))
                self.serie_index.append(str(key_id))
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
                if int(max_cords[1]) > max_col_count - image_col_span:
                    max_cords[1] = max_col_count - image_col_span

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
                    new_c += image_col_span

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
                new_c -= image_col_span
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
        ACTION_BACKSPACE = 92
        """Set up keyboard/remote navigation between controls."""
        self.connect(pyxbmct.ACTION_NAV_BACK, lambda: self._cancel())
        self.connect(ACTION_BACKSPACE, lambda: self._cancel())
        self.connect(xbmcgui.ACTION_PREVIOUS_MENU, lambda: self._cancel())
        self.connect(xbmcgui.ACTION_MOUSE_RIGHT_CLICK, lambda: self._run_context())
        self.connect(xbmcgui.ACTION_CONTEXT_MENU, lambda: self._run_context())

    #def onAction(self, action):
    #    ACTION_PREVIOUS_MENU = 10
    #    ACTION_BACKSPACE = 92
    #    if action == ACTION_PREVIOUS_MENU:
    #        self.close()
    #    elif action == ACTION_BACKSPACE:
    #        self.close()

    def serie(self):
        try:
            url = self.items.index(self.getFocus())
            xbmc.log('---------- oooo -----> url {0}'.format(self.urls[url]), xbmc.LOGWARNING)
            handle = xbmcgui.getCurrentWindowId()
            win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
            self.close()  # crash kodi without
            xbmc.executebuiltin('ActivateWindow({1},"{0}")'.format(self.urls[url], handle))
            xbmc.sleep(2000)
            xbmc.executebuiltin('Action(Info)')
        except Exception as ex:
            xbmc.log('>>>>>>>>>>>>>>>>>>not working {0}'.format(str(ex.message)), xbmc.LOGWARNING)


class Wizard(pyxbmct.AddonDialogWindow):
    def __init__(self, title):
        super(Wizard, self).__init__()
        self.setGeometry(640, 360, 9, 11)
        self.setWindowTitle(title=title)
        self.setup_ok = False
        # buttons
        self.button_test_net = pyxbmct.Button(label=util.__addon__.getLocalizedString(30072), textColor='0xFFFFFFFF', focusedColor='0xFF00FFFF')
        self.button_test_pass = pyxbmct.Button(label=util.__addon__.getLocalizedString(30072), textColor='0xFFFFFFFF', focusedColor='0xFF00FFFF')
        self.button_close = pyxbmct.Button(label=util.__addon__.getLocalizedString(30078), textColor='0xFFFFFFFF', focusedColor='0xFF00FFFF')
        self.button_save = pyxbmct.Button(label=util.__addon__.getLocalizedString(30073), textColor='0xFFFFFFFF', focusedColor='0xFF00FFFF')
        # labels
        self.label_ip = pyxbmct.Label(label=util.__addon__.getLocalizedString(30074), textColor='0xFFFFFFFF')
        self.label_port = pyxbmct.Label(label=util.__addon__.getLocalizedString(30075), textColor='0xFFFFFFFF')
        self.label_login = pyxbmct.Label(label=util.__addon__.getLocalizedString(30076), textColor='0xFFFFFFFF')
        self.label_pass = pyxbmct.Label(label=util.__addon__.getLocalizedString(30077), textColor='0xFFFFFFFF')
        # edit
        self.edit_ip = pyxbmct.Edit(label='', textColor='0xFFFFFFFF')
        self.edit_port = pyxbmct.Edit(label='', textColor='0xFFFFFFFF')
        self.edit_login = pyxbmct.Edit(label='', textColor='0xFFFFFFFF')
        self.edit_pass = pyxbmct.Edit(label='', textColor='0xFFFFFFFF', isPassword=True)
        # draw
        self.draw()

    def setAnimation(self, control):
        control.setAnimations([('WindowOpen', 'effect=fade start=0 end=100 time=200'),
                               ('WindowClose', 'effect=fade start=100 end=0 time=200')])

    def draw(self):
        self.set_active_controls()
        self.set_navigation()

    def _cancel(self):
        if util.__addon__.getSetting("apikey") != "":
            self.setup_ok = True
            self.close()
        else:
            if xbmcgui.Dialog().yesno(util.__addon__.getLocalizedString(30079),
                                      util.__addon__.getLocalizedString(30080),
                                      util.__addon__.getLocalizedString(30081)):
                self.setup_ok = False
                self.close()

    def _save(self):
        if util.__addon__.getSetting("apikey") != "":
            self.setup_ok = True
            self.close()
        else:
            xbmcgui.Dialog().ok(util.__addon__.getLocalizedString(30079), util.__addon__.getLocalizedString(30080))

    def _test_net(self):
        if util.get_server_status(ip=str(self.edit_ip.getText()), port=str(self.edit_port.getText())):
            ip = str(self.edit_ip.getText())
            port = str(self.edit_port.getText())
            util.__addon__.setSetting(id="ipaddress", value=ip)
            util.__addon__.setSetting(id="port", value=port)
            self.button_test_net.setLabel(label='OK', textColor='0xff7aad5c', focusedColor='0xff7aad5c')
        else:
            self.button_test_net.setLabel(label=util.__addon__.getLocalizedString(30072),
                                          textColor='0xFFDF1818', focusedColor='0xFFDF1818')

    def _test_pass(self):
        util.__addon__.setSetting(id="apikey", value="")
        util.__addon__.setSetting(id="login", value=self.edit_login.getText())
        util.__addon__.setSetting(id="password", value=self.edit_pass.getText())
        util.__addon__.setSetting(id="device", value="kodi")

        if util.valid_user():
            self.button_test_pass.setLabel(label='OK', textColor='0xff7aad5c', focusedColor='0xff7aad5c')
        else:
            self.button_test_pass.setLabel(label=util.__addon__.getLocalizedString(30072),
                                           textColor='0xFFDF1818', focusedColor='0xFFDF1818')

    def set_active_controls(self):
        self.placeControl(self.label_ip, 1, 1, rowspan=1, columnspan=3)
        self.placeControl(self.label_port, 1, 5, rowspan=1, columnspan=3)
        self.placeControl(self.label_login, 4, 1, rowspan=1, columnspan=3)
        self.placeControl(self.label_pass, 4, 5, rowspan=1, columnspan=3)
        self.placeControl(self.button_test_net, 2, 8, rowspan=1, columnspan=2)
        self.placeControl(self.button_test_pass, 5, 8, rowspan=1, columnspan=2)
        self.placeControl(self.button_close, 7, 1, rowspan=1, columnspan=3)
        self.placeControl(self.button_save, 7, 7, rowspan=1, columnspan=3)
        self.placeControl(self.edit_ip, 2, 1, rowspan=1, columnspan=3)
        self.placeControl(self.edit_port, 2, 5, rowspan=1, columnspan=2)
        self.placeControl(self.edit_login, 5, 1, rowspan=1, columnspan=3)
        self.placeControl(self.edit_pass, 5, 5, rowspan=1, columnspan=3)
        self.edit_ip.setText(util.__addon__.getSetting("ipaddress"))
        self.edit_port.setText(util.__addon__.getSetting("port"))
        self.edit_login.setText(util.__addon__.getSetting("login"))
        self.edit_pass.setText(util.__addon__.getSetting("password"))
        self.connect(self.button_test_net, lambda: self._test_net())
        self.connect(self.button_test_pass, lambda: self._test_pass())
        self.connect(self.button_save, lambda: self._save())
        self.connect(self.button_close, lambda: self._cancel())

    def set_navigation(self):
        """Set up keyboard/remote navigation between controls."""
        self.connect(pyxbmct.ACTION_NAV_BACK, self._cancel)
        self.connect(pyxbmct.ACTION_PREVIOUS_MENU, self._cancel)
        # setNavigation(up, down, left, right)
        self.edit_ip.setNavigation(self.edit_ip, self.edit_login, self.edit_ip, self.edit_port)
        self.edit_port.setNavigation(self.edit_port, self.edit_pass, self.edit_ip, self.button_test_net)
        self.edit_login.setNavigation(self.edit_ip, self.button_close, self.edit_login, self.edit_pass)
        self.edit_pass.setNavigation(self.edit_port, self.button_save, self.edit_login, self.button_test_pass)
        self.button_test_net.setNavigation(self.button_test_net, self.button_test_pass,
                                           self.edit_port, self.button_test_net)
        self.button_test_pass.setNavigation(self.button_test_net, self.button_save,
                                            self.edit_pass, self.button_test_pass)
        self.button_close.setNavigation(self.edit_login, self.button_close, self.button_close, self.button_save)
        self.button_save.setNavigation(self.button_test_pass, self.button_save, self.button_close, self.button_save)
        # Set initial focus.
        self.setFocus(self.edit_ip)
