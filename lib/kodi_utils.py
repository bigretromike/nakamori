# -*- coding: utf-8 -*-

import os
from uuid import uuid4

import xbmcaddon # type: ignore
import xbmcvfs # type: ignore
import xbmcgui # type: ignore
import xbmc # type: ignore

plugin_addon = xbmcaddon.Addon('plugin.video.nakamori')


def create_id():
    """
    Return random device id
    :return: str
    """
    return int(uuid4())


def get_device_id(reset: bool = False):
    """
    Return current DeviceID or create and save new one
    :param reset: Reset current DeviceID
    :return: DeviceID: str
    """
    device_id = xbmcgui.Window(10000).getProperty('nakamori_deviceId')
    if device_id:
        return device_id
    directory = xbmcvfs.translatePath(plugin_addon.getAddonInfo('profile'))
    nakamori_guid = os.path.join(directory, "nakamori_guid")
    file_guid = xbmcvfs.File(nakamori_guid)
    device_id = file_guid.read()

    if not device_id or reset:
        device_id = str("%016X" % create_id())
        file_guid = xbmcvfs.File(nakamori_guid, "w")
        file_guid.write(device_id)

    file_guid.close()

    xbmcgui.Window(10000).setProperty('nakamori_deviceId', device_id)
    return device_id


def message_box(title, text):
    xbmcgui.Dialog().ok(title, text)


def bold(value):
    return ''.join(['[B]', value, '[/B]'])


def color(text_to_color, color_name, enable_color=True):
    if enable_color:
        return ''.join(['[COLOR %s]' % color_name, text_to_color, '[/COLOR]'])
    return text_to_color


def move_to(position: int = 0):
    if plugin_addon.getSettingBool('select_first'):
        try:
            xbmc.sleep(100)
            win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
            cid = win.getFocusId()
            ctl = win.getControl(cid)
            ctl.selectItem(int(position))
        except Exception as e:
            xbmc.log(f'--- move_to did not work this time: {e}', xbmc.LOGINFO)


def debug(text: str):
    if plugin_addon.getSettingBool("debug_log"):
        xbmc.log(f'== [NAKA_DEBUG] == {text}', xbmc.LOGINFO)

def if_debug():
    if plugin_addon.getSettingBool("debug_log"):
        return True
    return False
