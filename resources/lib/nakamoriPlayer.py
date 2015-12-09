import xbmc

class nakamoriPlayer (xbmc.Player):
    def __init__ (self):
        #xbmc.Player.__init__(self)
        print("Player nakamori Initiated")

    def onPlayBackEnded(self):
        # Will be called when xbmc stops playing a file
        print "seting event in onPlayBackEnded " 
        self.stopPlaying.set();
        print "stop Event is SET" 

    def onPlayBackStopped(self):
        # Will be called when user stops xbmc playing a file
        print "seting event in onPlayBackStopped " 
        self.stopPlaying.set();
        print "stop Event is SET" 

    def setStopEvent(self, stopEvent):
        print 'stored stop event'
        self.stopPlaying=stopEvent;

    def onPlayBackStarted(self):
        # Will be called when xbmc starts playing a file
        print 'Beginning Nakamori Playback'
        self._totalTime = self.getTotalTime()
        self._tracker = threading.Thread(target=self._trackPosition)
        self._tracker.start()