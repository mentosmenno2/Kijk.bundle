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

import string
AZ = string.ascii_uppercase
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

	oc.add(DirectoryObject(
			title = 'Gemist',
			thumb = R(ICON),
			key = Callback(gemist)
	))
	oc.add(DirectoryObject(
			title = 'Meest Bekeken',
			thumb = R(ICON),
			key = Callback(meestBekeken)
	))
	oc.add(DirectoryObject(
			title = 'A-Z',
			thumb = R(ICON),
			key = Callback(AtoZ)
	))

	return oc

####################################################################################################
@route(PREFIX + '/gemist')
def gemist():

	oc = ObjectContainer(title2='Gemist')

	for channel in CHANNELS:
		oc.add(DirectoryObject(
			title = channel['name'],
			thumb = R(channel['slug']+'.png'),
			key = Callback(gemistForChannel, channel=channel['slug'])
		))

	return oc

####################################################################################################
@route(PREFIX + '/gemistForChannel')
def gemistForChannel(channel):

	oc = ObjectContainer(title2=(item['name'] for item in CHANNELS if item["slug"] == channel).next())

	html = HTML.ElementFromURL('http://www.kijk.nl/ajax/section/overview/missed_MissedChannel-'+channel)

	days = html.xpath('//h2[@class="showcase-heading"]//text()')

	for i,day in enumerate(days):
		oc.add(DirectoryObject(
			title = day.title(),
			thumb = R(channel+'.png'),
			key = Callback(gemistForDay, channel=channel, day=i, dayName=day.title())
		))

	return oc

####################################################################################################
@route(PREFIX + '/gemistForDay')
def gemistForDay(channel, day, dayName):

	html = HTTP.Request('http://www.kijk.nl/ajax/section/overview/missed_MissedChannel-'+channel).content.split('<hr>')[int(day)]

	return ListRows(HTML.ElementFromString(html), title2=dayName)

####################################################################################################
@route(PREFIX + '/meestBekeken')
def meestBekeken():

	return ListRowsFromAJAX('home_Episodes-popular/1/20', title2='Meest Bekeken')

####################################################################################################
@route(PREFIX + '/AtoZ')
def AtoZ():

	oc = ObjectContainer(title2='A-Z')

	for i in range(0, len(AZ)):
		oc.add(DirectoryObject(
			title = AZ[i],
			thumb = R(ICON),
			key = Callback(ListRowsFromAJAX, path='programs-abc-'+AZ[i], title2=AZ[i])
		))

	return oc

####################################################################################################
@route(PREFIX + '/ListRowsFromAJAX')
def ListRowsFromAJAX(path, FallbackIcon='', title2=''):

	return ListRows(HTML.ElementFromURL('http://www.kijk.nl/ajax/section/overview/'+path), FallbackIcon, title2)

####################################################################################################
def ListRows(html, FallbackIcon='', title2=''):

	oc = ObjectContainer(title2=title2)
	elements = html.xpath('//div[a/div/@class="info "]')

	for e in elements:
		try: subtitle = e.xpath('./div/div/div[@class="title"]/text()')[0]
		except: subtitle = ''

		title = e.xpath('./a/div/h3//text()')[0].strip()
		if len(subtitle.strip()) > 0 and title != subtitle:
			title = title+': '+subtitle

		try: thumb = Resource.ContentsOfURLWithFallback(e.xpath('./a/div/img[@itemprop="thumbnailUrl"]//@data-src')[0])
		except: thumb = FallbackIcon

		url = e.xpath('./a[@itemprop="url"]//@href')[0]

		if len(url.split('/')) == 3:
			channel = url.split('/')[1]
			series = url.split('/')[2]

			url = Callback(ListRowsFromAJAX, path='series-'+series+'.'+channel+'_Episodes-serie/1/500', FallbackIcon=thumb, title2=title)

			oc.add(DirectoryObject(
				title = title,
				thumb = thumb,
				key = url
			))
		else:
			oc.add(VideoClipObject(
				title = title,
				thumb = thumb,
				url = 'http://kijk.nl'+url
			))

	if len(oc) > 0:
		return oc
	else:
		return ObjectContainer(header="Geen afleveringen beschikbaar", message="Er zijn geen afleveringen beschikbaar")