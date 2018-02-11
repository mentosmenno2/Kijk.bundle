import string
import json
import urllib2
import datetime

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
KIJKEMBED_VIDEO_URL = "http://embed.kijk.nl/api/video/"
BRIGHTCOVE_VIDEO_URL = "https://edge.api.brightcove.com/playback/v1/accounts/585049245001/videos/"


####################################################################################################
def Start():

	ObjectContainer.title1 = NAME
	ObjectContainer.art = R(ART)
	ObjectContainer.view_group = 'Details'

	DirectoryObject.thumb = R(ICON)
	DirectoryObject.art = R(ART)

	VideoClipObject.thumb = R(ICON)
	VideoClipObject.art = R(ART)

	Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
	Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36'

####################################################################################################
@handler(PREFIX, NAME, thumb=ICON, art=ART)
def MainMenu():

	oc = ObjectContainer()

	oc.add(DirectoryObject(
			title = L("MISSED"),
			thumb = R(ICON),
			art = R(ART),
			key = Callback(MissedDayList, title2=L("MISSED"))
			#https://api.kijk.nl/v2/templates/page/missed/all/20180208
	))
	oc.add(DirectoryObject(
			title = L("POPULAR_EPISODES"),
			thumb = R(ICON),
			art = R(ART),
			key = Callback(PopularList, title2=L("POPULAR_EPISODES"))
			#https://api.kijk.nl/v2/default/sections/popular_PopularVODs
	))
	oc.add(DirectoryObject(
			title = L("PROGRAMS_LIST"),
			thumb = R(ICON),
			art = R(ART),
			key = Callback(ProgramsList, title2=L("PROGRAMS_LIST"))
	))

	return oc

####################################################################################################
@route(PREFIX + '/missedDayList')
def MissedDayList(title2='', path=''):

	oc = ObjectContainer(title2=title2)
	dayStrings = [L("MONDAY"), L("TUESDAY"), L("WEDNESDAY"), L("THURSDAY"), L("FRIDAY"), L("SATURDAY"), L("SUNDAY")]
	now = datetime.datetime.today()
	for index in range(0, 7):
		dayDate = now - datetime.timedelta(index)
		dayName = dayStrings[dayDate.weekday()]
		dayPath = "templates/page/missed/all/"+dayDate.strftime("%Y%m%d")

		if(index == 0):
			dayName = L("TODAY")
		if(index == 1):
			dayName = L("YESTERDAY")

		oc.add(DirectoryObject(
				title = dayName,
				thumb = R(ICON),
				art = R(ART),
				key = Callback(MissedEpisodesList, title2=dayName, path=dayPath)
		))

	return oc

####################################################################################################
@indirect
@route(PREFIX + '/missedEpisodesList')
def MissedEpisodesList(title2='', path=''):

	oc = ObjectContainer(title2=title2, art=R(ART))

	try:
		jsonObj = getFromAPI2(path=path)
		components = jsonObj["components"]
	except:
		return errorMessage(L("ERROR_EPISODES_RETREIVING"))

	for c in components:
		if c["type"] == "video_list":
			try:
				elements = c["data"]["items"]
			except:
				return errorMessage(L("ERROR_EPISODES_NO_RESULTS"))

			for e in elements:
				try: newPath = BRIGHTCOVE_VIDEO_URL+e["brightcoveId"]
				except: newPath = KIJKEMBED_VIDEO_URL+e["id"]

				try: title = e["title"]
				except: title = ''

				try: seasonLabelShort = e["seasonLabelShort"]
				except: seasonLabelShort = ''

				try: episode = e["episode"]
				except: episode = ''

				try: episodeLabel = e["episodeLabel"]
				except: episodeLabel = ''

				try: summary = e["synopsis"]
				except: summary = ''

				try: thumbUrl = e["images"]["nonretina_image"]
				except: thumbUrl = ''

				try: artUrl = e["images"]["nonretina_image_pdp_header"]
				except: artUrl = ''

				thumb = Resource.ContentsOfURLWithFallback(thumbUrl, R(ICON))

				art = Resource.ContentsOfURLWithFallback(artUrl, R(ART))

				try: millis = e["durationSeconds"]*1000
				except: millis = 0

				oc.add(VideoClipObject(
					title = title+" - "+seasonLabelShort+"E"+episode+": "+episodeLabel,
					thumb = thumb,
					summary = summary,
					art = art,
					duration = millis,
					url = newPath
				))

	if len(oc) > 0:
		return oc
	else:
		return errorMessage(L("ERROR_EPISODES_NO_RESULTS"))

####################################################################################################
@indirect
@route(PREFIX + '/popularList')
def PopularList(title2=''):

	oc = ObjectContainer(title2=title2, art=R(ART))

	try:
		jsonObj = getFromAPI2(path='default/sections/popular_PopularVODs?limit=999&offset=0')
	except:
		return errorMessage(L("ERROR_EPISODES_RETREIVING"))

	try:
		elements = jsonObj["items"]
	except:
		return errorMessage(L("ERROR_EPISODES_NO_RESULTS"))

	for e in elements:
		try: newPath = BRIGHTCOVE_VIDEO_URL+e["brightcoveId"]
		except: newPath = KIJKEMBED_VIDEO_URL+e["id"]

		try: title = e["title"]
		except: title = ''

		try: seasonLabelShort = e["seasonLabelShort"]
		except: seasonLabelShort = ''

		try: episode = e["episode"]
		except: episode = ''

		try: episodeLabel = e["episodeLabel"]
		except: episodeLabel = ''

		try: summary = e["synopsis"]
		except: summary = ''

		try: thumbUrl = e["images"]["nonretina_image"]
		except: thumbUrl = ''

		try: artUrl = e["images"]["nonretina_image_pdp_header"]
		except: artUrl = ''

		thumb = Resource.ContentsOfURLWithFallback(thumbUrl, R(ICON))

		art = Resource.ContentsOfURLWithFallback(artUrl, R(ART))

		try: millis = e["durationSeconds"]*1000
		except: millis = 0

		oc.add(VideoClipObject(
			title = title+" - "+seasonLabelShort+"E"+episode+": "+episodeLabel,
			thumb = thumb,
			summary = summary,
			art = art,
			duration = millis,
			url = newPath
		))

	if len(oc) > 0:
		return oc
	else:
		return errorMessage(L("ERROR_EPISODES_NO_RESULTS"))

####################################################################################################
@indirect
@route(PREFIX + '/programsList')
def ProgramsList(title2=''):

	oc = ObjectContainer(title2=title2, art=R(ART))

	try:
		jsonObj = getFromAPI(path='default/sections/programs-abc-'+DIGS+AZ_LOWER+'?limit=999&offset=0')
	except:
		return errorMessage(L("ERROR_PROGRAMS_RETREIVING"))

	try:
		elements = jsonObj["items"]
	except:
		return errorMessage(L("ERROR_PROGRAMS_NO_RESULTS"))

	for e in elements:
		if e["available"]:
			try: title = e["title"]
			except: title = ''

			try: summary = e["synopsis"]
			except: summary = ''

			try: thumbUrl = e["images"]["nonretina_image"]
			except: thumbUrl = ''

			try: artUrl = e["images"]["nonretina_image_pdp_header"]
			except: artUrl = ''

			thumb = Resource.ContentsOfURLWithFallback(thumbUrl, R(ICON))

			art = Resource.ContentsOfURLWithFallback(artUrl, R(ART))

			try: millis = int(e["duration"].replace(' min.', ''))*60*1000
			except: millis = 0

			oc.add(DirectoryObject(
				title = title,
				thumb = thumb,
				summary = summary,
				art = art,
				duration = millis,
				key = Callback(EpisodeList, title2=title, path=e["_links"]["self"], art=art)
			))

	oc.objects.sort(key = lambda obj: obj.title.lower())
	if len(oc) > 0:
		return oc
	else:
		return errorMessage(L("ERROR_PROGRAMS_NO_RESULTS"))

####################################################################################################
@indirect
@route(PREFIX + '/episodeList')
def EpisodeList(title2='', path='', art=R(ART)):

	oc = ObjectContainer(title2=title2, art=art)

	try:
		jsonObj = getFromAPI(path=path)
		sections = jsonObj["sections"]
	except:
		return errorMessage(L("ERROR_EPISODES_RETREIVING"))

	for s in sections:
		if s["type"] == "horizontal-single":
			try:
				elements = s["items"]
			except:
				return errorMessage(L("ERROR_EPISODES_NO_RESULTS"))

			for e in elements:
				try: newPath = BRIGHTCOVE_VIDEO_URL+e["brightcoveId"]
				except: newPath = KIJKEMBED_VIDEO_URL+e["id"]

				try: seasonLabelShort = e["seasonLabelShort"]
				except: seasonLabelShort = ''

				try: episode = e["episode"]
				except: episode = ''

				try: episodeLabel = e["episodeLabel"]
				except: episodeLabel = ''

				try: summary = e["synopsis"]
				except: summary = ''

				try: thumbUrl = e["images"]["nonretina_image"]
				except: thumbUrl = ''

				try: artUrl = e["images"]["nonretina_image_pdp_header"]
				except: artUrl = ''

				thumb = Resource.ContentsOfURLWithFallback(thumbUrl, R(ICON))

				art = Resource.ContentsOfURLWithFallback(artUrl, R(ART))

				try: millis = e["durationSeconds"]*1000
				except: millis = 0

				oc.add(VideoClipObject(
					title = seasonLabelShort+"E"+episode+": "+episodeLabel,
					thumb = thumb,
					summary = summary,
					art = art,
					duration = millis,
					url = newPath
				))

	if len(oc) > 0:
		return oc
	else:
		return errorMessage(L("ERROR_EPISODES_NO_RESULTS"))

####################################################################################################
@indirect
def getFromAPI(path=''):
	#receivedJson = urllib.urlopen(API_URL_V1+path).read()
	#jsonObj = json.loads(receivedJson)
	#return jsonObj
	return JSON.ObjectFromURL(API_URL_V1+path)

####################################################################################################
@indirect
def getFromAPI2(path=''):
	#receivedJson = urllib.urlopen(API_URL_V1+path).read()
	#jsonObj = json.loads(receivedJson)
	#return jsonObj
	return JSON.ObjectFromURL(API_URL_V2+path)

####################################################################################################
def errorMessage(message = ''):
	return ObjectContainer(header=L("ERROR"), message=message)
