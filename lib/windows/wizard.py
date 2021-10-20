# -*- coding: utf-8 -*-
import xbmcgui
import xbmcaddon

from lib import shoko_utils, kodi_utils

plugin_addon = xbmcaddon.Addon(id='plugin.video.nakamori')
CWD = plugin_addon.getAddonInfo('path')

MSG_HEADER = plugin_addon.getLocalizedString(30334)
MSG_CONNECT = plugin_addon.getLocalizedString(30335)
MSG_NOAUTH = plugin_addon.getLocalizedString(30336)

OK_BUTTON = 201
ACTION_PREVIOUS_MENU = 10
ACTION_NAV_BACK = 92
IP_ADDRESS = 203
PORT_NUMBER = 204
LOGIN = 205
PASSWORD = 206
LABEL_PASSWORD = 306
LABEL_IP_ADDRESS = 303
LABEL_PORT_NUMBER = 304
LABEL_LOGIN = 305

# noinspection PyUnusedName
CENTER_Y = 6
# noinspection PyUnusedName
CENTER_X = 2

# resources
RSC_OK = plugin_addon.getLocalizedString(30327)
COLOR_WHITE = '0xAAFFFFFF'


# noinspection PyUnusedFunction,PySameParameterValue
class LoginWizard(xbmcgui.WindowXML):
    def __init__(self, xml_file, resource_path, skin, skin_res):
        xbmcgui.WindowXML.__init__(self, xml_file, resource_path, skin, skin_res, False)
        self.window_type = 'window'
        self.login = ''
        self.password = ''
        self.apikey = None
        self.cancelled = True
        # additional variables
        self._button_ok = None
        self._box_login = None
        self._box_password = None
        self._label_login = None
        self._label_password = None

    def onInit(self):
        # self.setProperty('script.module.nakamori.running', 'true')
        # static bind
        self._button_ok = self.getControl(OK_BUTTON)
        self._label_login = self.getControl(LABEL_LOGIN)
        self._label_password = self.getControl(LABEL_PASSWORD)
        self._box_login = self.getControl(LOGIN)
        self._box_password = self.getControl(PASSWORD)
        # navigation
        # up, down, left, right
        self._box_login.setNavigation(self._box_login, self._box_password, self._box_login, self._button_ok)
        self._box_password.setNavigation(self._box_login, self._box_password, self._box_password, self._button_ok)
        self._button_ok.setNavigation(self._button_ok, self._button_ok, self._box_login, self._button_ok)
        # get current settings
        self.login = plugin_addon.getSetting('login')
        self.password = plugin_addon.getSetting('password')
        self.apikey = plugin_addon.getSetting('apikey')
        # validate
        if not isinstance(self._box_login, xbmcgui.ControlEdit):
            return
        if not isinstance(self._box_password, xbmcgui.ControlEdit):
            return
        if not isinstance(self._button_ok, xbmcgui.ControlButton):
            return
        if not isinstance(self._label_login, xbmcgui.ControlLabel):
            return
        if not isinstance(self._label_password, xbmcgui.ControlLabel):
            return

        # populate controls
        self._box_login.setText(self.login)
        self._box_password.setText(self.password)
        self._box_password.setType(xbmcgui.INPUT_TYPE_PASSWORD, plugin_addon.getLocalizedString(30300))
        self._button_ok.setLabel(label=RSC_OK, textColor=COLOR_WHITE, focusedColor=COLOR_WHITE)

        # set focus
        self.setFocus(self._box_login)

    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU:
            # self.setProperty('script.module.nakamori.running', 'false')
            self.close()
        if action == ACTION_NAV_BACK:
            self.close()

    def onControl(self, control):
        pass

    def onFocus(self, control):
        pass

    def onClick(self, control):
        if control == OK_BUTTON:
            # populate info from edits
            self.login = str(self._box_login.getText()).strip()
            self.password = str(self._box_password.getText()).strip()
            # check auth
            self.apikey = None
            try:
                self.apikey = shoko_utils.get_apikey(self.login, self.password)
            except:
                print('error')

            if self.apikey is not None:
                # this action is not saved to settings (at first run)
                plugin_addon.setSetting(id='apikey', value=str(self.apikey))
                plugin_addon.setSetting(id='login', value='')
                plugin_addon.setSetting(id='password', value='')
                if shoko_utils.can_user_connect(self.apikey):
                    # self.setProperty('script.module.nakamori.running', 'false')
                    self.cancelled = False
                    self.close()
                    return

            kodi_utils.message_box(MSG_HEADER, MSG_NOAUTH)


# noinspection PyUnusedFunction,PySameParameterValue
class ConnectionWizard(xbmcgui.WindowXML):
    def __init__(self, xml_file, resource_path, skin, skin_res):
        xbmcgui.WindowXML.__init__(self, xml_file, resource_path, skin, skin_res, False)
        self.window_type = 'window'
        self.ip = None
        self.port = None
        # additional variables
        self.cancelled = True
        self._box_ip = None
        self._box_port = None
        self._button_ok = None
        self._label_address = None
        self._label_port = None

    def onInit(self):
        self.setProperty('script.module.nakamori.running', 'true')
        # static bind
        self._box_ip = self.getControl(IP_ADDRESS)
        self._box_port = self.getControl(PORT_NUMBER)
        self._button_ok = self.getControl(OK_BUTTON)
        self._label_address = self.getControl(LABEL_IP_ADDRESS)
        self._label_port = self.getControl(LABEL_PORT_NUMBER)
        # validate, this also allows PyCharm to use intellisense
        if not isinstance(self._box_ip, xbmcgui.ControlEdit):
            return
        if not isinstance(self._box_port, xbmcgui.ControlEdit):
            return
        if not isinstance(self._button_ok, xbmcgui.ControlButton):
            return
        if not isinstance(self._label_address, xbmcgui.ControlLabel):
            return
        if not isinstance(self._label_port, xbmcgui.ControlLabel):
            return
        # navigation
        # up, down, left, right
        self._box_ip.setNavigation(self._box_ip, self._box_port, self._box_ip, self._button_ok)
        self._box_port.setNavigation(self._box_ip, self._box_port, self._box_port, self._button_ok)
        self._button_ok.setNavigation(self._button_ok, self._button_ok, self._box_ip, self._button_ok)
        # get current settings
        self.ip = plugin_addon.getSetting('ipaddress')
        self.port = plugin_addon.getSetting('port')
        # populate controls
        self._box_ip.setText(self.ip)
        self._box_port.setText(self.port)

        self._button_ok.setLabel(label=RSC_OK, textColor=COLOR_WHITE, focusedColor=COLOR_WHITE)
        # set focus
        self.setFocus(self.getControl(IP_ADDRESS))

    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU:
            # self.setProperty('script.module.nakamori.running', 'false')
            self.close()
        if action == ACTION_NAV_BACK:
            self.close()

    def onControl(self, control):
        pass

    def onFocus(self, control):
        pass

    def onClick(self, control):
        if control == OK_BUTTON:
            if shoko_utils.can_connect(ip=str(self._box_ip.getText()), port=int(self._box_port.getText())):
                plugin_addon.setSetting(id='ipaddress', value=str(self._box_ip.getText()))
                plugin_addon.setSetting(id='port', value=str(self._box_port.getText()))
                self.cancelled = False
                self.close()
            else:
                # show message
                kodi_utils.message_box(MSG_HEADER, MSG_CONNECT)


def open_connection_wizard():
    ui = ConnectionWizard('connection_wizard.xml', CWD, 'default', '1080i')
    ui.doModal()
    x = ui.cancelled
    del ui
    return x


def open_login_wizard():
    ui = LoginWizard('login_wizard.xml', CWD, 'default', '1080i')
    ui.doModal()
    x = ui.cancelled
    a = ui.apikey
    del ui
    return x, a
