ART = 'art-default.jpg'
ICON = 'icon-default.png'
APPSTORE_URL = 'http://nine.plugins.plexapp.com/apps/%s.json'
ICON_URL = 'http://nine.plugins.plexapp.com%s'
TESTURLS_URL = 'http://localhost:32400/system/:/serviceTestURLs/%s'

TEST = {
	"Redirect (MP4)": [
		"com.plexapp.plugins.cnn",
		"com.plexapp.plugins.twitlive",
		"com.plexapp.plugins.thedailyshow"
	],
	"Redirect (FLV)": [
		"com.plexapp.plugins.euronews"
	],
	"Redirect (HLS)": [
		"com.plexapp.plugins.nationalgeographic"
	],
	"Indirect (MP4)": [
		"com.plexapp.plugins.vimeo",
		"com.plexapp.plugins.youtube",
		"com.plexapp.plugins.revision3",
		"com.plexapp.plugins.dailymotion"
	],
	"Indirect (MOV)": [
		"com.plexapp.plugins.amt"
	],
	"Indirect (RTMP)": [
		"com.plexapp.plugins.abc",
		"com.plexapp.plugins.cbs",
		"com.plexapp.plugins.ustream"
	],
	"Multiple Indirects (MP4)": [
		"com.plexapp.plugins.ted"
	],
	"Multiple Parts": [
		"com.plexapp.plugins.thedailyshow"
	],
	"Webkit": [
		"com.plexapp.plugins.4oD",
		"com.plexapp.plugins.nbc"
	],
	" Miscellaneous TestURLs": [
		"com.plexapp.plugins.test",
		"com.plexapp.plugins.fallback",
		"com.plexapp.plugins.blip"
	]
}

RADIO_THUMB = 'http://www.biography.com/imported/images/Biography/Images/Galleries/Billie%20Holiday/billie-holiday-thumb.jpg'
RADIO_TEST = [
	[
		('Billie Holiday', 'September Song', 'http://archive.org/download/BillieHoliday-41-50/BillieHoliday-SeptemberSong.mp3'),
		('Billie Holiday', 'Solitude', 'http://archive.org/download/BillieHoliday-41-50/BillieHoliday-Solitude.mp3'),
		('Billie Holiday', 'Strange Fruit', 'http://archive.org/download/BillieHoliday-41-50/BillieHoliday-StrangeFruit1939.mp3'),
	],
	[
		('Billie Holiday', 'Sugar', 'http://archive.org/download/BillieHoliday-41-50/BillieHoliday-Sugar.mp3'),
		('Billie Holiday', 'Tell Me More', 'http://archive.org/download/BillieHoliday-41-50/BillieHoliday-TellMeMore.mp3'),
		('Billie Holiday', 'That Old Devil', 'http://archive.org/download/BillieHoliday-41-50/BillieHoliday-ThatOldDevil.mp3'),
	],
	[
		('Billie Holiday', 'The Blues Are Brewin', 'http://archive.org/download/BillieHoliday-41-50/BillieHoliday-TheBluesAreBrewin.mp3'),
		('Billie Holiday', 'The Man I Love', 'http://archive.org/download/BillieHoliday-41-50/BillieHoliday-TheManILove.mp3'),
		('Billie Holiday', 'The Very Thought Of You', 'http://archive.org/download/BillieHoliday-41-50/BillieHoliday-TheVeryThoughtOfYou.mp3'),
	]
]

####################################################################################################
def Start():
	ObjectContainer.art = R(ART)
	ObjectContainer.title1 = 'Test'
	DirectoryObject.thumb = R(ICON)

####################################################################################################
@handler('/video/test', 'Test', art=ART, thumb=ICON)
def MainMenu():

	oc = ObjectContainer(no_cache=True)

	tests = TEST.keys()
	tests.sort()

	for test in tests:
		oc.add(DirectoryObject(
			key = Callback(GetIdentifiers, title=test),
			title = test
		))

	summary = ''

	if Prefs['username']:
		summary += 'Username: %s\n' % Prefs['username']

	if Prefs['password']:
		summary += 'Password: %s\n' % Prefs['password']

	if Prefs['test']:
		summary += 'Test: %s\n' % str(Prefs['test'])

	if Prefs['fruit']:
		summary += 'Fruit: %s\n' % Prefs['fruit']

	oc.add(PrefsObject(title='Preferences', summary=summary, thumb=R('icon-prefs.png')))
	
	oc.add(DirectoryObject(
		key = Callback(GetFrameworkFeatures),
		title = "Framework Features"
	))

	return oc

####################################################################################################
@route('/video/test/identifiers')
def GetIdentifiers(title):

	oc = ObjectContainer(title2=title, no_cache=True)

	for identifier in TEST[title]:
		summary = ''
		thumb = ''

		try:
			info = JSON.ObjectFromURL(APPSTORE_URL % identifier, cacheTime=CACHE_1HOUR)['app']
			title = info['name']
			thumb = ICON_URL % info['icon_url']

			if len(info['current_version']['regions']) > 0:
				geo = []
				for region in info['current_version']['regions']:
					geo.append(region['name'])

				summary += 'Available in: %s\n' % ', '.join(geo)
			else:
				summary += 'Available in: *\n'

			if 'client_platforms' in info and len(info['client_platforms']) > 0:
				summary += 'Client platforms: %s\n' % info['client_platforms'][0]['name']

			if 'client_platform_exclusions' in info and len(info['client_platform_exclusions']) > 0:
				summary += 'Client platforms exclusions: %s\n' % info['client_platform_exclusions'][0]['name']

		except:
			title = identifier

		oc.add(DirectoryObject(
			key = Callback(GetTestURLs, title=title, identifier=identifier),
			title = title,
			summary = summary,
			thumb = Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON)
		))

	return oc

####################################################################################################
@route('/video/test/{identifier}/gettesturls')
def GetTestURLs(title, identifier):

	oc = ObjectContainer(title2=title, no_cache=True)
	json = JSON.ObjectFromURL(TESTURLS_URL % identifier, cacheTime=0)[identifier]
	name = json.keys()[0]

	for url in json[name]:
		oc.add(URLService.MetadataObjectForURL(url))

	return oc

####################################################################################################
@route('/video/test/framework')
def GetFrameworkFeatures():
	return ObjectContainer(
		title2 = "Framework Features",
		objects = [
			PlaylistObject(
				key = Callback(TestRadioDirectories),
				title = "Radio Directories",
				radio = True,
			),
			DirectoryObject(
			    key = Callback(TestMessageObject),
			    title = "Message Objects",
			    summary = "For Message Objects, The header and message attributes are used in conjunction. They instruct the client to display a message dialog on loading the container, where header is the message dialog’s title and message is the body."
			),
			PopupDirectoryObject(
			    key = Callback(TestPopupObject),
			    title = "Popup Directories",
			    summary = "PopupDirectoryObjects are presented as a pop-up menu where possible, and are not added to the client’s history stack." 
			)
		]
	)
	
####################################################################################################
def RadioObjectForItem(page, index):
	items = RADIO_TEST[page - 1]
	artist, title, track_url = items[index]
	return TrackObject(
		key = Callback(TestRadioLookup, page = page, index = index),
		rating_key = track_url,
		album = "Demo album",
		artist = artist,
		title = title,
		thumb = 'http://www.biography.com/imported/images/Biography/Images/Galleries/Billie%20Holiday/billie-holiday-thumb.jpg',
		items = [
			MediaObject(
				audio_codec = AudioCodec.MP3,
				parts=[PartObject(key = track_url)],
			)
		],
	)

@route('/video/test/framework/radio', page = int)
def TestRadioDirectories(page = 1):
	oc = ObjectContainer()
	
	for index in range(len(RADIO_TEST[page - 1])):
		oc.add(RadioObjectForItem(page, index))
		
	if page < len(RADIO_TEST):
		oc.add(NextPageObject(key = Callback(TestRadioDirectories, page = page + 1), title = "Next Page"))
	
	return oc
	
@route('/video/test/framework/lookup')
def TestRadioLookup(page, index):
	return ObjectContainer(
		objects = [
			RadioObjectForItem(page, index)
		]
	)

####################################################################################################
@route('/video/test/framework/message')
def TestMessageObject():
    return ObjectContainer(header="Message Object", message="This should be presented to the user.")
    
####################################################################################################
@route('/video/test/framework/popup')
def TestPopupObject():
    return ObjectContainer(
        objects = [
            DirectoryObject(key=Callback(TestMessageObject), title="Test1"),
            DirectoryObject(key=Callback(TestMessageObject), title="Test2")
            DirectoryObject(key=Callback(TestMessageObject), title="Test3")
            ]
        )

