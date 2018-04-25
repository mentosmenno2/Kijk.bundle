import string
import json
import urllib
import urllib2
import ssl
import datetime

NAME   = 'KIJK 2.0'
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

ICON_MISSED = 'missed.png'
ICON_POPULAR = 'popular.png'
ICON_PROGRAMS = 'programs.png'
ICON_SEARCH = 'search.png'

AZ_UPPER = string.ascii_uppercase
AZ_LOWER = string.ascii_lowercase
DIGS = string.digits

API_URL_V1 = 'https://api.kijk.nl/v1/'
API_URL_V2 = 'https://api.kijk.nl/v2/'

RE_SERIES = 'http://kijk.nl/(.*?)/(.*?)'
KIJKEMBED_API_URL = "https://embed.kijk.nl/api/video/"
BRIGHTCOVE_API_URL = "https://edge.api.brightcove.com/playback/v1/accounts/585049245001/videos/"


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
		thumb = R(ICON_MISSED),
		art = R(ART),
		key = Callback(MissedDayList, title2=L("MISSED"))
		#https://api.kijk.nl/v2/templates/page/missed/all/20180208
	))
	oc.add(DirectoryObject(
		title = L("POPULAR_EPISODES"),
		thumb = R(ICON_POPULAR),
		art = R(ART),
		key = Callback(PopularList, title2=L("POPULAR_EPISODES"))
		#https://api.kijk.nl/v2/default/sections/popular_PopularVODs
	))
	oc.add(DirectoryObject(
		title = L("PROGRAMS_LIST"),
		thumb = R(ICON_PROGRAMS),
		art = R(ART),
		key = Callback(ProgramsList, title2=L("PROGRAMS_LIST"))
	))
	oc.add(InputDirectoryObject(
		title = L("SEARCH"),
		thumb = R(ICON_SEARCH),
		art = R(ART),
		prompt = L("SEARCH_PROMPT"),
		key = Callback(Search, title2=L("SEARCH"))
	))
	oc.add(PrefsObject(
		title = L("SETTINGS"),
		thumb = R(ICON),
		art = R(ART)
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
		dayDateString = dayDate.strftime("%d-%m-%Y")
		dayPath = "default/sections/missed-all-"+dayDate.strftime("%Y%m%d")+"?limit=350&offset=0"

		if(index == 0):
			dayName = L("TODAY")
		if(index == 1):
			dayName = L("YESTERDAY")

		oc.add(DirectoryObject(
				title = dayName+": "+dayDateString,
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
		jsonObj = getFromAPI(path=path)
	except:
		return errorMessage(L("ERROR_EPISODES_RETREIVING"))

	try:
		elements = jsonObj["items"]
	except:
		return errorMessage(L("ERROR_EPISODES_NO_RESULTS"))

	for e in elements:
		try: available = e["available"]
		except: available = False

		if onlyMP4() and "brightcoveId" not in e:
			available = False

		if not available:
			continue

		try: newPath = BRIGHTCOVE_API_URL+e["brightcoveId"]
		except: newPath = KIJKEMBED_API_URL+e["id"]

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
		jsonObj = getFromAPI2(path='default/sections/popular_PopularVODs?limit=20&offset=0')
	except:
		return errorMessage(L("ERROR_EPISODES_RETREIVING"))

	try:
		elements = jsonObj["items"]
	except:
		return errorMessage(L("ERROR_EPISODES_NO_RESULTS"))

	for e in elements:
		try: available = e["available"]
		except: available = False

		if onlyMP4() and "brightcoveId" not in e:
			available = False

		if not available:
			continue

		try: newPath = BRIGHTCOVE_API_URL+e["brightcoveId"]
		except: newPath = KIJKEMBED_API_URL+e["id"]

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
		jsonObj = getFromAPI2(path='templates/page/abc')
	except:
		return errorMessage(L("ERROR_PROGRAMS_RETREIVING"))

	try:
		components = jsonObj["components"]
	except:
		return errorMessage(L("ERROR_PROGRAMS_RETREIVING"))

	for comp in components:
		try: objType = comp["type"]
		except: objType = ''
		if objType == "letter_programs_list":
			pageProgList = comp["data"]["items"]

			for programslist in pageProgList:
				try: objType = programslist["type"]
				except: objType = ''
				if objType == "letter_programs":

					letters = programslist["data"]["items"]
					for letter in letters:
						Log(letter["data"]["title"])
						elements = letter["data"]["items"]

						for e in elements:
							try: available = e["available"]
							except: available = False

							# if onlyMP4() and "brightcoveId" not in e:
							# 	available = False

							if not available:
								continue

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

	hasMoreItems = False
	for s in sections:
		try: objType = s["type"]
		except: objType = ''

		if objType == "horizontal-single":
			try: hasMoreItems = s["hasMoreItems"]
			except: objType = False

			try:
				elements = s["items"]
			except:
				return errorMessage(L("ERROR_EPISODES_NO_RESULTS"))

			for e in elements:
				try: available = e["available"]
				except: available = False

				if onlyMP4() and "brightcoveId" not in e:
					available = False

				if not available:
					continue

				try: newPath = BRIGHTCOVE_API_URL+e["brightcoveId"]
				except: newPath = KIJKEMBED_API_URL+e["id"]

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

	if hasMoreItems:
		for s in sections:
			try: objType = s["type"]
			except: objType = ''

			if objType == "slider":
				try:
					sliderSections = s["sections"]
				except:
					continue

				for sliderSection in sliderSections:
					try:
						sliderTabSections = sliderSection["sections"]
					except:
						continue

				for sliderTabSection in sliderTabSections:
					try: objType = sliderTabSection["type"]
					except: objType = ''

					if objType == "vertical":
						try:
							elements = sliderTabSection["items"]
						except:
							continue

						for e in elements:
							try: available = e["available"]
							except: available = False

							if onlyMP4() and "brightcoveId" not in e:
								available = False

							if not available:
								continue

							try: newPath = BRIGHTCOVE_API_URL+e["brightcoveId"]
							except: newPath = KIJKEMBED_API_URL+e["id"]

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
@route(PREFIX + '/search')
def Search(title2='', query=''):
	oc = ObjectContainer(title2=title2, art=R(ART))

	try:
		encodedQuery = urllib.quote_plus(query)
		jsonObj = getSearchResult(path='default/searchresultsgrouped?search='+encodedQuery)
	except:
		return errorMessage(L("ERROR_SEARCH_RETREIVING"))

	try:
		elements = jsonObj["results"]
	except:
		return errorMessage(L("ERROR_PROGRAMS_NO_RESULTS"))

	for e in elements:
		try: objType = e["type"]
		except: objType = ''

		if objType == "series":
			try: title = e["title"]+": "+e["subtitle"]
			except: title = ''

			try: summary = next((item for item in CHANNELS if item['slug'] == e["channel"]), None)["name"]
			except: summary = ''

			try: thumbUrl = e["images"]["nonretina_image"]
			except: thumbUrl = ''

			try: artUrl = e["images"]["nonretina_image_pdp_header"]
			except: artUrl = ''

			thumb = Resource.ContentsOfURLWithFallback(thumbUrl, R(ICON))

			art = Resource.ContentsOfURLWithFallback(artUrl, R(ART))

			oc.add(DirectoryObject(
				title = title,
				thumb = thumb,
				summary = summary,
				art = art,
				key = Callback(EpisodeList, title2=title, path='default/pages/series-'+e["_links"]["self"], art=art)
			))

			try: episodes = e["episodes"]
			except: episodes = []

			for episode in episodes:

				try: newPath = BRIGHTCOVE_API_URL+episode["brightcoveId"]
				except: newPath = KIJKEMBED_API_URL+episode["id"]

				try: title = episode["title"]+": "+episode["subtitle"]
				except: title = ''

				try: summary = next((item for item in CHANNELS if item['slug'] == e["channel"]), None)["name"]
				except: summary = ''

				try: thumbUrl = episode["images"]["nonretina_image"]
				except: thumbUrl = ''

				try: artUrl = episode["images"]["nonretina_image_pdp_header"]
				except: artUrl = ''

				thumb = Resource.ContentsOfURLWithFallback(thumbUrl, R(ICON))

				art = Resource.ContentsOfURLWithFallback(artUrl, R(ART))

				oc.add(VideoClipObject(
					title = title,
					thumb = thumb,
					summary = summary,
					art = art,
					url = newPath
				))

	if len(oc) > 0:
		return oc
	else:
		return errorMessage(L("ERROR_SEARCH_NO_RESULTS"))

####################################################################################################
@indirect
def getFromAPI(path=''):
	#receivedJson = urllib.urlopen(API_URL_V1+path).read()
	#jsonObj = json.loads(receivedJson)
	#return jsonObj
	return JSON.ObjectFromURL(API_URL_V1+path)

@indirect
def getSearchResult(path=''):
	Log("GetSearchResult")
	Log(API_URL_V1+path)
	gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
	receivedJson = urllib2.urlopen(API_URL_V1+path, context=gcontext).read()
	Log(receivedJson)
	receivedJson = "{\"results\": "+receivedJson+"}"
	jsonObj = json.loads(receivedJson)
	return jsonObj

####################################################################################################
@indirect
def getFromAPI2(path=''):
	#receivedJson = urllib.urlopen(API_URL_V1+path).read()
	#jsonObj = json.loads(receivedJson)
	#return jsonObj
	return JSON.ObjectFromURL(API_URL_V2+path)

####################################################################################################
def onlyMP4():
	onlymp4 = False
	if Client.Platform == 'Samsung': #Samsung smart tv
		onlymp4 = True
	return onlymp4

####################################################################################################
def errorMessage(message = ''):
	return ObjectContainer(header=L("ERROR"), message=message)
