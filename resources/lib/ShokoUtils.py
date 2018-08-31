# -*- coding: utf-8 -*-
import nakamoritools as nt
from resources.lib import KodiUtils

import xbmc


def folder_list():
    """
    List all import folders
    :return: int vl of picked folder
    """
    return KodiUtils.import_folder_list()


def mediainfo_update():
    """
    Update mediainfo for all files
    :return:
    """
    nt.get_json(nt.server + "/api/mediainfo_update")


def stats_update():
    """
    Update stats via server
    :return:
    """
    nt.get_json(nt.server + "/api/stats_update")


def rescan_file(params, rescan):
    """
    Rescans or rehashes a file
    Args:
        params:
        rescan: True to rescan, False to rehash
    """
    vl_id = params.get('vl', '')
    if vl_id != 0:
        command = 'rehash'
        if rescan:
            command = 'rescan'

        key_url = ""
        if vl_id != '':
            key_url = nt.server + "/api/" + command + "?id=" + vl_id
        if nt.addon.getSetting('log_spam') == 'true':
            xbmc.log('vlid: ' + str(vl_id), xbmc.LOGWARNING)
            xbmc.log('key: ' + key_url, xbmc.LOGWARNING)

        nt.get_json(key_url)

        xbmc.executebuiltin("XBMC.Notification(%s, %s, 2000, %s)" % (
            nt.addon.getLocalizedString(30190) if rescan else nt.addon.getLocalizedString(30189),
            nt.addon.getLocalizedString(30191), nt.addon.getAddonInfo('icon')))
        xbmc.sleep(10000)
        nt.refresh()


def remove_missing_files():
    """
    Run "remove missing files" on server to remove every file that is not accessible by server
    :return:
    """
    key = nt.server + "/api/remove_missing_files"

    if nt.addon.getSetting('log_spam') == 'true':
        xbmc.log('key: ' + key, xbmc.LOGWARNING)

    nt.get_json(key)
    xbmc.executebuiltin("XBMC.Notification(%s, %s, 2000, %s)" % (nt.addon.getLocalizedString(30192),
                                                                 nt.addon.getLocalizedString(30193),
                                                                 nt.addon.getAddonInfo('icon')))
    xbmc.sleep(10000)
    nt.refresh()
