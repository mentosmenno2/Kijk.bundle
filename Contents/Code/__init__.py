import string
import json
import urllib

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
			except: thumb = FallbackIcon

			url = e["_links"]["self"]
			oc.add(DirectoryObject(
				title = title,
				thumb = thumb,
				key = url
			))

	oc.objects.sort(key = lambda obj: obj.title.lower())
	if len(oc) > 0:
		return oc
	else:
		return ObjectContainer(header="Geen resultaten", message="Er zijn geen programma's gevonden")

####################################################################################################
def getFromAPI(path=''):
	receivedJson = urllib.urlopen(API_URL_V1+path).read();
	jsonObj = json.loads(receivedJson)
	return jsonObj

####################################################################################################
def sortByTitle(t):
	return t["title"]
