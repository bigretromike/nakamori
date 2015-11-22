import urllib2, re, urllib, json, sys, os.path, time, base64, datetime
import xml.etree.ElementTree
import xbmcaddon, xbmcplugin, xbmcgui
import resources.lib.util as util

handle = int(sys.argv[1])
xbmcplugin.setContent(handle, 'TVShows')

sysarg=str(sys.argv[1])
ADDON_ID='plugin.video.nakamoriplugin'
addon = xbmcaddon.Addon(id=ADDON_ID)

rootDir = addon.getAddonInfo('path')
if rootDir[-1] == ';':
    rootDir = rootDir[0:-1]
rootDir = xbmc.translatePath(rootDir)
resDir = os.path.join(rootDir, 'resources')
imgDir = os.path.join(resDir, 'images')

urlopen = urllib2.urlopen
Request = urllib2.Request
opener = urllib2.build_opener()
urllib2.install_opener(opener)

def toInt(val):
     if val is None:
          val = 0;
     return int(val)

def buildMainMenu():
    e=xml.etree.ElementTree.XML(getHtml("http://" + addon.getSetting("ipaddress") + ":" + addon.getSetting("port") + "/jmmserverkodi/getfilters/" + addon.getSetting("userid"),""))
    for atype in e.findall('Directory'):
        rating=9.0
        label2="la2"
        title=atype.get('title')
        url=atype.get('key')
        thumb=atype.get('thumb')
        u=sys.argv[0]+"?url="+url+"&mode="+str(2)+"&name="+urllib.quote_plus(title)
        ok=True
        #ListItem([label, label2, iconImage, thumbnailImage, path])
        liz=xbmcgui.ListItem(label=title, label2="666", iconImage="DefaultVideo.png",  thumbnailImage=thumb, path=url)
        #liz.setInfo( type="Video", infoLabels={ "Title": title, 'Rating': rating ,'episode': 3, 'playcount': 1 , 'watched': True, 'votes': 100} )
        liz.setInfo( type="Video", infoLabels={ "Title": title, 'Rating': rating} )
        liz.setProperty("Poster_Image", thumb)
        #liz.setProperty("Label2", label2)
        #liz.setProperty("Episode", str(1))
        #liz.setLabel2(str(1))
        xbmcplugin.addDirectoryItem(handle,url=u,listitem=liz,isFolder=True, totalItems=5)
    util.addDir("Search", "http://" + addon.getSetting("ipaddress") + ":" + addon.getSetting("port") + "/jmmserverkodi/search/" + addon.getSetting("userid") + "/"+ addon.getSetting("maxlimit") +"/", 3, "1","2","3","4")
    xbmcplugin.endOfDirectory(handle)

def buildSubMenu(params):
    e=xml.etree.ElementTree.XML(getHtml(params['url'],''))
    #whenever there is series/movie its shown as <Directory>
    for atype in e.findall('Directory'):
        url=atype.get('key')
        thumb=atype.get('thumb')
        #Extended support
        #count
        #size
        #date
        try:
            genre=atype.find('Tag').get('tag')
        except:
            genere="none"
        year=toInt(atype.get('year'))
        episode=toInt(atype.get('leafCount'))
        season=toInt(atype.get('season'))
        #top250=toInt()
        #tracknumber=toInt()
        rating=atype.get('rating')
        playcount=toInt(atype.get('viewedLeafCount'))
        #overlay : integer (2, - range is 0..8. See GUIListItem.h for values
        #cast
        #castandrole
        #director
        mpaa=atype.get('contentRating')
        plot=atype.get('summary')
        plotoutline=plot
        title=atype.get('title')
        originaltitle=atype.get('original_title')
        sorttitle=title.encode("utf-8")
        #duration=str(datetime.timedelta(minutes=((int(atype.find('Media').get('duration')))/60000)))[:-3]
        #studio="Ghilbi"
        #tagline="??"
        #writer=""
        #tvshowtitle=""
        premiered = atype.get('originallyAvailableAt')
        status = "Airing"
        #code = ""
        aired = "2008-12-07"
        #credits
        lastplayed = "2009-04-05 23:16:04"
        #album
        #artist
        votes = atype.get('votes')
        #trailer
        dateadded = atype.get('addedAt')
        #Extended support END#
        u=sys.argv[0]+"?url="+url+"&mode="+str(2)+"&name="+urllib.quote_plus(title)+"&poster_file="+urllib.quote_plus(thumb)+"&filename="+urllib.quote_plus("none")
        liz=xbmcgui.ListItem(title, iconImage="DefaultVideo.png", thumbnailImage=thumb)
        liz.setInfo( type="Video" , infoLabels={
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
        #'Duration': duration,
        #'Studio':studio,
        #'Tagline': tagline,
        #'Writer': writer,
        #'Tvshowtitle': tvshowtitle,
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
        #Let's set some arts
        #liz.setArt({ 'thumb': thumb, 'poster': poster, 'banner' : banner, 'fanart': fanart, 'clearart': clearart, 'clearlogo': clearlogo, 'landscape': landscape})
        #liz.setProperty("Poster_Image",thumb)
        liz.setProperty('Label2', '10')
        xbmcplugin.addDirectoryItem(handle,url=u,listitem=liz,isFolder=True)
    #whenever there is a <Video> inside <Directory> this will kick in with VideoSpecific values
    for atype in e.findall('Video'):
        a2=atype.get('key')
        a3=3
        try:
            a4=atype.get('thumb')
        except:
            a4="none"
        try:
            plot=atype.get('summary')
        except:
            plot="none"
        a6="none"
        a7="none"
        #Extended support
        try:
            genre=atype.find('Tag').get('tag')
        except:
            genre=""
        try:
            year=atype.get('year')
        except:
            year=""
        try:
            episode=atype.get('index')
        except:
            episode="0"
        title=atype.get('title')
        originaltitle=atype.get('original_title')
        sorttitle=title.encode("utf-8")
        duration=str(datetime.timedelta(minutes=((int(atype.find('Media').get('duration')))/60000)))[:-3]
        premiered = atype.get('originallyAvailableAt')
        rating=atype.get('rating')
        votes = atype.get('votes')
        season=atype.get('season')
        mpaa=atype.get('contentRating')
        plotoutline=plot
        dateadded = atype.get('addedAt')
        #TODO
        playcount="0"
        #NOT IMPLEMENTED IN Contract_AniDBAnime
        studio="Ghilbi"
        tagline="??"
        writer=""
        tvshowtitle=""
        status = "Airing"
        aired = "2008-12-07"
        lastplayed = "2009-04-05 23:16:04"
        #Extended support END#
        u=sys.argv[0]+"?url=" + a2+"&play="+str(4)+"&name="+urllib.quote_plus(title.encode("utf-8"))+ "&thumb="+a4 +"&poster="+a7+"&filename="+urllib.quote_plus(atype.find('Media').find('Part').get('file'))
        liz=xbmcgui.ListItem(title.encode("utf-8"), iconImage=a4, thumbnailImage=a4)
        liz.setInfo( type="Video" , infoLabels={
        "Title": title.encode("utf-8") , 
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
        #'Tvshowtitle': tvshowtitle,
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
                    language = ""
            else:
                #error
                xbmcgui.Dialog().ok('Error',str("Something went wrong!"))
        xbmcplugin.addDirectoryItem(handle,url=u,listitem=liz,isFolder=False)
    xbmcplugin.endOfDirectory(int(sysarg))

        
def search(url):
    try:
        term=util.searchBox()
        toSend = { 'url' : url+term }    
        buildSubMenu(toSend)
    except:
        pass
    

def getLink(url):
    www = url
    params2 = ""
    link = ""
    e=xml.etree.ElementTree.XML(getHtml(www,params2))
    for atype in e.iter('Part'):
        link = atype.get('key')
    return link


def getTitle(url):
    www = url
    params2 = ""
    link = ""
    e=xml.etree.ElementTree.XML(getHtml(www,params2))
    for atype in e.findall('Video'):
        link=atype.get('title')
    return link

    
def getThumb(url):
    www = url
    params2 = ""
    link = ""
    e=xml.etree.ElementTree.XML(getHtml(www,params2))
    for atype in e.findall('Video'):
        link=atype.get('thumb')
    return link
        
    
def playVideo(params):
    link = getLink(params['url'])
    thumb = getThumb(params['url'])
    title = getTitle(params['url'])
    #xbmcgui.Dialog().ok('MODE=link',str(link))
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
    buildSubMenu(parameters)
elif mode==3: #SEARCH
    #xbmcgui.Dialog().ok('MODE=3',str(parameters))
    search(parameters['url'])
elif 'play' in parameters:
    #xbmcgui.Dialog().ok('MODE=play',str(parameters))
    playVideo(parameters)
else:
    buildMainMenu()
