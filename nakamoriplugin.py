# -*- coding: utf-8 -*-

# moje
from lib import kodi_utils
from lib import shoko_utils
from models import kodi_models
# nie moje

import routing
from lib.windows import wizard
import xbmc
from xbmcgui import ListItem
from xbmcplugin import addDirectoryItem, endOfDirectory

plugin = routing.Plugin()


@plugin.route('/')
def index():
    for x in kodi_models.ListAllFilters():
        addDirectoryItem(plugin.handle, plugin.url_for(show_filter, "one"), x, True)
    endOfDirectory(plugin.handle)


@plugin.route('/category/<category_id>')
def show_category(category_id):
    addDirectoryItem(plugin.handle, "", ListItem("Hello category %s!" % category_id))
    endOfDirectory(plugin.handle)


@plugin.route('/directory/<path:dir>')
def show_directory(dir):
    addDirectoryItem(plugin.handle, "", ListItem("List directory %s!" % dir))
    endOfDirectory(plugin.handle)


@plugin.route('/filter/<filter_id>')
def show_filter(filter_id):
    kodi_models.ListAllFilters()

def main():
    # stage 0 - everything before connecting
    kodi_utils.get_device_id()

    # stage 1 - check connection
    if not shoko_utils.can_connect():
        kodi_utils.message_box("not connect", 'cannot connect')
        xbmc.executebuiltin("Dialog.Close(all, true)")
        if wizard.open_connection_wizard():
            pass
        if not shoko_utils.can_connect():
            raise RuntimeError("try again with other settings")

    # stage 2 - Check server startup status
    if not shoko_utils.get_server_status():
        pass

    # stage 3 - auth
    auth = shoko_utils.auth()
    if not auth:
        kodi_utils.message_box("auth", "error")
        xbmc.executebuiltin("Dialog.Close(all, true)")
        if wizard.open_login_wizard():
            pass
        auth = shoko_utils.auth()
        if not auth:
            raise RuntimeError("try again with other settings")
    else:
        return True


if __name__ == '__main__':
    if main():
        plugin.run()
