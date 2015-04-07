NAME = 'KIJK'
ICON = 'icon-default.png'
ART  = 'art-default.jpg'

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

####################################################################################################
def Start():

	ObjectContainer.title1 = NAME
	ObjectContainer.art = R(ART)

####################################################################################################
@handler('/video/kijk', NAME)
def MainMenu():

	#return channels()
	oc = ObjectContainer()

	for channel in CHANNELS:
		oc.add(DirectoryObject(
			title = channel['name'],
			thumb = R(channel['slug']+'.png'),
			key = Callback(gemist, channel=channel['slug'])
		))
	oc.add(DirectoryObject(
			title = 'Meest Bekeken',
			thumb = R(ICON),
			key = Callback(meestBekeken)
	))
	oc.add(DirectoryObject(
			title = 'Kijk Eerder',
			thumb = R(ICON),
			key = Callback(kijkEerder)
	))

	return oc

####################################################################################################
def gemist(channel):

	oc = ObjectContainer()

	html = HTML.ElementFromURL('http://www.kijk.nl/ajax/section/overview/missed_MissedChannel-'+channel)

	days = html.xpath('//h2[@class="showcase-heading"]//text()')

	for i,day in enumerate(days):
		oc.add(DirectoryObject(
			title = day.title(),
			thumb = R(channel+'.png'),
			key = Callback(gemistForDay, channel=channel, day=i)
		))

	return oc

####################################################################################################
def gemistForDay(channel, day):

	html = HTTP.Request('http://www.kijk.nl/ajax/section/overview/missed_MissedChannel-'+channel).content.split('<hr>')[day]
	html = HTML.ElementFromString(html)

	return ListRows(html)

####################################################################################################
def meestBekeken():

	return ListRowsFromAJAX('home_Episodes-popular/1/20')

####################################################################################################
def kijkEerder():

	return ListRowsFromAJAX('future_Future')

####################################################################################################
def ListRowsFromAJAX(path):

	html = HTTP.Request('http://www.kijk.nl/ajax/section/overview/'+path).content
	html = HTML.ElementFromString(html)

	return ListRows(html)

####################################################################################################
def ListRows(html):
	oc = ObjectContainer()
	elements = html.xpath('//div[a/div/@class="info "]')

	for e in elements:
		subtitle = e.xpath('./div/div/div[@class="title"]/text()')[0]
		title = e.xpath('./a/div/h3//text()')[0].strip()
		if len(subtitle.strip()) > 0:
			title = title+': '+subtitle

		thumb = Resource.ContentsOfURLWithFallback(e.xpath('./a/div/img[@itemprop="thumbnailUrl"]//@data-src')[0])
		url = 'http://kijk.nl'+e.xpath('./a[@itemprop="url"]//@href')[0]

		oc.add(VideoClipObject(
			title = title,
			thumb = thumb,
			url = url
		))

	if len(oc) > 0:
		return oc
	else:
		return MessageContainer("Geen shows beschikbaar", "Er zijn geen shows beschikbaar")