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

AZ_UPPER = string.ascii_uppercase
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

	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36'

####################################################################################################
@handler(PREFIX, NAME, thumb=ICON, art=ART)
def MainMenu():

	oc = ObjectContainer()

	oc.add(DirectoryObject(
			title = 'Gemist',
			thumb = R(ICON),
			key = ''
	))
	oc.add(DirectoryObject(
			title = 'Meest Bekeken',
			thumb = R(ICON),
			key = ''
	))
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

	try:
		jsonObj = getFromAPI(path='default/sections/programs-abc-'+DIGS+AZ_LOWER+'?limit=999&offset=0')
		elements = jsonObj["items"]
	except:
		return ObjectContainer(header="Fout", message="Er is iets fout gegaan bij het ophalen van de programmalijst.")

	for e in elements:
		if e["available"]:
			try: title = e["title"]
			except: title = ''

			try: summary = e["synopsis"]
			except: summary = ''

			try: thumb = Resource.ContentsOfURLWithFallback(e["images"]["nonretina_image"])
			except: thumb = R(ICON)

			try: art = Resource.ContentsOfURLWithFallback(e["images"]["nonretina_image_pdp_header"])
			except: art = R(ART)

			try: millis = int(e["duration"].replace(' min.', ''))*60*1000
			except: millis = 0

			oc.add(DirectoryObject(
				title = title,
				thumb = thumb,
				summary = summary,
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

	try:
		jsonObj = getFromAPI(path=path)
		sections = jsonObj["sections"]
	except:
		return ObjectContainer(header="Fout", message="Er is iets fout gegaan bij het ophalen van dit programma.")

	for s in sections:
		if s["type"] == "horizontal-single":
			elements = s["items"]
			for e in elements:
				try: newPath = e["brightcoveId"]
				except: continue

				try: seasonLabelShort = e["seasonLabelShort"]
				except: seasonLabelShort = ''

				try: episode = e["episode"]
				except: episode = ''

				try: episodeLabel = e["episodeLabel"]
				except: episodeLabel = ''

				try: summary = e["synopsis"]
				except: summary = ''

				try: thumb = Resource.ContentsOfURLWithFallback(e["images"]["nonretina_image"])
				except: thumb = R(ICON)

				try: art = Resource.ContentsOfURLWithFallback(e["images"]["nonretina_image_pdp_header"])
				except: art = R(ART)

				try: millis = int(e["duration"].replace(' min.', ''))*60*1000
				except: millis = 0

				millis = int(e["duration"].replace(' min.', ''))*60*1000

				oc.add(DirectoryObject(
					title = seasonLabelShort+"E"+episode+": "+episodeLabel,
					thumb = thumb,
					summary = summary,
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

	try:
		jsonObj = getFromBrightcove(path=path) #https://edge.api.brightcove.com/playback/v1/accounts/585049245001/videos/5574398508001
		sources = jsonObj["sources"]
	except:
		return ObjectContainer(header="Fout", message="Er is iets fout gegaan bij het ophalen van deze aflevering.")

	# sources.sort(key = lambda obj: obj.avg_bitrate)
	videoUrl = ""
	try:
		for s in sources:
			if(s["container"] == "MP4"):
				videoUrl = s["stream_name"].replace("mp4:", '')
				videoUrlBase = "https://vod-bc-prod-1.sbscdn.nl/"
				if not videoUrl.startswith(videoUrlBase):
					videoUrl = videoUrlBase+videoUrl
	except:
		ObjectContainer(header="Fout", message="Er is iets fout gegaan bij het ophalen van de afleveringskwaliteit aflevering.")
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
