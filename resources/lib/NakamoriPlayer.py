# -*- coding: utf-8 -*-
import xbmc
import time
import xbmcgui
from util import *

class NakamoriPlayer(xbmc.Player):

    _playing = False
    currentPlaylistIndex = None

    def __init__(self, *args, **kwargs):
        pass

    # called when kodi starts playing a file
    def onPlayBackStarted(self):
        xbmc.sleep(1000)
        self.type = None
        self.id = None

        # wait a second
        if not xbmc.abortRequested:
            time.sleep(1)
            if not self.isPlayingVideo():
                return

        # only do anything if we're playing a video
        if self.isPlayingVideo():
            # get item data from json rpc
            activePlayers = kodi_jsonrpc('{"jsonrpc": "2.0", "method": "Player.GetActivePlayers", "id": 1}')
            playerId = int(activePlayers[0]['playerid'])
            result = kodi_jsonrpc("{'jsonrpc': '2.0', 'method': 'Player.GetItem', 'params': {'playerid':" + str(playerId) + "}, 'id': 1}")
            if result:
                # playing started
                dump_dictionary(result, 'Player.GetItem results')

                # handle playlists
                playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
                playlist_size = len(playlist)
                if playlist_size > 1:
                    pos = playlist.getposition()
                    if not self.currentPlaylistIndex is None:
                        # skipped to next file
                        self.onPlayBackEnded()
                    self.currentPlaylistIndex = pos
                    # the next file is playing

                self._playing = True


    # called when kodi stops playing a file
    def onPlayBackEnded(self):
        if self._playing:
            self._playing = False
            self.currentPlaylistIndex = None
            pass

    # called when user stops kodi playing a file
    def onPlayBackStopped(self):
        if self._playing:
            self._playing = False
            self.currentPlaylistIndex = None
            pass

    # called when user pauses a playing file
    def onPlayBackPaused(self):
        if self._playing:
            pass

    # called when user resumes a paused file
    def onPlayBackResumed(self):
        if self._playing:
            pass

    # called when user seeks to a time
    def onPlayBackSeek(self, time, offset):
        if self._playing:
            pass

    # called when user performs a chapter seek
    def onPlayBackSeekChapter(self, chapter):
        if self._playing:
            pass