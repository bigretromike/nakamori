import urllib2
import re
import urllib
import json
import sys
import os.path
import time
import base64
import datetime
import xml.etree.ElementTree as tree
import xbmcaddon
import xbmcplugin
import xbmcgui
import resources.lib.util as util

handle = int(sys.argv[1])
addon = xbmcaddon.Addon(id='plugin.video.nakamoriplugin')

urlopen = urllib2.urlopen
Request = urllib2.Request


#Internal function
def getHtml(url, referer):
    referer=urllib2.quote(referer).replace("%3A", ":")
    req = Request(url)
    if len(referer) > 1:
        req.add_header('Referer', referer)
    #response = urlopen(req, timeout=int(addon.getSetting('timeout')))
    response = urlopen(req, timeout=60)
    data = response.read()
    response.close()
    return data

def setWindowHeading(tree) :
    WINDOW = xbmcgui.Window( xbmcgui.getCurrentWindowId() )
    try:
        WINDOW.setProperty("heading", tree.get('title1'))
    except:
        WINDOW.clearProperty("heading")
    try:
        WINDOW.setProperty("heading2", tree.get('title2'))
    except:
        WINDOW.clearProperty("heading2")

def addGUIItem(url, details, extraData, context=None, folder=True):

    if extraData.get('parameters'):
        for argument, value in extraData.get('parameters').items():
            link_url = "%s&%s=%s" % (link_url, argument, urllib.quote(value))
    link_url = url
    liz=xbmcgui.ListItem(details.get('title', 'Unknown'), thumbnailImage=extraData.get('thumb'))

    #Set the properties of the item, such as summary, name, season, etc
    liz.setInfo(type=extraData.get('type','Video'), infoLabels=details )

    #For all end items    
    if not folder:
        liz.setProperty('IsPlayable', 'true')

        if extraData.get('type','video').lower() == "video":
            liz.setProperty('TotalTime', str(extraData.get('duration')))
            liz.setProperty('ResumeTime', str(extraData.get('resume')))

            liz.setProperty('VideoResolution', str(extraData.get('xVideoResolution','')))
            liz.setProperty('VideoCodec', extraData.get('xVideoCodec',''))
            liz.setProperty('AudioCodec', extraData.get('xAudioCodec',''))
            liz.setProperty('AudioChannels', str(extraData.get('xAudioChannels','')))
            liz.setProperty('VideoAspect', str(extraData.get('xVideoAspect','')))

            video_codec={}
            if extraData.get('VideoCodec'): video_codec['codec'] = extraData.get('VideoCodec')
            if extraData.get('height') : video_codec['height'] = int(extraData.get('height'))
            if extraData.get('width') : video_codec['width'] = int(extraData.get('width'))
            if extraData.get('duration') : video_codec['duration'] = extraData.get('duration')

            audio_codec={}
            if extraData.get('AudioCodec') : audio_codec['codec'] = extraData.get('AudioCodec')
            if extraData.get('AudioChannels') : audio_codec['channels'] = int(extraData.get('AudioChannels'))
            if extraData.get('AudioLanguage') : audio_codec['language'] = extraData.get('AudioLanguage')

            liz.addStreamInfo('video', video_codec )
            liz.addStreamInfo('audio', audio_codec )

    if extraData.get('source') == 'tvshows' or extraData.get('source') =='tvseasons':
        #Then set the number of watched and unwatched, which will be displayed per season
        liz.setProperty('TotalEpisodes', str(extraData['TotalEpisodes']))
        liz.setProperty('WatchedEpisodes', str(extraData['WatchedEpisodes']))
        liz.setProperty('UnWatchedEpisodes', str(extraData['UnWatchedEpisodes']))

        #Hack to show partial flag for TV shows and seasons
        if extraData.get('partialTV') == 1:            
            liz.setProperty('TotalTime', '100')
            liz.setProperty('ResumeTime', '50')

    #fanart is nearly always available, so exceptions are rare.
    try:
        liz.setProperty('fanart_image', extraData.get('fanart_image'))
    except:
        pass

    if extraData.get('banner'):
        liz.setProperty('banner', '%s' % extraData.get('banner', ''))

    if extraData.get('season_thumb'):
        liz.setProperty('seasonThumb', '%s' % extraData.get('season_thumb', ''))

    if context is None:
        if extraData.get('type','video').lower() == "video":
            context=[]
            url_peep = sys.argv[2]
            #xbmcgui.Dialog().ok('TESTUJEMY', url, str(extraData.get('source','none')))
            if 'mode=4' in url_peep:
                url_peep = url_peep + "&anime_id=" + extraData.get('key') +"&cmd=vote"
                context.append(('Vote', 'RunScript(plugin.video.nakamoriplugin, %s, %s)' % (sys.argv[1] ,url_peep)))
            #elif 'mode=5' in url_peep:
                #url = url + "&anime_id=" + extraData.get('key')[2:]+"&cmd=vote"
                #context.append(('Vote', 'RunScript(plugin.video.nakamoriplugin, %s, %s)' % (sys.argv[1] ,url_peep)))
            elif 'mode=6' in url_peep:
                url_peep = url_peep + "&anime_id=" + extraData.get('parentKey') + "&ep_id=" + extraData.get('jmmepisodeid') 
                context.append(('Vote', 'RunScript(plugin.video.nakamoriplugin, %s, %s&cmd=vote)' % (sys.argv[1] ,url_peep)))
                context.append(('Mark as Watched', 'RunScript(plugin.video.nakamoriplugin, %s, %s&cmd=watched)' % (sys.argv[1] ,url_peep)))
                context.append(('Mark as Unwatched', 'RunScript(plugin.video.nakamoriplugin, %s, %s&cmd=unwatched)' % (sys.argv[1] ,url_peep)))
            liz.addContextMenuItems(context)
    return xbmcplugin.addDirectoryItem(handle,url,listitem=liz,isFolder=folder)

#Adding items to list/menu:
def buildMainMenu():
    xbmcplugin.setContent(handle, content='tvshows')
    e=tree.XML(getHtml("http://" + addon.getSetting("ipaddress") + ":" + addon.getSetting("port") + "/jmmserverkodi/getfilters/" + addon.getSetting("userid"),""))
    for atype in e.findall('Directory'):
        title=atype.get('title')
        url=atype.get('key')
        thumb=atype.get('thumb')
        u=sys.argv[0]+"?url="+url+"&mode="+str(4)+"&name="+urllib.quote_plus(title)
        liz=xbmcgui.ListItem(label=title, label2=title, iconImage="DefaultVideo.png",  thumbnailImage=thumb, path=url)
        liz.setInfo( type="Video", infoLabels={ "Title": title } )
        xbmcplugin.addDirectoryItem(handle,url=u,listitem=liz,isFolder=True)
    util.addDir("Search", "http://" + addon.getSetting("ipaddress") + ":" + addon.getSetting("port") + "/jmmserverkodi/search/" + addon.getSetting("userid") + "/"+ addon.getSetting("maxlimit") +"/", 3, "http://" + addon.getSetting("ipaddress") + ":" + addon.getSetting("port") + "/jmmserverkodi/GetSupportImage/plex_others.png","2","3","4")
    xbmcplugin.endOfDirectory(handle)

def buildTVShows(params):
    xbmcplugin.setContent(handle, 'tvshows')
    xbmcplugin.addSortMethod(handle, 37 ) #maintain original plex sorted
    xbmcplugin.addSortMethod(handle, 25 ) #video title ignore THE
    xbmcplugin.addSortMethod(handle, 3 )  #date
    xbmcplugin.addSortMethod(handle, 18 ) #rating
    xbmcplugin.addSortMethod(handle, 17 ) #year
    xbmcplugin.addSortMethod(handle, 28 ) #by MPAA
    
    #Get XML from JMMServer
    e=tree.XML(getHtml(params['url'],''))

    setWindowHeading(e)
    for atype in e.findall('Directory'):
        #new aproche
        tempgenre=[]

        for child in atype:
            if child.tag == "Genre":
                tempgenre.append(child.get('tag','')) #atype.find('Tag').get('tag')
        watched = int(atype.get('viewedLeafCount',0))

        #Extended support
        cast = [ ]
        listCast = []
        listCastAndRole = []
        if atype.find('Characters'):
            for char in atype.find('Characters').findall('Character'):
                char_id = char.get('charID')
                char_charname=char.get('charname')
                char_picture=char.get('picture','')
                char_desc=char.get('description','')
                char_seiyuuname=char.get('seiyuuname','')
                char_seiyuupic=char.get('seiyuupic','')
                listCast.append(char_charname)
                listCastAndRole.append((char_charname, char_seiyuuname))
        else:
             cast = [ ]
        cast = [listCast, listCastAndRole]
        #Extended support END#

        details={
        #'count': count,
        #'size': size,
        #'Date': date, 
        'title': atype.get('title','Unknown').encode('utf-8') , 
        'genre':  " / ".join(tempgenre),
        'year': int(atype.get('year',0)),
        'episode': int(atype.get('leafCount',0)),
        'season': int(atype.get('season',0)),
        #top250 : integer (192,
        #tracknumber : integer (3,
        'rating': atype.get('rating'),
        #'playcount': int(atype.get('viewedLeafCount')),
        #overlay : integer (2, - range is 0..8. See GUIListItem.h for values
        'cast': cast[0], #cast : list (Michal C. Hall,
        'castandrole': cast[1], # : list (Michael C. Hall|Dexter,
        #director : string (Dagur Kari,
        'mpaa': atype.get('contentRating',''),
        'plot': atype.get('summary','').encode('utf-8'),
        #'plotoutline': plotoutline,
        #'originaltitle': atype.get('original_title').encode("utf-8"),
        'sorttitle': atype.get('title','Unknown').encode('utf-8'),
        #'Duration': duration,
        #'Studio':studio, < ---
        #'Tagline': tagline,
        #'Writer': writer,
        #'tvshowtitle': tvshowtitle,
		'tvshowname' : atype.get('title','Unknown').encode('utf-8'),
        #'premiered': premiered,
        #'Status': status,
        #code : string (tt0110293, - IMDb code
        'aired': atype.get('originallyAvailableAt',''),
        #credits : string (Andy Kaufman, - writing credits
        #'Lastplayed': lastplayed,
        #album : string (The Joshua Tree,
        #artist : list (['U2'],
        'votes': atype.get('votes'),
        #trailer : string (/home/user/trailer.avi,
        'dateadded': atype.get('addedAt')
        }
        
        extraData={ 'type'              : 'video' ,
                   'source'            : 'tvshows',
                   'UnWatchedEpisodes' : int(details['episode']) - watched,
                   'WatchedEpisodes'   : watched,
                   'TotalEpisodes'     : details['episode'],
                   'thumb'             : atype.get('thumb') ,
                   'fanart_image'      : e.get('art','')  ,
                   'key'               : atype.get('key','') ,
                   'ratingKey'         : str(atype.get('ratingKey',0))  #<------
                   #'ArtistThumb'     :  'http://s-media-cache-ak0.pinimg.com/236x/11/13/ac/1113acce3968360db3d0280526fd5382.jpg'  #<-----------
                 }

        url=atype.get('key')

        #Set up overlays for watched and unwatched episodes
        if extraData['WatchedEpisodes'] == 0:
            details['playcount'] = 0
        elif extraData['UnWatchedEpisodes'] == 0:
            details['playcount'] = 1
        else:
            extraData['partialTV'] = 1

        #u=sys.argv[0]+"?url="+url+"&mode="+str(2)+"&name="+urllib.quote_plus(details['title'])+"&poster_file="+urllib.quote_plus(extraData['thumb'])+"&filename="+urllib.quote_plus("none")
        u=sys.argv[0]+"?url="+url+"&mode="+str(5)
        context=None
        addGUIItem(u,details,extraData, context)
        #liz=xbmcgui.ListItem(title, thumbnailImage=thumb) <<<<<<<<<<<<<<<

        #liz.setInfo( type="Video", infoLabels = info) <<<<<<<<<<<<<<
        #liz.setProperty('IsPlayable', 'False') <<<<<<<<<<<<<
        #Let's set some arts
        #liz.setArt({ 'thumb': thumb, 'poster': poster, 'banner' : banner, 'fanart': fanart, 'clearart': clearart, 'clearlogo': clearlogo, 'landscape': landscape})
        #This should work
        #liz.setProperty('TotalEpisodes', str(10))
        #liz.setProperty('WatchedEpisodes', str(5))
        #liz.setProperty('UnWatchedEpisodes', str(5))
        #Hack to show partial flag for TV shows and seasons
        #liz.setProperty('TotalTime', '100')
        #liz.setProperty('ResumeTime', '50')
        #xbmcplugin.addDirectoryItem(handle,url=u,listitem=liz,isFolder=True) <<<<<<<<<<<<<<
    xbmcplugin.endOfDirectory(handle)

def buildTVSeasons(params):
    xbmcplugin.setContent(handle, 'seasons')

    e=tree.XML(getHtml(params['url'],''))
    setWindowHeading(e)

    if not e.find('Directory'):
        params['url'] = params['url'].replace('&mode=5','&mode=6')
        buildTVEpisodes(params)
        return

    willFlatten=False
    #check for a single season
    if int(e.get('size',0)) == 1:
        willFlatten=True

    sectionart=e.get('art','') #<------------------
    banner=e.get('banner','') #<-----------------
    setWindowHeading(e)
    #For all the directory tags
    plot=e.get('summary','').encode('utf-8')

    for atype in e.findall('Directory'):
        if willFlatten:
            url=atype.get('key')
            u=sys.argv[0]+"?url=" + url + "&mode="+str(6)
            buildTVEpisodes(u)
            return

        watched=int(atype.get('viewedLeafCount',0))

        #Create the basic data structures to pass up
        details={'title'      : atype.get('title','Unknown').encode('utf-8') ,
                 'tvshowname' : atype.get('title','Unknown').encode('utf-8') ,
                 'sorttitle'  : atype.get('titleSort', atype.get('title','Unknown')).encode('utf-8') ,
                 'studio'     : atype.get('studio','').encode('utf-8') ,
                 'plot'       : plot ,
                 'season'     : int(atype.get('season',0)) ,
                 'episode'    : int(atype.get('leafCount',0)) ,
                 'mpaa'       : atype.get('contentRating','') ,
                 'aired'      : atype.get('originallyAvailableAt','') }

        if atype.get('sorttitle'): details['sorttitle'] = season.get('sorttitle')

        extraData={'type'              : 'video' ,
                   'source'            : 'tvseasons',
                   'TotalEpisodes'     : details['episode'],
                   'WatchedEpisodes'   : watched ,
                   'UnWatchedEpisodes' : details['episode'] - watched ,
                   'thumb'             :  atype.get('thumb','') ,
                   'fanart_image'      : atype.get('art','') ,
                   'key'               : atype.get('key','') ,
                   'ratingKey'         : str(atype.get('ratingKey',0)) , #<--------------
                   'mode'              : str(6) }

        if banner:
            extraData['banner']=banner

        if extraData['fanart_image'] == "":
            extraData['fanart_image']=sectionart

        #Set up overlays for watched and unwatched episodes
        if extraData['WatchedEpisodes'] == 0:
            details['playcount'] = 0
        elif extraData['UnWatchedEpisodes'] == 0:
            details['playcount'] = 1
        else:
            extraData['partialTV'] = 1

        url=sys.argv[0]+"?url=" + extraData['key'] + "&mode="+str(6)
        context=None

        #Build the screen directory listing
        addGUIItem(url,details,extraData, context)

    xbmcplugin.endOfDirectory(handle)

def buildTVEpisodes(params):
    xbmcplugin.setContent(handle, 'episodes')

    e=tree.XML(getHtml(params['url'],''))
    setWindowHeading(e)
    #get banner thumb
    banner = e.get('banner','') #<----------
    art = e.get('art','')

    #get season thumb for SEASON NODE
    season_thumb = e.get('thumb','')
    #Set Sort Method
    xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_EPISODE )  #episode
    xbmcplugin.addSortMethod(handle, 3 )  #date
    xbmcplugin.addSortMethod(handle, 25 ) #video title ignore THE
    xbmcplugin.addSortMethod(handle, 19 )  #date added
    xbmcplugin.addSortMethod(handle, 18 ) #rating
    xbmcplugin.addSortMethod(handle, 17 ) #year
    xbmcplugin.addSortMethod(handle, 29 ) #runtime
    xbmcplugin.addSortMethod(handle, 28 ) #by MPAA

    for atype in e.findall('Video'):
        tempgenre=[]
        tempcast=[]
        tempdir=[]
        tempwriter=[]

        #Gather some data
        view_offset=atype.get('viewOffset',0)
        duration=int(atype.find('Media').get('duration'))/1000
        #Required listItem entries for XBMC
        details={'plot'        : atype.get('summary','').encode('utf-8') ,
                 'title'       : atype.get('title','Unknown').encode('utf-8') ,
                 'sorttitle'   : atype.get('titleSort', atype.get('title','Unknown')).encode('utf-8')  ,
                 'rating'      : float(atype.get('rating',0)) ,
                 #'studio'      : episode.get('studio',tree.get('studio','')).encode('utf-8') ,
                 'duration'    : str(datetime.timedelta(seconds=duration)) ,
                 'mpaa'        : atype.get('contentRating','') ,
                 'year'        : int(atype.get('year',0)) ,
                 'tagline'     : atype.get('tagline','').encode('utf-8') ,
                 'episode'     : int(atype.get('index',0)),
                 'aired'       : atype.get('originallyAvailableAt','') ,
                 'tvshowtitle' : atype.get('grandparentTitle',atype.get('grandparentTitle','')).encode('utf-8') , #<-----------------------
                 'votes'        : int(atype.get('votes',0)) ,
                 'originaltitle' : atype.get('original_title','') ,
                 'size'          : int(atype.find('Media').find('Part').get('size',0)) ,
                 'season'      : int(atype.get('season',0)) }

        #Extra data required to manage other properties
        extraData={'type'         : "Video" ,
                   'source'       : 'tvepisodes',
                   'thumb'        : atype.get('thumb','') ,
                   'fanart_image' : art ,
                   'key'          : atype.get('key',''),
                   #'ratingKey'    : str(episode.get('ratingKey',0)),
                   #'duration'     : duration,
                   'resume'       : int(int(view_offset)/1000),
                   'parentKey'   : atype.get('parentKey','0'),
                   'jmmepisodeid' : atype.get('JMMEpisodeId','0') }

	    #Information about streams inside video file
        extraData['xVideoResolution'] = atype.find('Media').get('videoResolution',0)
        extraData['xVideoCodec']= atype.find('Media').get('audioCodec','')
        extraData['xVideoAspect']=float(atype.find('Media').get('aspectRatio',0))
        extraData['xAudioCodec']= atype.find('Media').get('videoCodec','')
        extraData['xAudioChannels']=int(atype.find('Media').get('audioChannels',0))
        
        for vtype in atype.find('Media').find('Part').findall('Stream'): #<-----------------nadpisuje dane
            stream=int(vtype.get('streamType'))
            if stream == 1:
                #video
                extraData['VideoCodec'] = vtype.get('codec','')
                extraData['width'] = int(vtype.get('width',0))
                extraData['height'] = int(vtype.get('height',0) )
                extraData['duration'] = duration
            elif stream == 2:
                #audio
                extraData['AudioCodec'] = vtype.get('codec')
                extraData['AudioLanguage'] = vtype.get('language')
                extraData['AudioChannels'] = int(vtype.get('channels'))
            elif stream == 3:
                #subtitle
                try:
                    language = vtype.get('language')
                except:
                    pass
            else:
                #error
                 xbmcgui.Dialog().ok('Error',str("Something went wrong!"))

        #Determine what tupe of watched flag [overlay] to use
        if int(atype.get('viewCount',0)) > 0:
            details['playcount'] = 1
        else: 
            details['playcount'] = 0

        #Another Metadata
        details['cast']     = tempcast
        details['director'] = " / ".join(tempdir)
        details['writer']   = " / ".join(tempwriter)
        details['genre']    = " / ".join(tempgenre)

        context=None

        url=atype.get('key')

        u=sys.argv[0]+"?url=" + url+"&mode="+str(1) +"&file=" + atype.find('Media').find('Part').get('key')

        addGUIItem(u, details, extraData, context, folder=False)

    xbmcplugin.endOfDirectory(handle)

def buildSearch(url):
    try:
        term=util.searchBox()
        toSend = { 'url' : url+term }    
        buildTVShows(toSend)
    except:
        pass

#Other functions
def playVideo(url):
    item = xbmcgui.ListItem(path=url)
    return xbmcplugin.setResolvedUrl(handle, True, item)

def voteSeries(params):
    vote_list = [ 'Don\'t Vote', '10', '9', '8', '7', '6', '5', '4', '3', '2', '1' ,'0']
    myVote = xbmcgui.Dialog().select('myVote', vote_list)
    myLen = len("http://" + addon.getSetting("ipaddress") + ":" + addon.getSetting("port") + addon.getSetting("userid"))
    if myVote != 0:
        vote_value=str(vote_list[myVote])
        vote_type = str(1)
        series_id=params['anime_id'][(myLen+30):]
        getHtml("http://" + addon.getSetting("ipaddress") + ":" + addon.getSetting("port") + "/jmmserverkodi/vote/" + addon.getSetting("userid") + "/" + series_id + "/" +vote_value + "/" + vote_type, "")
        xbmc.executebuiltin("XBMC.Notification(%s, %s %s, 7500, %s)" % ('Vote saved', 'You voted', vote_value , addon.getAddonInfo('icon')))

def watchedMark(params):
    myLen = len("http://" + addon.getSetting("ipaddress") + ":" + addon.getSetting("port") + addon.getSetting("userid"))
    episode_id=params['ep_id']
    watched=bool(params['watched'])
    watched_msg = ""
    if watched is True:
        watched_msg = "watched"
    else:
        watched_msg = "unwatched"
    xbmc.executebuiltin('XBMC.Action(ToggleWatched)',True)
    getHtml("http://" + addon.getSetting("ipaddress") + ":" + addon.getSetting("port") + "/jmmserverkodi/watch/" + addon.getSetting("userid")+ "/" +episode_id + "/" + str(watched),"")
    xbmc.executebuiltin("XBMC.Notification(%s, %s %s, 7500, %s)" % ('Watched status changed', 'Mark as ', watched_msg , addon.getAddonInfo('icon')))

#Script run here
try:
    parameters=util.parseParameters()
    #xbmcgui.Dialog().ok('DEBUG',str(parameters))
except:
    xbmcgui.Dialog().ok('Forced mode=2','ERROR - This should be fixd')
    parameters = {"mode":2}
try:
    mode=int(parameters["mode"])
except:
    mode=None
try:
    cmd=parameters['cmd']
except:
    cmd=None

#xbmcgui.Dialog().ok("CMD", cmd)
#xbmcgui.Dialog().ok("PARAMETERS", str(parameters))
if cmd != None:
    if cmd == "vote":
        voteSeries(parameters)
    elif cmd == "watched":
        parameters['watched']=True
        watchedMark(parameters)
    elif cmd == "unwatched":
        parameters['watched']=False
        watchedMark(parameters)

if mode==1: #VIDEO
    playVideo(parameters['file'])
elif mode==2: #DIRECTORY
    xbmcgui.Dialog().ok('MODE=2','BAD MODE')
elif mode==3: #SEARCH
    buildSearch(parameters['url'])
elif mode==4: #TVShows
    buildTVShows(parameters)
elif mode==5: #TVSeasons
    buildTVSeasons(parameters)
elif mode==6: #TVEpisodes
    buildTVEpisodes(parameters)
else:
    buildMainMenu()
