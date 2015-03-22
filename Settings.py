import json
import os

import GlobalValues


class Settings(object):
	settingsFilename = os.path.join(GlobalValues.carddatafolder, 'settings.json')
	_settings = {}
	settingsChanged = False

	def __init__(self):
		if os.path.exists(self.settingsFilename):
			with open(self.settingsFilename, 'r') as settingsFile:
				self._settings = json.load(settingsFile)
		# Fill in some defaults
		for key, defaultValue in (('showImages', True), ('cardUpdateCheckInterval', 172800)):
			if key not in self._settings:
				self.settingsChanged = True
				self._settings[key] = defaultValue

	def getSetting(self, key, defaultValue=None):
		if key in self._settings:
			return self._settings[key]
		return defaultValue

	def setSetting(self, key, value):
		self._settings[key] = value
		self.settingsChanged = True
		return value

	def saveSettings(self, ignoreChangeCheck=False):
		if self.settingsChanged or ignoreChangeCheck:
			with open(self.settingsFilename, 'w') as settingsfile:
				settingsfile.write(json.dumps(self._settings))