# -*- coding: utf-8 -*-
import nakamoritools as nt
from resources.lib import kodi_utils

import xbmc


localization_notification_map = {
    'rescan': nt.addon.getLocalizedString(30190),
    'rehash': nt.addon.getLocalizedString(30189),
    'runimport': nt.addon.getLocalizedString(30198),
    'folderscan': nt.addon.getLocalizedString(30199),
}

localization_refresh_map = {
    'refresh10': nt.addon.getLocalizedString(30191),
    'awhile': nt.addon.getLocalizedString(30193),
}


def perform_server_action(command, object_id=None, refresh='refresh10', post=False):
    """
    Performs an action on the server
    Args:
        object_id: the object_id or None
        command: string representing api/command?object_id=...
        refresh: whether to refresh
        post: is it a POST endpoint
    """
    key_url = nt.server + "/api/" + command
    if object_id is not None and object_id != 0 and object_id != '':
        key_url = nt.set_parameter(key_url, 'id', object_id)
    if nt.addon.getSetting('spamLog') == 'true':
        xbmc.log('object_id: ' + str(object_id), xbmc.LOGWARNING)
        xbmc.log('key: ' + key_url, xbmc.LOGWARNING)

    if post:
        response = nt.post_json(key_url, '')
    else:
        response = nt.get_json(key_url)

    if nt.addon.getSetting('spamLog') == 'true':
        xbmc.log('response: ' + response, xbmc.LOGWARNING)

    refresh_message = localization_refresh_map.get(refresh, '')
    xbmc.executebuiltin("XBMC.Notification(%s, %s, 2000, %s)" % (
        localization_notification_map.get(command, command),
        refresh_message, nt.addon.getAddonInfo('icon')))

    # there's a better way to do this, but I don't feel like trying to make it work in Python
    if refresh != '' and refresh != 'awhile':
        xbmc.sleep(10000)
        nt.refresh()


def rescan_file(object_id):
    """
    This rescans a file for info from AniDB.
    :param object_id: VideoLocalID
    """
    perform_server_action('rescan', object_id=object_id)


def rehash_file(object_id):
    """
    This rehashes and rescans a file
    :param object_id: VideoLocalID
    """
    perform_server_action('rehash', object_id=object_id)


def folder_list():
    """
    List all import folders
    :return: ImportFolderID of picked folder
    """
    return kodi_utils.import_folder_list()


def mediainfo_update():
    """
    Update mediainfo for all files
    :return:
    """
    perform_server_action('mediainfo_update', refresh='awhile')


def stats_update():
    """
    Update stats via server
    :return:
    """
    perform_server_action('stats_update', refresh='awhile')


def run_import():
    """
    THIS DOES NOT HAVE API YET. DON'T TRY TO USE IT
    Same as pressing run import in Shoko. It performs many tasks, such as checking for files that are not added
    :return: None
    """
    pass


def scan_folder(object_id):
    """
    THE API FOR THIS IS BROKEN. DON'T TRY TO USE IT
    Scans an import folder. This checks files for hashes and adds new ones. It takes longer than run import
    :param object_id:
    :return:
    """
    pass


def remove_missing_files():
    """
    Run "remove missing files" on server to remove every file that is not accessible by server
    This give a different localization, so for now, use another method. Ideally, we would make an Enum for Refresh Message
    :return:
    """
    perform_server_action('remove_missing_files', refresh='awhile')
