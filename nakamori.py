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
	www="http://" + addon.getSetting("ipaddress") + ":" + addon.getSetting("port") + "/jmmserverplex/getfilters/" + addon.getSetting("userid")
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
	util.addDir("Search", "http://" + addon.getSetting("ipaddress") + ":" + addon.getSetting("port") + "/jmmserverplex/search/" + addon.getSetting("userid") + "/"+ addon.getSetting("maxlimit") +"/", 3, "1","2","3","4")
	xbmcplugin.endOfDirectory(int(sysarg))


def buildSubMenu(params):
	params2="";
	if "jmmserverplex" in params['url'].lower():
		params['url'] = encodeHex(params['url']) 
	www = decodeHex(params['url'])
	e=xml.etree.ElementTree.XML(getHtml(www,params2))
	for atype in e.findall('Directory'):
		a1=atype.get('title')
		a2=decodeHex(atype.get('key'))
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
		a1=atype.get('title')
		a2=atype.get('key')
		a3=3
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
		u=sys.argv[0]+"?url=" + a2+"&play="+str(4)+"&name="+urllib.quote_plus(a1.encode("utf-8"))+ "&thumb="+a4 +"&poster="+a7
		liz=xbmcgui.ListItem(a1.encode("utf-8"), iconImage=a4, thumbnailImage=a4)
		liz.setInfo( type="Video", infoLabels={ "Title": a1.encode("utf-8"),"Plot": a5} )
         #liz.setProperty("Fanart_Image", video[7])
         #liz.setProperty("Landscape_Image", video[7])
         #liz.setProperty("Poster_Image", video[6])
		ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
	xbmcplugin.endOfDirectory(int(sysarg))

        
def search(url):
	term=util.searchBox()
	toSend = { 'url' : encodeHex(url+term) }	
	buildSubMenu(toSend)
	

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
	playVideo(parameters)
elif mode==2: #DIRECTORY
	#xbmcgui.Dialog().ok('MODE=2',str(parameters))
	buildSubMenu(parameters)
elif mode==3: #SEARCH
	#xbmcgui.Dialog().ok('MODE=3',str(parameters))
	search(parameters['url'])
elif 'play' in parameters:
	playVideo(parameters)
else:
	buildMainMenu()