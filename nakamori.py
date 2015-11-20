import urllib2, re, urllib, json, sys, os.path, time, base64
import xml.etree.ElementTree
import xbmcaddon, xbmcplugin, xbmcgui, xbmc
import resources.lib.util as util


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


def decodeHex(url):
    return url.replace("/video/jmm/proxy/","").decode("hex")


def encodeHex(url):
    return "/video/jmm/proxy/" + url.encode("hex")

    
def buildMainMenu():
    params2=""
    www="http://" + addon.getSetting("ipaddress") + ":" + addon.getSetting("port") + "/jmmserverkodi/getfilters/" + addon.getSetting("userid")
    e=xml.etree.ElementTree.XML(getHtml(www,params2))
    for atype in e.findall('Directory'):
        a1=atype.get('title')
        a2=atype.get('key')
        a3=2
        a4=atype.get('thumb')
        a5="1"
        a6="1"
        a7="1"
        util.addDir(a1,a2,a3,a4,a5,a6,a7)
    util.addDir("Search", "http://" + addon.getSetting("ipaddress") + ":" + addon.getSetting("port") + "/jmmserverkodi/search/" + addon.getSetting("userid") + "/"+ addon.getSetting("maxlimit") +"/", 3, "1","2","3","4")
    xbmcplugin.endOfDirectory(int(sysarg))


def buildSubMenu(params):
    params2="";
    if "jmmserverplex" in params['url'].lower():
        params['url'] = params['url']
    www = params['url']
    e=xml.etree.ElementTree.XML(getHtml(www,params2))
    for atype in e.findall('Directory'):
        a1=atype.get('title')
        a2=atype.get('key')
        a3=2
        try:
            a4=atype.get('thumb')
        except:
            a4="none"
        try:
            a5=atype.get('summary')
        except:
            a5="none"
        a6="none"
        a7="none"
        util.addDir(a1,a2,a3,a4,a5,a6,a7)
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
        duration=atype.find('Media').get('duration')
        premiered = atype.get('originallyAvailableAt')
        #TODO
        season="1"
        rating="9.0"
        playcount="0"
        mpaa="R"
        plotoutline="short plot"
        studio="Ghilbi"
        tagline="??"
        writer=""
        tvshowtitle=""
        status = "Airing"
        aired = "2008-12-07"
        lastplayed = "2009-04-05 23:16:04"
        votes = "666 votes"
        dateadded = "2009-04-05 23:16:04"
        #Extended support END#
        u=sys.argv[0]+"?url=" + a2+"&play="+str(4)+"&name="+urllib.quote_plus(title.encode("utf-8"))+ "&thumb="+a4 +"&poster="+a7
        liz=xbmcgui.ListItem(a1.encode("utf-8"), iconImage=a4, thumbnailImage=a4)
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
        'Studio':studio,
        'Tagline': tagline,
        'Writer': writer,
        'Tvshowtitle': tvshowtitle,
        'Premiered': premiered,
        'Status': status,
        #code : string (tt0110293, - IMDb code
        'Aired': aired,
        #credits : string (Andy Kaufman, - writing credits
        'Lastplayed': lastplayed,
        #album : string (The Joshua Tree,
        #artist : list (['U2'],
        'Votes': votes,
        #trailer : string (/home/user/trailer.avi,
        'Dateadded': dateadded
		})
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
                xbmcgui.Dialog().ok('Error',str(Error))
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    xbmcplugin.endOfDirectory(int(sysarg))

        
def search(url):
    term=util.searchBox()
    toSend = { 'url' : url+term }    
    buildSubMenu(toSend)
    

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
