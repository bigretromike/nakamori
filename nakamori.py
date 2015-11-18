import urllib2, re, urllib, json, sys, os.path, time, base64
import xml.etree.ElementTree
import xbmcaddon, xbmcplugin, xbmcgui, xbmc
import resources.lib.util as util
		
USER_AGENT = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'

hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

headers = {'User-Agent': USER_AGENT,
           'Accept': '*/*',
           'Connection': 'keep-alive'}

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
		
			
def buildMainMenu():
	params2=""
	www="http://" + addon.getSetting("ipaddress") + ":" + addon.getSetting("port") + "/jmmserverplex/getfilters/1"
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
	xbmcplugin.endOfDirectory(int(sysarg))


def buildSubMenu(params):
	params2="";
	www = decodeHex(params['url'])
	e=xml.etree.ElementTree.XML(getHtml(www,params2))
	for atype in e.findall('Directory'):
		a1=atype.get('title')
		a2=atype.get('key')
		a3=2
		a4=atype.get('thumb')
		a5="1"
		a6="1"
		#a6=atype.get('art') gives None
		a7="1"
		util.addDir(a1,a2,a3,a4,a5,a6,a7)
		#u=a2+"&mode="+str(a3)
		#xbmcgui.Dialog().ok('URL',u)
		#liz=xbmcgui.ListItem(a1.encode("utf-8"), iconImage=a4, thumbnailImage=a4)
		#liz.setInfo( type="Video", infoLabels={ "Title": a1.encode("utf-8"),"Plot": a5} )
		#liz.setProperty("Fanart_Image", video[7])
		#liz.setProperty("Landscape_Image", video[7])
		#liz.setProperty("Poster_Image", video[6])
		#ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
	for atype in e.findall('Video'):
		a1=atype.get('title')
		a2=atype.get('key')
		a3=3
		try:
			a4=atype.get('thumb')
		except:
			a4="4"
		try:
			a5=atype.get('summary')
		except:
			a5="5"
		try:
			a6=atype.get('art')
		except:
			a6="6"
		a7="1"
		#util.addDir(a1,a2,a3,a4,a5,a6,a7)
		u=sys.argv[0]+"?url=" + a2+"&play="+str(4)+"&name="+urllib.quote_plus(a1.encode("utf-8"))+ "&thumb="+a4 #+"&poster="+video[6]
		#xbmcgui.Dialog().ok('URL ',str(a2)[120:])
		#xbmcgui.Dialog().ok('URL',u.replace("/video/jmm/proxy/","")[100:])
		liz=xbmcgui.ListItem(a1.encode("utf-8"), iconImage=a4, thumbnailImage=a4)
		liz.setInfo( type="Video", infoLabels={ "Title": a1.encode("utf-8"),"Plot": a5} )
         #liz.setProperty("Fanart_Image", video[7])
         #liz.setProperty("Landscape_Image", video[7])
         #liz.setProperty("Poster_Image", video[6])
		ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
	xbmcplugin.endOfDirectory(int(sysarg))

        
def search(urls):
    toSend=[]
    term=util.searchBox()
    for url in urls:
        xbmc.log(url+term, xbmc.LOGERROR)
        toSend.append(url+term)
    getVids(toSend)
	

def getLink(url):
	www = decodeHex(url)
	params2 = ""
	link = ""
	e=xml.etree.ElementTree.XML(getHtml(www,params2))
	for atype in e.iter('Part'):
		link = atype.get('key')
	return link


def getTitle(url):
	www = decodeHex(url)
	params2 = ""
	link = ""
	e=xml.etree.ElementTree.XML(getHtml(www,params2))
	for atype in e.findall('Video'):
		link=atype.get('title')
	return link

	
def getThumb(url):
	www = decodeHex(url)
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
	xbmcgui.Dialog().ok('link2',str(link))
	xbmcgui.Dialog().ok('thumb',str(thumb))
	xbmcgui.Dialog().ok('title',str(title))
	util.playMedia(title, thumb, link, "Video")


def getHtml(url, referer, hdr=None):
    referer=urllib2.quote(referer).replace("%3A", ":")
    if not hdr:
        req = Request(url, '', headers)
    else:
        req = Request(url, '', hdr)
    if len(referer) > 1:
        req.add_header('Referer', referer)
    response = urlopen(req, timeout=60)
    data = response.read()
    response.close()
    return data


try:        
	parameters=util.parseParameters()
except:
	parameters = {"mode":2}

try:
    mode=int(parameters["mode"])
except:
    mode=None

if mode==1: #VIDEO
	playVideo(parameters)
elif mode==2: #DIRECTORY
	buildSubMenu(parameters)
elif mode==3: #SEARCH
	search(parameters['url'].split('<split>'))
elif 'play' in parameters:
	playVideo(parameters)
else:
	buildMainMenu()