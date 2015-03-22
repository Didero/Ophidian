import json
import os
import re
import threading
import time
import Tkinter, ttk
import urllib
import zipfile

import GlobalValues


class CardFileDownloader(object):
	NO_UPDATE_NEEDED = 0
	UPDATE_SUCCESSFUL = 1
	UPDATE_FAILED = 2

	cardFormatVersion = '1.0'

	downloadProgressQueue = []
	updateProgressMessages = []
	downloadSucceeded = None

	def __init__(self, root):
		self.cardsLocation = os.path.join(GlobalValues.carddatafolder, 'cards.json')
		self.versionFileLocation = os.path.join(GlobalValues.carddatafolder, 'cardsversion.json')
		self.setInfofileLocation = os.path.join(GlobalValues.carddatafolder, 'sets.json')
		self.root = root

	def handleCardFileUpdate(self, showProgressWindow=True):
		# TODO: Make the check whether we should update threaded, so that it doesn't hold up the whole GUI. Progress window on actual download should still steal focus though
		shouldUpdate, latestVersionNumber = self.shouldCardFileBeUpdated()
		if shouldUpdate:
			updateArgs = (False,)
			progressWindow = None
			if showProgressWindow:
				# First create a window to show progress
				progressWindow = Tkinter.Toplevel(self.root)
				progressWindow.title("Ophidian Card Updater")
				# Attach it to the main window
				progressWindow.transient(self.root)
				# Steal its events
				progressWindow.grab_set()

				progressWindow.label = Tkinter.Label(progressWindow, text="Downloading card update...", anchor=Tkinter.CENTER)
				progressWindow.label.grid(column=0, row=0)
				progressWindow.progressBarValue = Tkinter.IntVar()
				progressWindow.progressBarValue.set(0)
				progressWindowProgressBar = ttk.Progressbar(progressWindow, orient=Tkinter.HORIZONTAL, mode='determinate', variable=progressWindow.progressBarValue)
				progressWindowProgressBar.grid(column=0, row=1)
				updateArgs = (True,)

				# Make sure the progresswindow's size is set properly
				progressWindow.update_idletasks()
				# Center the progress window relative to the main window
				progressWindow.geometry("{}x{}+{}+{}".format(progressWindow.winfo_width(), progressWindow.winfo_height(), GlobalValues.root.winfo_width()/2, GlobalValues.root.winfo_height()/2))
				# Reset the size, otherwise it will be 1 by 1 pixel. The position will stay the same
				progressWindow.geometry('')

				# Make sure the update window can't be closed, otherwise weird stuff starts happening
				# TODO: Handle update window closing better, by cancelling update for instance
				progressWindow.protocol('WM_DELETE_WINDOW', lambda: False)

			cardDownloadThread = threading.Thread(target=self.downloadAndFormatCardFile, args=updateArgs)
			cardDownloadThread.start()

			if showProgressWindow:
				self.progressWindowUpdater(progressWindow, progressWindow.progressBarValue, cardDownloadThread)
				# Keep the window up until the updates are done
				progressWindow.wait_window(progressWindow)

			if not self.downloadSucceeded:
				return self.UPDATE_FAILED
			else:
				versiondata = {'format': self.cardFormatVersion, 'cards': latestVersionNumber, 'lastChecked': time.time()}
				# Replace the old version file with the new one
				with open(self.versionFileLocation, 'w') as versionFile:
					versionFile.write(json.dumps(versiondata))
				return self.UPDATE_SUCCESSFUL
		return self.NO_UPDATE_NEEDED

	def progressWindowUpdater(self, progresswindow, progressbarValue, updaterThread):
		# Get the latest progress update
		if len(self.downloadProgressQueue) > 0:
			progressbarValue.set(self.downloadProgressQueue[-1])
			# Clear the queue
			del self.downloadProgressQueue[:]
		if len(self.updateProgressMessages) > 0:
			progresswindow.label.configure(text=self.updateProgressMessages.pop(0))
		# If it's still going, check progress again in a little while
		if updaterThread.isAlive():
			progresswindow.after(50, self.progressWindowUpdater, progresswindow, progressbarValue, updaterThread)
		# Otherwise we're done, destroy the window
		else:
			progresswindow.destroy()

	def shouldCardFileBeUpdated(self):
		localVersionInfo = self.getStoredVersionData()
		# Always download cards if at least one the required files doesn't exist
		if not localVersionInfo or not os.path.exists(self.cardsLocation) or not os.path.exists(self.setInfofileLocation):
			return (True, self.getLatestVersionNumber())
		# Don't check too often
		if 'lastChecked' in localVersionInfo and time.time() - localVersionInfo['lastChecked'] < GlobalValues.settings.getSetting('cardUpdateCheckInterval', 172800):  # Two days in seconds
			return (False, localVersionInfo['cards'])
		latestVersion = self.getLatestVersionNumber()
		# If we got an empty result, something went wrong with downloading the version number. Move on as if nothing happened (which is what happened)
		if not latestVersion:
			return (False, localVersionInfo['cards'])
		if self.cardFormatVersion != localVersionInfo['format'] or localVersionInfo['cards'] != latestVersion:
			# Write down when we last checked, so we can make sure we don't check too often
			localVersionInfo['lastChecked'] = time.time()
			with open(self.versionFileLocation, 'w') as versionfile:
				versionfile.write(json.dumps(localVersionInfo))
			return (True, latestVersion)
		return (False, localVersionInfo['cards'])

	@staticmethod
	def getLatestVersionNumber():
		# Download the latest version file
		url = "http://mtgjson.com/json/version.json"
		newversionfilename = os.path.join(GlobalValues.carddatafolder, 'onlinecardsversion.json')
		# Make sure the data folder actually exists before downloading anything to it
		if not os.path.exists(GlobalValues.carddatafolder):
			os.makedirs(GlobalValues.carddatafolder)
		try:
			urllib.urlretrieve(url, newversionfilename)
		except IOError as e:
			print "ERROR: Connection error while checking for card updates:"
			print e
			GlobalValues.statusbar.addMessage("An error occured while checking for card updates ({})".format(e.message))
			return None

		with open(newversionfilename) as newversionfile:
			latestVersion = newversionfile.read().replace('"', '').strip()
		os.remove(newversionfilename)
		return latestVersion

	def getStoredVersionData(self):
		# Load in the currently stored version number
		if os.path.exists(self.versionFileLocation):
			with open(self.versionFileLocation) as versionfile:
				return json.load(versionfile)
		# Version file doesn't exist
		return None

	def downloadAndFormatCardFile(self, reportProgressUpdates):
		# First make sure the subfolder exists
		if not os.path.exists(GlobalValues.carddatafolder):
			os.mkdir(GlobalValues.carddatafolder)

		# First download the cards file
		url = "http://mtgjson.com/json/AllSets-x.json.zip"
		cardzipFilename = os.path.join(GlobalValues.carddatafolder, 'AllSets-x.json.zip')
		urllib.urlretrieve(url, cardzipFilename, lambda blockcount, blocksize, totalsize: self.downloadProgressQueue.append((100 * blockcount * blocksize) / totalsize))

		if not os.path.exists(cardzipFilename):
			# Something went wrong during download, abort
			GlobalValues.statusbar.addMessage("WARNING: Card download aborted")
			self.downloadSucceeded = False
			return

		if reportProgressUpdates:
			# Clear the progress bar
			self.downloadProgressQueue.append(0.0)
			# And update the text to show what we're doing next
			self.updateProgressMessages.append("Unzipping downloaded file...")

		# Since it's a zip, extract it
		zipContainingCardfile = zipfile.ZipFile(cardzipFilename, 'r')
		downloadedCardsFilename = os.path.join(GlobalValues.carddatafolder, zipContainingCardfile.namelist()[0])
		if os.path.exists(downloadedCardsFilename):
			os.remove(downloadedCardsFilename)
		zipContainingCardfile.extractall(GlobalValues.carddatafolder)
		zipContainingCardfile.close()
		# We don't need the zip anymore
		os.remove(cardzipFilename)

		if reportProgressUpdates:
			self.updateProgressMessages.append("Opening downloaded file...")

		# Read the new file so we can save it in our preferred format (not per set, but just a dict of cards)
		with open(downloadedCardsFilename, 'r') as newcardfile:
			downloadedCardstore = json.load(newcardfile)

		def formatText(text):
			# Remove brackets around mana cost
			if '{' in text:
				text = text.replace('}{', ' ').replace('{', '').replace('}', '')
			# Replace newlines with spaces. If the sentence adds in a letter, add a period
			#text = re.sub('(?<=\w)\n', '. ', text).replace('\n', ' ')
			# Prevent double spaces
			text = text.replace(u'  ', u' ').strip()
			return text

		if reportProgressUpdates:
			self.updateProgressMessages.append("Formatting cards...")

		keysToRemove = ['border', 'foreignNames', 'imageName', 'originalText', 'originalType', 'printings',  # Printings can be removed because we build our own setlist
						'reserved', 'source', 'starter', 'subtypes', 'supertypes', 'timeshifted', 'watermark']
		listKeysToMakeString = ['colors']
		keysToFormatNicer = ['flavor', 'manacost', 'text']
		setKeysToStore = ['artist', 'flavor', 'number', 'multiverseid', 'rarity', 'variations']
		# Further down, 'colors' gets sorted, 'manaCost' gets turned into 'manacost' (lowercase), and the 'rulings' dict list gets turned into a string
		#  These aren't put in a list here, because they're single keys, and a single-item list and single-item for-loop are wasteful
		newcardstore = {}
		setstore = {}
		totalSetcount = len(downloadedCardstore)
		# Use the keys instead of iteritems() so we can pop off the set we need, to reduce memory usage
		for currentSetNumber in xrange(0, totalSetcount):
			setcode, setData = downloadedCardstore.popitem()
			if reportProgressUpdates:
				self.downloadProgressQueue.append(100 * currentSetNumber / totalSetcount)
			cardlist = setData.pop('cards')
			# Store info on the set too
			setstore[setData['name']] = setData
			# Again, pop off cards when we need them, to save on memory
			for cardcount in xrange(0, len(cardlist)):
				card = cardlist.pop(0)
				cardname = card['name'].lower()  # lowering the keys makes searching easier later, especially when comparing against the literal searchstring

				# If the card isn't in the store yet, parse its data
				if cardname not in newcardstore:
					# Remove some useless data to save some space, memory and time
					for keyToRemove in keysToRemove:
						if keyToRemove in card:
							del card[keyToRemove]

					# The 'Colors' field benefits from some ordering, for readability.
					if 'colors' in card:
						card['colors'] = sorted(card['colors'])

					# Make sure all stored values are strings, that makes searching later much easier
					for attrib in listKeysToMakeString:
						if attrib in card:
							card[attrib] = u"; ".join(card[attrib])

					# Make 'manaCost' lowercase, for easier searching
					if 'manaCost' in card:
						card['manacost'] = card['manaCost']
						del card['manaCost']

					for keyToFormat in keysToFormatNicer:
						if keyToFormat in card:
							card[keyToFormat] = formatText(card[keyToFormat])

					# The Rulings field is a list of dicts, format that nicer
					if 'rulings' in card:
						rulingsText = u""
						for dateRulingPair in card['rulings']:
							rulingsText += u"{}: {}\n".format(dateRulingPair['date'], formatText(dateRulingPair['text']))
						card['rulings'] = rulingsText.rstrip()

					# Add the card as a new entry, with a sets list ready to be filled out
					card['sets'] = {}
					newcardstore[cardname] = card

				# New and already listed cards need their set info stored
				cardSetInfo = {}
				for setKeyToStore in setKeysToStore:
					if setKeyToStore in card:
						value = card.pop(setKeyToStore)
						if setKeyToStore in keysToFormatNicer:
							value = formatText(value)
						cardSetInfo[setKeyToStore] = value
				newcardstore[cardname]['sets'][setData['name']] = cardSetInfo  # No need to check if there's any set info, because all cards have a Rarity field

		# First delete the original file
		if os.path.exists(self.cardsLocation):
			os.remove(self.cardsLocation)
		# Save the new database to disk
		with open(self.cardsLocation, 'w') as cardfile:
			cardfile.write(json.dumps(newcardstore))
		with open(self.setInfofileLocation, 'w') as setsfile:
			setsfile.write(json.dumps(setstore))

		# Remove the file downloaded from MTGjson.com
		os.remove(downloadedCardsFilename)
		self.downloadSucceeded = True
