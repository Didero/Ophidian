# -*- coding: utf-8 -*-

import os
import threading
import Tkinter, ttk
import traceback
import unicodedata
import urllib

import GlobalValues
from ScrollableFrame import ScrollableFrame

PILerrorMessage = None
try:
	from PIL import Image, ImageTk
except ImportError as e:
	GlobalValues.isImageLibraryLoaded = False
	print "WARNING: Image library PIL could not be loaded, not displaying images:", e
	PILerrorMessage = "Images not shown! ({})".format(e.message)
else:
	GlobalValues.isImageLibraryLoaded = True


class CardDisplayFrame(Tkinter.Frame):
	fieldOrder = ('name', 'type', 'watermark', 'layout', 'manacost', 'cmc', 'layout', 'names', 'power', 'toughness', 'loyalty', 'hand', 'life',
				  'text', 'artist', 'rulings', 'sets', 'rarity', 'flavor')
	setFields = ['flavor', 'rarity']  # A list of fields that can be different for each set print of that card
	fieldDisplayname = {'cmc': 'CMC:', 'hand': 'Hand Mod:', 'life': 'Life Mod:', 'names': 'Other Card(s):'}
	fieldToLabel = {}  # In this dict keys are the field name, and the corresponding value is a 2-tuple with the name label widget and value label widget
	# Field values from the card dataset will be fed to these functions for further parsing
	fieldParseCommands = {'layout': lambda self, layoutValue: None if layoutValue == 'normal' else layoutValue.capitalize(),  # Hide the layout field if the card layout is normal
						  'names': lambda self, nameslist: u"; ".join([name for name in nameslist if name.lower() != self.currentlyDisplayedCard]),  # Remove the current card from the list
						  'sets': lambda self, setdict: u"; ".join(setdict) + u' ({} sets)'.format(len(setdict)),  # Display a list of the sets
						  }

	currentlyDisplayedCard = None
	currentlyDisplayedSet = None

	displayType = None

	def __init__(self, parentFrame, width, height):
		Tkinter.Frame.__init__(self, parentFrame, width=width, height=height)

		# Show the message here instead of at the import statement, to give the Statusbar time to initialize
		if PILerrorMessage:
			GlobalValues.statusbar.addMessage(PILerrorMessage)

		# TODO: Maybe move the 'add card to deck/sideboard' buttons to the SearchResultsFrame? And the '+/-/x' buttons to the ChosenCardsFrame?
		#  They kind of make more sense there, since they interact with those fields
		#  Or maybe even move the 'add card' buttons to the ChosenCardsFrame too, since that's where they'd be added anyway

		# TODO: Occasional update checks to see if images got updated
		#  This could be done by storing the version number of mtgimage.com, and when that changes, retrieve the changelog
		#  Then, search the latest change(s) for setnames, and deleting the whole folder, forcing the images to be redownloaded

		# TODO: Display variation art of cards in same set
		# Some sets have multiple of the same card but with different art (Mostly lands, most sets have 4 different land arts per land type)
		#  The multiverseIDs of the other cards is stored in the 'variations' set field

		self.cardDataFrame = ScrollableFrame(self, width=width, height=height)
		self.cardDataFrame.grid(column=0, row=1, columnspan=2, rowspan=2, sticky=Tkinter.N)

		for rowcount, field in enumerate(self.fieldOrder):
			displayname = self.fieldDisplayname[field] if field in self.fieldDisplayname else "{}:".format(field.capitalize())
			namelabel = Tkinter.Label(self.cardDataFrame.innerFrame, text=displayname, anchor=Tkinter.NE)
			# Add and remove the label, so the 'sticky' part stays set
			#namelabel.grid(column=0, row=rowcount, sticky=Tkinter.NE)
			#namelabel.grid_remove()
			valuelabel = Tkinter.Label(self.cardDataFrame.innerFrame, text='', width=70, wraplength=375, justify=Tkinter.LEFT, anchor=Tkinter.W)
			self.fieldToLabel[field] = namelabel, valuelabel

		self.setSelectionCombobox = ttk.Combobox(self.cardDataFrame.innerFrame, state='readonly', width=50)
		self.setSelectionCombobox.bind('<<ComboboxSelected>>', lambda arg: self.setDisplayedSet(self.setSelectionCombobox.get()))
		self.setSelectionCombobox.label = Tkinter.Label(self.cardDataFrame.innerFrame, anchor=Tkinter.NE, text="Display Set:")

		self.cardImageLabel = Tkinter.Label(self.cardDataFrame.innerFrame)
		self.cardImageLabel.grid(column=0, row=100, columnspan=2, sticky=Tkinter.NW, padx=width/10)

	def toggleShowingImages(self):
		if GlobalValues.settings.getSetting('showImages', True):
			if self.currentlyDisplayedSet and self.currentlyDisplayedCard:
				self.retrieveAndDisplayCardImage(self.currentlyDisplayedSet, self.currentlyDisplayedCard)
		else:
			self.cardImageLabel.configure(image="")  # Clear the current image

	def constructCardImagePath(self, setname, cardname):
		# First clean up the names a bit, so the OS doesn't get confused by weird characters
		return os.path.join(GlobalValues.mainfolder, "images", self.removeSpecialCharsFromString(setname),
							u"{}.jpg".format(self.removeSpecialCharsFromString(cardname)))

	@staticmethod
	def removeSpecialCharsFromString(s):
		# First remove some really unusual characters and characters that aren't allowed in filenames
		for char in ['"', ':']:
			s = s.replace(char, '')
		# Some characters don't parse well, replace them with more common equivalents
		s = s.replace(u'æ', 'ae').replace(u'—', '-')
		# Then turn accented characters in their un-accented equivalent
		s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore')
		return s

	def displayCard(self, cardname, setname=None):
		self.currentlyDisplayedCard = cardname
		# If no setname was provided, just pick the first one in the list of sets this card is in
		if not setname:
			setname = GlobalValues.cards[cardname]['sets'].keys()[0]
		self.currentlyDisplayedSet = setname
		cardinfo = GlobalValues.cards[cardname]
		for fieldcount, field in enumerate(self.fieldOrder):
			fieldvalue = None
			if field in self.setFields and field in cardinfo['sets'][setname]:
				fieldvalue = cardinfo['sets'][setname][field]
			elif field in cardinfo:
				fieldvalue = cardinfo[field]
			if fieldvalue is not None:
				# Field does exist! Make sure it's shown, and filled in properly
				self.fieldToLabel[field][0].grid(column=0, row=fieldcount, sticky=Tkinter.NE)
				self.fieldToLabel[field][1].grid(column=1, row=fieldcount)
				# If we need to parse the value in a special way, do that
				if field in self.fieldParseCommands:
					fieldvalue = self.fieldParseCommands[field](self, fieldvalue)
				# A fieldparse command could return None, handle that
				if fieldvalue:
					self.fieldToLabel[field][1].configure(text=fieldvalue)
			if fieldvalue is None:
				# Field doesn't exist, hide it
				self.fieldToLabel[field][0].grid_remove()
				self.fieldToLabel[field][1].grid_remove()

		# Update the set selector, or hide it if the card is in only one set
		if len(cardinfo['sets']) > 1:
			self.setSelectionCombobox.label.grid(column=0, row=99)
			self.setSelectionCombobox.configure(values=cardinfo['sets'].keys())
			self.setSelectionCombobox.set(setname)
			self.setSelectionCombobox.grid(column=1, row=99, sticky=Tkinter.W)
		else:
			self.setSelectionCombobox.label.grid_remove()
			self.setSelectionCombobox.grid_remove()

		# If we already have the image, show it, if we should
		if GlobalValues.isImageLibraryLoaded and GlobalValues.settings.getSetting('showImages', True):
			# TODO: Show a 'loading' image, perhaps the backside of cards?
			# TODO: If a card is in multiple sets, and the first set doesn't have a multiverseid so we can't retrieve picture, go to next set
			self.cardImageLabel.configure(image="")
			self.retrieveAndDisplayCardImage(setname, cardname)

	def retrieveAndDisplayCardImage(self, setname, cardname):
		# If we already have the image, just draw it
		if os.path.exists(self.constructCardImagePath(setname, cardname)):
			self.drawCardImage(setname, cardname)
		# Otherwise, retrieve it
		else:
			self.cardImageLabel.configure(text="Downloading...")
			# Fetch the card image in a new thread, to not freeze the GUI
			cardImageDownloadThread = threading.Thread(target=self.downloadCardImage, args=(setname, cardname))
			cardImageDownloadThread.start()

	def drawCardImage(self, setname, cardname):
		img = Image.open(self.constructCardImagePath(setname, cardname))
		# Make sure the image isn't too wide
		width, height = img.size
		maxwidth = self.configure('width')[-1] - 20.0
		if width > maxwidth:
			# Too large! Calculate the aspect ratio, and reduce the height as much as the width, so it doesn't get stretched
			ratio = width / maxwidth
			newheight = height / ratio
			print u"Image for '{}/{}' too large, changing size from {}, {} to {}, {} (ratio {})".format(setname, cardname, width, height, maxwidth, newheight, ratio)
			GlobalValues.statusbar.addMessage(u"Image for card '{}' is too large, shrinking to {:.0f}%".format(ratio * 100))
			img = img.resize((int(maxwidth), int(round(newheight))), Image.ANTIALIAS)
		try:
			img = ImageTk.PhotoImage(img)
		except IOError as e:
			GlobalValues.statusbar.addMessage("ERROR displaying image for '{}' ({})".format(cardname, e.message))
			self.cardImageLabel.configure(text='')
			# Delete the offending image, redownloading might fix the problem
			os.remove(self.constructCardImagePath(setname, cardname))
		else:
			self.cardImageLabel.configure(text='', image=img)
			self.cardImageLabel.image = img  # Store a reference to the Image instance, otherwise it gets garbage-collected

	def downloadCardImage(self, setname, cardname):
		# Create these variables outside the try-catch so we can always reference them in the catch
		cardImageUrl = ''
		localImageLocation = ''
		# These are used a few times, no need to repeat the effort
		fixedSetname = self.removeSpecialCharsFromString(setname)
		if 'multiverseid' not in GlobalValues.cards[cardname]['sets'][setname]:
			GlobalValues.statusbar.addMessage(u"Skipping art download for '{}' (no multiverse id)".format(cardname))
			self.cardImageLabel.configure(text='')
			return
		try:
			# Get the first set the card is in
			# TODO: Allow for multiple image sources, like 'api.mtgdb.info'
			cardImageUrl = "http://gatherer.wizards.com/Handlers/Image.ashx?type=card&multiverseid={}".format(GlobalValues.cards[cardname]['sets'][setname]['multiverseid'])

			localImageLocation = self.constructCardImagePath(fixedSetname, cardname)
			# Make sure all the folders exist
			if not os.path.exists(os.path.dirname(localImageLocation)):
				os.makedirs(os.path.dirname(localImageLocation))

			try:
				urllib.urlretrieve(cardImageUrl, localImageLocation)
			except IOError as ioe:
				print u"ERROR occured while trying to download the card '{}' from set '{}':".format(cardname, setname)
				print ioe
				GlobalValues.statusbar.addMessage(u"ERROR occured while downloading art for card '{}' ({})".format(cardname, ioe.message))
				self.cardImageLabel.configure(text='')  # Clear the 'Downloading' message
				return

			# Check if the file downloaded correctly
			with open(localImageLocation, 'r') as imageFile:
				imagefileContents = imageFile.readlines()
			if len(imagefileContents) == 0:
				# Something went wrong (The file starts with an HTML tag instead of binary data)
				#  Show error and remove the file
				print u"ERROR downloading card '{}', online file not found".format(cardImageUrl)
				GlobalValues.statusbar.addMessage(u"Art file for '{}' failed to download properly".format(cardname))
				os.remove(localImageLocation)
				self.cardImageLabel.configure(text='')
			else:
				# Check if the requested card should still be displayed
				if self.currentlyDisplayedSet == setname and self.currentlyDisplayedCard == cardname:
					self.drawCardImage(setname, cardname)
		except Exception as e:
			print "ERROR while fetching card image: ", e
			print u" Card '{}' in set '{}' ('{}')".format(cardname, setname, fixedSetname)
			print u" Url is '{}'; local image location is '{}'".format(cardImageUrl, localImageLocation)
			traceback.print_exc()
			GlobalValues.statusbar.addMessage(u"ERROR while fetching card image for '{}'! ({})".format(cardname, e.message))

	def addCardToList(self, listname):
		GlobalValues.chosenCardsFrame.addCard(self.currentlyDisplayedCard, listname)
		# Deselect the search results list and both the deck and sideboard list, then select the one we need
		GlobalValues.searchResultsFrame.clearSelection()
		GlobalValues.chosenCardsFrame.deckTreeview.clearSelection()
		GlobalValues.chosenCardsFrame.sideboardTreeview.clearSelection()
		GlobalValues.chosenCardsFrame.selectCard(self.currentlyDisplayedCard, listname)

	def increaseCardCount(self, *args):
		GlobalValues.chosenCardsFrame.changeCardCount(self.currentlyDisplayedCard, 1, self.displayType)

	def decreaseCardCount(self, *args):
		GlobalValues.chosenCardsFrame.changeCardCount(self.currentlyDisplayedCard, -1, self.displayType)

	def removeCard(self, *args):
		GlobalValues.chosenCardsFrame.removeCard(self.currentlyDisplayedCard, self.displayType)

	def setDisplayedSet(self, setname):
		if setname != self.currentlyDisplayedSet:
			self.currentlyDisplayedSet = setname
			self.setSelectionCombobox.set(setname)
			self.cardDataFrame.innerFrame.focus_set()  # Move the focus from the combobox to the parent frame, so scrolling doesn't change sets
			self.displayCard(self.currentlyDisplayedCard, setname)