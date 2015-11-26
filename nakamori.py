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
xbmcplugin.setContent(handle, 'tvshows')
addon = xbmcaddon.Addon(id='plugin.video.nakamoriplugin')

urlopen = urllib2.urlopen
Request = urllib2.Request

def toInt(val):
     if val is None:
          val = 0;
     return int(val)

def buildMainMenu():
    xbmcplugin.setContent(handle, content='tvshows')
    e=tree.XML(getHtml("http://" + addon.getSetting("ipaddress") + ":" + addon.getSetting("port") + "/jmmserverkodi/getfilters/" + addon.getSetting("userid"),""))
    for atype in e.findall('Directory'):
        title=atype.get('title')
        url=atype.get('key')
        thumb=atype.get('thumb')
        u=sys.argv[0]+"?url="+url+"&mode="+str(2)+"&name="+urllib.quote_plus(title)
        liz=xbmcgui.ListItem(label=title, label2=title, iconImage="DefaultVideo.png",  thumbnailImage=thumb, path=url)
        liz.setInfo( type="Video", infoLabels={ "Title": title } )
        xbmcplugin.addDirectoryItem(handle,url=u,listitem=liz,isFolder=True)
    util.addDir("Search", "http://" + addon.getSetting("ipaddress") + ":" + addon.getSetting("port") + "/jmmserverkodi/search/" + addon.getSetting("userid") + "/"+ addon.getSetting("maxlimit") +"/", 3, "http://" + addon.getSetting("ipaddress") + ":" + addon.getSetting("port") + "/jmmserverkodi/GetSupportImage/plex_others.png","2","3","4")
    xbmcplugin.endOfDirectory(handle)

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

        details={
		#'count': count,
        #'size': size,
        #'Date': date, 
        'title': atype.get('title','Unknown').encode('utf-8') , 
        'genre':  " / ".join(tempgenre),
        'year': toInt(atype.get('year')),
        'episode': toInt(atype.get('leafCount','0')),
        'season': toInt(atype.get('season','0')),  #<------ 0
        #top250 : integer (192,
        #tracknumber : integer (3,
        'rating': atype.get('rating'),
        #'playcount': toInt(atype.get('viewedLeafCount')),
        #overlay : integer (2, - range is 0..8. See GUIListItem.h for values
        #'cast': cast, #cast : list (Michal C. Hall,
        #castandrole : list (Michael C. Hall|Dexter,
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
        
        extraData={ 'mode'      : 2, 
                   'type'              : 'video' ,
                   'source'            : 'tvshows',
                   'UnWatchedEpisodes' : int(details['episode']) - watched,
                   'WatchedEpisodes'   : watched,
                   'TotalEpisodes'     : details['episode'],
                   'thumb'             : atype.get('thumb') ,
                   #'fanart_image'      : atype.get('thumb')  ,
                   'key'               : atype.get('key','') ,
                   #'ratingKey'         : str(show.get('ratingKey',0)) 
                 }

        url=atype.get('key')

        #Set up overlays for watched and unwatched episodes
        if extraData['WatchedEpisodes'] == 0:
            details['playcount'] = 0
        elif extraData['UnWatchedEpisodes'] == 0:
            details['playcount'] = 1
        else:
            extraData['partialTV'] = 1

        #Extended support
        cast = [ ]
        #xbmcgui.Dialog().ok('atype',str(atype.find('Characters')))
        if atype.find('Characters'):
            for char in atype.find('Characters').findall('Character'):
                char_id = char.get('charID')
                char_charname=char.get('charname')
                char_picture=char.get('picture')
                char_desc=char.get('description')
                cast.append(char_charname)
            else:
                cast = [ ]
        #Extended support END#

        u=sys.argv[0]+"?url="+url+"&mode="+str(2)+"&name="+urllib.quote_plus(details['title'])+"&poster_file="+urllib.quote_plus(extraData['thumb'])+"&filename="+urllib.quote_plus("none")
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

def buildTVEpisodes(params):
    xbmcplugin.setContent(handle, 'episodes')
    e=tree.XML(getHtml(params['url'],''))
    setWindowHeading(e)
    #get banner thumb
    banner = e.get('banner','')

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
                 'mpaa'        : atype.get('contentRating','') ,
                 'year'        : toInt(atype.get('year')) ,
                 'tagline'     : atype.get('tagline','').encode('utf-8') ,
                 'episode'     : toInt(atype.get('index',0)),
                 'aired'       : atype.get('originallyAvailableAt','') ,
                 'tvshowtitle' : atype.get('grandparentTitle',atype.get('grandparentTitle','')).encode('utf-8') , #<-----------------------
                 'votes'        : int(atype.get('votes',0)) , 
                 'season'      : int(atype.get('season',0)) }

        #details['title'] = "%s - %sx%s %s" % ( details['tvshowtitle'], details['season'], str(details['episode']).zfill(2), details['title'] )

        #Extra data required to manage other properties
        extraData={'type'         : "Video" ,
                   'source'       : 'tvepisodes',
                   'thumb'        : atype.get('thumb','') ,
                   'fanart_image' : atype.get('fanart','') ,
                   'key'          : atype.get('key',''),
                   #'ratingKey'    : str(episode.get('ratingKey',0)),
                   'duration'     : duration,
                   'resume'       : int(int(view_offset)/1000) }

	    #Information about streams inside video file
        extraData['xVideoResolution'] = int(atype.find('Media').get('videoResolution'),0)
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
                extraData['duration'] = int(vtype.get('duration',0))

            elif stream == 2:
                #audio
                extraData['AudioCodec'] = vtype.get('codec')
                extraData['AudioLanguage'] = vtype.get('language')
                extraData['AudioChannels'] = int(vtype.get('channels'))
                #liz.addStreamInfo('audio', { 'Codec': codec, 'Language': language, 'Channels': channels })
                #liz.setProperty('AudioCodec', codec)
                #liz.setProperty('AudioChannels', str(channels))
            elif stream == 3:
                #subtitle
                try:
                    language = vtype.get('language')
                    #liz.addStreamInfo('subtitle', { 'Language': language })
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

        u=sys.argv[0]+"?url=" + url+"&mode="+str(1)+"&play="+str(1)+"&name="+urllib.quote_plus(details['title'].encode("utf-8")) +"&poster="+season_thumb+"&filename="+urllib.quote_plus(atype.find('Media').find('Part').get('file'))

        addGUIItem(u, details, extraData, context, folder=False)

    xbmcplugin.endOfDirectory(handle)

def addGUIItem(url, details, extraData, context=None, folder=True):

    if extraData.get('parameters'):
        for argument, value in extraData.get('parameters').items():
            link_url = "%s&%s=%s" % (link_url, argument, urllib.quote(value))

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
            if extraData.get('duration') : video_codec['duration'] = int(extraData.get('duration'))

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

    if context is not None:
        if not folder and extraData.get('type','video').lower() == "video":
            #Play Transcoded
            context.insert(0,('Play Transcoded', "XBMC.PlayMedia(%s&transcode=1)" % link_url , ))
        liz.addContextMenuItems( context, settings.get_setting('contextreplace') )

    return xbmcplugin.addDirectoryItem(handle,url,listitem=liz,isFolder=folder)

def buildEpisodesMenu(params):
    xbmcplugin.setContent(handle, content='episodes')
    e=tree.XML(getHtml(params['url'],''))
    for atype in e.findall('Video'):
        url=atype.get('key')
        thumb=atype.get('thumb')
        #Extended support
        #count
        size=toInt(atype.find('Media').find('Part').get('size'))
        #date
        try:
            genre=atype.find('Tag').get('tag')
        except:
            genre="none"
        year=toInt(atype.get('year'))
        episode=toInt(atype.get('index'))
        season=toInt(atype.get('season'))
        #top250=toInt()
        #tracknumber=toInt()
        rating=atype.get('rating')
        playcount=toInt(atype.get('viewCount'))
        #overlay : integer (2, - range is 0..8. See GUIListItem.h for values
        #cast
        #castandrole
        #director
        mpaa=atype.get('contentRating')
        plot=atype.get('summary')
        plotoutline=plot
        title=atype.get('title')
        try:
            originaltitle=atype.get('original_title').encode("utf-8")
        except:
            originaltitle=title
        sorttitle=title.encode("utf-8")
        duration=int(atype.find('Media').get('duration'))/1000
        #xbmcgui.Dialog().ok('Error',str(duration))
        #studio="Ghilbi"
        #tagline="??"
        #writer=""
        tvshowtitle=title
        premiered = atype.get('originallyAvailableAt')
        #status = "Airing"
        #code = ""
        #aired = "2008-12-07"
        #credits
        #lastplayed = "2009-04-05 23:16:04"
        #album
        #artist
        votes = atype.get('votes')
        #trailer
        dateadded = atype.get('addedAt')
        #Extended support END#
        u=sys.argv[0]+"?url=" + url+"&mode="+str(1)+"&play="+str(1)+"&name="+urllib.quote_plus(title.encode("utf-8")) +"&poster="+thumb+"&filename="+urllib.quote_plus(atype.find('Media').find('Part').get('file'))
        liz=xbmcgui.ListItem(str(episode) + ". " + title, thumbnailImage=thumb)
        info ={
        #'Count': count,
        'Size': size,
        #'Date': date, 
        'Title': str(episode) + ". " + title.encode("utf-8") , 
        'Genre': genre,
        'Year': year,
        'Episode': episode,
        'Season': season,
        #top250 : integer (192,
        #tracknumber : integer (3,
        'Rating': rating,
        'Playcount': playcount,
        #overlay : integer (2, - range is 0..8. See GUIListItem.h for values
        #cast : list (Michal C. Hall,
        #castandrole : list (Michael C. Hall|Dexter,
        #director : string (Dagur Kari,
        'Mpaa': mpaa,
        'Plot': plot,
        'Plotoutline': plotoutline,
        'Originaltitle': originaltitle.encode("utf-8"),
        'Sorttitle': sorttitle,
        'Duration': duration,
        #'Studio':studio,
        #'Tagline': tagline,
        #'Writer': writer,
        'Tvshowtitle': tvshowtitle,
        'Premiered': premiered,
        #'Status': status,
        #code : string (tt0110293, - IMDb code
        #'Aired': aired,
        #credits : string (Andy Kaufman, - writing credits
        #'Lastplayed': lastplayed,
        #album : string (The Joshua Tree,
        #artist : list (['U2'],
        'Votes': votes,
        #trailer : string (/home/user/trailer.avi,
        'Dateadded': dateadded
        }
        liz.setInfo( type="Video" , infoLabels=info )
        liz.setProperty('IsPlayable', 'true')
        #Let's set some arts
        #liz.setArt({ 'thumb': thumb, 'poster': poster, 'banner' : banner, 'fanart': fanart, 'clearart': clearart, 'clearlogo': clearlogo, 'landscape': landscape})
        #Information about streams inside video file
        for vtype in atype.find('Media').find('Part').findall('Stream'):
            stream=int(vtype.get('streamType'))
            if stream == 1:
                #video
                codec = vtype.get('codec')
                aspect = float(atype.find('Media').get('aspectRatio'))
                width = int(vtype.get('width'))
                height = int(vtype.get('height')) 
                try:
                     duration = int(vtype.get('duration'))
                except:
                     duration = int(0)
                try:
                     videores = int(atype.find('Media').get('videoResolution'))
                except:
                     videores = 0
                liz.addStreamInfo('video', { 'Codec': codec, 'Aspect' : aspect, 'Width': width, 'Height': height, 'Duration': duration })
                liz.setProperty('VideoResolution', str(videores))
                liz.setProperty('VideoCodec', codec)
                liz.setProperty('VideoAspect', str(aspect))
            elif stream == 2:
                #audio
                codec = vtype.get('codec')
                language = vtype.get('language')
                channels = int(vtype.get('channels'))
                liz.addStreamInfo('audio', { 'Codec': codec, 'Language': language, 'Channels': channels })
                liz.setProperty('AudioCodec', codec)
                liz.setProperty('AudioChannels', str(channels))
            elif stream == 3:
                #subtitle
                try:
                    language = vtype.get('language')
                    liz.addStreamInfo('subtitle', { 'Language': language })
                except:
                    pass
            else:
                #error
                xbmcgui.Dialog().ok('Error',str("Something went wrong!"))
        #Adding information about count of episodes
        #liz.setProperty('TotalEpisodes', str())
        #liz.setProperty('WatchedEpisodes', str())
        #liz.setProperty('UnWatchedEpisodes', str())
        #Hack to show partial flag for TV shows and seasons
        #if extraData.get('partialTV') == 1:            
        #    liz.setProperty('TotalTime', '100')
        #    liz.setProperty('ResumeTime', '50')
        #liz.setProperty('fanart_image', '')
        #liz.setProperty('banner', '')
        #liz.setProperty('seasonThumb', ''))
        xbmcplugin.addSortMethod(handle, 37 ) #maintain original plex sorted
        xbmcplugin.addSortMethod(handle, 25 ) #video title ignore THE
        xbmcplugin.addSortMethod(handle, 19 )  #date added
        xbmcplugin.addSortMethod(handle, 3 )  #date
        xbmcplugin.addSortMethod(handle, 18 ) #rating
        xbmcplugin.addSortMethod(handle, 17 ) #year
        xbmcplugin.addSortMethod(handle, 29 ) #runtime
        xbmcplugin.addSortMethod(handle, 28 ) #by MPAA
        xbmcplugin.addDirectoryItem(handle,url=u,listitem=liz,isFolder=False)
    xbmcplugin.endOfDirectory(handle)

def openMenu(params):
    e=tree.XML(getHtml(params['url'],''))
    if e.find('Directory') is not None:
        buildTVShows(params)
    elif e.find('Video') is not None:
        #buildEpisodesMenu(params)
        buildTVEpisodes(params)
    else:
        buildTVShows(params)

def search(url):
    try:
        term=util.searchBox()
        toSend = { 'url' : url+term }    
        openMenu(toSend)
    except:
        pass

def playVideo(params):
    e=tree.XML(getHtml(params['url'],""))
    title = e.find('Video').get('title')
    thumb= e.find('Video').get('thumb')
    link = e.find('Video').find('Media').find('Part').get('key')
    util.playMedia(title, thumb, link, "Video")

def getHtml(url, referer):
    referer=urllib2.quote(referer).replace("%3A", ":")
    req = Request(url)
    if len(referer) > 1:
        req.add_header('Referer', referer)
    response = urlopen(req, timeout=60)
    data = response.read()
    response.close()
    return data

try:
    #if there is a parameter without value it will faile here.
    parameters=util.parseParameters()
except:
    parameters = {"mode":2}
try:
    mode=int(parameters["mode"])
except:
    mode=None

if mode==1: #VIDEO
    #xbmcgui.Dialog().ok('MODE=1',str(parameters))
    playVideo(parameters)
elif mode==2: #DIRECTORY
    #xbmcgui.Dialog().ok('MODE=2',str(parameters))
     openMenu(parameters)
elif mode==3: #SEARCH
    #xbmcgui.Dialog().ok('MODE=3',str(parameters))
    search(parameters['url'])
elif 'play' in parameters:
    #xbmcgui.Dialog().ok('MODE=play',str(parameters))
    playVideo(parameters)
else:
    buildMainMenu()
