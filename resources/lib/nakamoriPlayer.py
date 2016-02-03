import xbmc, sys, xbmcgui

class nakamoriPlayer (xbmc.Player):
    def __init__ (self):
        self.is_active = True
        self.finished = False
        xbmc.Player.__init__(self)
        print("Player Nakamori Initiated <---------")

    def play(self, listitem, windowed):
         xbmc.Player().play(listitem=listitem)

    def playplaylist(self, playlist):
         xbmc.Player().play(item=playlist)

    def onPlayBackEnded(self):
        # Will be called when xbmc stops playing a file
        print("Nakamori Playback: onPlayBackEnded <---------")
        finished=True
        xbmc.executebuiltin('RunScript(plugin.video.nakamoriplugin, %s, %s&cmd=watched)' % (sys.argv[1], sys.argv[2]))

    def onPlayBackStopped(self):
        # Will be called when user stops xbmc playing a file
        print("Nakamori Playback: onPlayBackStopped <---------")

    def onPlayBackStarted(self):
        # Will be called when xbmc starts playing a file
        print("Nakamori Playback: STARTED <---------")

    def onPlayBackPaused(self):
        # Will be called when user pauses a playing file
        print("Nakamori Playback: PAUSE <---------")
        self._totalTime = self.getTotalTime()
        self._currentTime = self.getTime()

    def onPlayBackResumed(self):
        #Will be called when user resumes a paused file
        print("Nakamori Playback: RESUMED <---------")

    def isFinished(self):
        self.finished = True
        finished = True

finished  = False
_totalTime = 0
_currentTime = 0