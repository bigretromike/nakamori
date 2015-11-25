import urllib2, re, urllib, json, sys, os.path, time, base64, datetime
import xml.etree.ElementTree as tree
import xbmcaddon, xbmcplugin, xbmcgui
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


def buildSeriesMenu(params):
    xbmcplugin.setContent(handle, content='tvshows')
    e=tree.XML(getHtml(params['url'],''))
    for atype in e.findall('Directory'):
        url=atype.get('key')
        thumb=atype.get('thumb')
        #Extended support
        count=2
        size=3
        #date #of file
        try:
            genre=atype.find('Tag').get('tag')
        except:
            genre="none"
        year=toInt(atype.get('year'))
        episode=toInt(atype.get('leafCount'))
        season=toInt(atype.get('season'))
        #top250=toInt()
        #tracknumber=toInt()
        rating=atype.get('rating')
        playcount=toInt(atype.get('viewedLeafCount'))
        #overlay : integer (2, - range is 0..8. See GUIListItem.h for values
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
        #xbmcgui.Dialog().ok('CAST',str(cast))
        #castandrole <---- AniDB
        #director <---- AniDB
        mpaa=atype.get('contentRating')
        plot=atype.get('summary')
        plotoutline=plot
        title=atype.get('title')
        try:
            originaltitle=atype.get('original_title').encode("utf-8")
        except:
            originaltitle=title
        sorttitle=title.encode("utf-8")
        #duration 
        #studio <---- AniDB
        #tagline="??"
        #writer <---- AniDB
        tvshowtitle=title
        premiered = atype.get('originallyAvailableAt')
        #status = "Airing"
        #code
        #aired = "2008-12-07"
        #credits
        #lastplayed = "2009-04-05 23:16:04"
        #album
        #artist
        votes = atype.get('votes')
        #trailer
        dateadded = atype.get('addedAt')
        #Extended support END#
        u=sys.argv[0]+"?url="+url+"&mode="+str(2)+"&name="+urllib.quote_plus(title)+"&poster_file="+urllib.quote_plus(thumb)+"&filename="+urllib.quote_plus("none")
        liz=xbmcgui.ListItem(title, iconImage="DefaultVideo.png", thumbnailImage=thumb)

        #liz.setProperty('TotalEpisodes', str(10))
        #liz.setProperty('WatchedEpisodes', str(5))
        #liz.setProperty('UnWatchedEpisodes', str(5))
        #Hack to show partial flag for TV shows and seasons
        #liz.setProperty('TotalTime', '100')
        #liz.setProperty('ResumeTime', '50')

        liz.setInfo( type="Video", infoLabels={
        'Count': count,
        'Size': size,
        #'Date': date, 
        'Title': title.encode("utf-8"), 
        'Genre': genre,
        'Year': year,
        'Episode': episode,
        'Season': season,
        #top250 : integer (192,
        #tracknumber : integer (3,
        'Rating': rating,
        'Playcount': playcount,
        #overlay : integer (2, - range is 0..8. See GUIListItem.h for values
        'Cast': cast, #cast : list (Michal C. Hall,
        #castandrole : list (Michael C. Hall|Dexter,
        #director : string (Dagur Kari,
        'Mpaa': mpaa,
        'Plot': plot,
        'Plotoutline': plotoutline,
        'Originaltitle': originaltitle,
        'Sorttitle': sorttitle,
        #'Duration': duration,
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
        })
        liz.setProperty('IsPlayable', 'False')
        #Let's set some arts
        #liz.setArt({ 'thumb': thumb, 'poster': poster, 'banner' : banner, 'fanart': fanart, 'clearart': clearart, 'clearlogo': clearlogo, 'landscape': landscape})
        #liz.setProperty('TotalSeasons','2')
        #liz.setProperty('TotalEpisodes','2')
        #liz.setProperty('WatchedEpisodes','1')
        #liz.setProperty('UnWatchedEpisodes','1')
        #liz.setProperty('NumEpisodes','2')
        #liz.setProperty('TVShows.Count','3')
        xbmcplugin.addDirectoryItem(handle,url=u,listitem=liz,isFolder=True)
        #xbmcgui.Dialog().ok('PARRRA',str(liz.getProperty('NumEpisodes')))
    xbmcplugin.endOfDirectory(handle)


def buildEpisodesMenu(params):
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
        liz=xbmcgui.ListItem(str(episode) + ". " + title, iconImage="DefaultVideo.png", thumbnailImage=thumb)
        liz.setInfo( type="Video" , infoLabels={
        #'Count': count,
        'Size': size,
        #'Date': date, 
        'Title': title.encode("utf-8") , 
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
        })
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
                liz.addStreamInfo('video', { 'Codec': codec, 'Aspect' : aspect, 'Width': width, 'Height': height, 'Duration': duration })
            elif stream == 2:
                #audio
                codec = vtype.get('codec')
                language = vtype.get('language')
                channels = int(vtype.get('channels'))
                liz.addStreamInfo('audio', { 'Codec': codec, 'Language': language, 'Channels': channels })
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
        xbmcplugin.addDirectoryItem(handle,url=u,listitem=liz,isFolder=False)
    xbmcplugin.endOfDirectory(handle)
    xbmcplugin.setContent(handle, content='episodes')


def openMenu(params):
    e=tree.XML(getHtml(params['url'],''))
    if e.find('Directory') is not None:
        buildSeriesMenu(params)
    elif e.find('Video') is not None:
        buildEpisodesMenu(params)
    else:
        buildSeriesMenu(params)


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
