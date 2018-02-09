import string
import json
import urllib2

NAME   = 'KIJK'
ICON   = 'icon-default.png'
ART    = 'art-default.jpg'
PREFIX = '/video/kijk'

CHANNELS = [
	{
		'name': 'Net5',
		'slug': 'net5',
	},
	{
		'name': 'SBS6',
		'slug': 'sbs6'
	},
	{
		'name': 'Veronica',
		'slug': 'veronicatv'
	},
	{
		'name': 'SBS9',
		'slug': 'sbs9'
	}
]

AZUPPER = string.ascii_uppercase
AZ_LOWER = string.ascii_lowercase
DIGS = string.digits
API_URL_V1 = 'https://api.kijk.nl/v1/'
API_URL_V2 = 'https://api.kijk.nl/v2/'

RE_SERIES = 'http://kijk.nl/(.*?)/(.*?)'
VIDEO_URL = "https://edge.api.brightcove.com/playback/v1/accounts/585049245001/videos/"

####################################################################################################
def Start():

	ObjectContainer.title1 = NAME
	ObjectContainer.art = R(ART)

	DirectoryObject.thumb = R(ICON)

	Plugin.AddViewGroup("Programs", viewMode="InfoList", mediaType="items")

	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36'

####################################################################################################
@handler(PREFIX, NAME, thumb=ICON, art=ART)
def MainMenu():

	oc = ObjectContainer()

	# oc.add(DirectoryObject(
	# 		title = 'Gemist',
	# 		thumb = R(ICON),
	# 		key = Callback(gemist)
	# ))
	# oc.add(DirectoryObject(
	# 		title = 'Meest Bekeken',
	# 		thumb = R(ICON),
	# 		key = Callback(meestBekeken)
	# ))
	oc.add(DirectoryObject(
			title = 'Programmalijst',
			thumb = R(ICON),
			key = Callback(ProgramsList, title2='Programmalijst')
	))

	return oc

####################################################################################################
@route(PREFIX + '/programsList')
def ProgramsList(title2=''):

	oc = ObjectContainer(title2='Programmalijst')

	jsonObj = getFromAPI(path='default/sections/programs-abc-'+DIGS+AZ_LOWER+'?limit=999&offset=0');
	elements = jsonObj["items"]

	for e in elements:
		if e["available"]:
			title = e["title"]

			try: thumb = Resource.ContentsOfURLWithFallback(e["images"]["nonretina_image"])
			except: thumb = R(ICON)

			try: art = Resource.ContentsOfURLWithFallback(e["images"]["nonretina_image_pdp_header"])
			except: art = R(ART)

			millis = int(e["duration"].replace(' min.', ''))*60*1000

			oc.add(DirectoryObject(
				title = title,
				thumb = thumb,
				summary = e["synopsis"],
				art = art,
				duration = millis,
				key = Callback(Program, title2=title, path=e["_links"]["self"])
			))

	oc.objects.sort(key = lambda obj: obj.title.lower())
	if len(oc) > 0:
		return oc
	else:
		return ObjectContainer(header="Geen resultaten", message="Er zijn geen programma's gevonden")

####################################################################################################
@route(PREFIX + '/program')
def Program(title2='', path=''):

	oc = ObjectContainer(title2=title2)

	jsonObj = getFromAPI(path=path);
	sections = jsonObj["sections"]
	for s in sections:
		if s["type"] == "horizontal-single":
			elements = s["items"]
			for e in elements:
				try: thumb = Resource.ContentsOfURLWithFallback(e["images"]["nonretina_image"])
				except: thumb = R(ICON)

				try: art = Resource.ContentsOfURLWithFallback(e["images"]["nonretina_image_pdp_header"])
				except: art = R(ART)

				try: newPath = e["brightcoveId"]
				except: newPath = ''

				millis = int(e["duration"].replace(' min.', ''))*60*1000

				oc.add(DirectoryObject(
					title = e["seasonLabelShort"]+"E"+e["episode"]+": "+e["episodeLabel"],
					thumb = thumb,
					summary = e["synopsis"],
					art = art,
					duration = millis,
					key = Callback(Episode, title2=e["episodeLabel"], path=newPath) #e["brightcoveId"]
				))

	oc.objects.sort(key = lambda obj: obj.title.lower())
	if len(oc) > 0:
		return oc
	else:
		return ObjectContainer(header="Geen resultaten", message="Er zijn geen programma's gevonden")

####################################################################################################
@route(PREFIX + '/episode')
def Episode(title2='', path=''):

	oc = ObjectContainer(title2=title2)

	jsonObj = getFromBrightcove(path=path); #https://edge.api.brightcove.com/playback/v1/accounts/585049245001/videos/5574398508001
	sources = jsonObj["sources"]
	# sources.sort(key = lambda obj: obj.avg_bitrate)
	videoUrl = ""
	for s in sources:
		if(s["container"] == "MP4"):
			videoUrl = s["stream_name"]replace("mp4:", '')
			videoUrlBase = 'https://vod-bc-prod-1.sbscdn.nl/'
			if(!videoUrl.startswith(videoUrlBase)) :
				videoUrl = videoUrlBase+videoUrl
		break
	return ObjectContainer(header="Video URL", message=videoUrl)

####################################################################################################
def getFromAPI(path=''):
	#receivedJson = urllib.urlopen(API_URL_V1+path).read()
	#jsonObj = json.loads(receivedJson)
	#return jsonObj
	return JSON.ObjectFromURL(API_URL_V1+path)

####################################################################################################
def getFromBrightcove(path=''):
	req = urllib2.Request(VIDEO_URL+path);
	req.add_header('Accept', "application/json;pk=BCpkADawqM3ve1c3k3HcmzaxBvD8lXCl89K7XEHiKutxZArg2c5RhwJHJANOwPwS_4o7UsC4RhIzXG8Y69mrwKCPlRkIxNgPQVY9qG78SJ1TJop4JoDDcgdsNrg")
	receivedJson = urllib2.urlopen(req).read()
	jsonObj = json.loads(receivedJson)
	return jsonObj
	#return JSON.ObjectFromURL(VIDEO_URL+path)

####################################################################################################
def sortByTitle(t):
	return t["title"]
