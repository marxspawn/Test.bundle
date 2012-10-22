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
		"com.plexapp.plugins.syfy",
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

####################################################################################################
def Start():

	Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
	Plugin.AddViewGroup('InfoList', viewMode='InfoList', mediaType='items')

	ObjectContainer.art = R(ART)
	ObjectContainer.title1 = 'Test'
	DirectoryObject.thumb = R(ICON)

	HTTP.CacheTime = CACHE_1HOUR

####################################################################################################
@handler('/video/test', 'Test', art=ART, thumb=ICON)
def MainMenu():

	oc = ObjectContainer(view_group='InfoList', no_cache=True)

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

	return oc

####################################################################################################
@route('/video/test/identifiers')
def GetIdentifiers(title):

	oc = ObjectContainer(title2=title, view_group='InfoList', no_cache=True)

	for identifier in TEST[title]:
		summary = ''
		thumb = ''

		try:
			info = JSON.ObjectFromURL(APPSTORE_URL % identifier)['app']
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

	oc = ObjectContainer(title2=title, view_group='InfoList', no_cache=True)
	json = JSON.ObjectFromURL(TESTURLS_URL % identifier)[identifier]
	name = json.keys()[0]

	for url in json[name]:
		oc.add(URLService.MetadataObjectForURL(url))

	return oc
