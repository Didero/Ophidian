import json
import os
import Tkinter, ttk
import tkFileDialog
import tkMessageBox
from xml.etree import ElementTree

import GlobalValues
from CardTreeview import CardTreeview


class ChosenCardsFrame(Tkinter.Frame):
	hasUnsavedChanges = False

	def __init__(self, parentframe, width, height):
		Tkinter.Frame.__init__(self, parentframe, width=width, height=height)

		# First add the control buttons (Load, Save)
		self.buttonFrame = Tkinter.Frame(self)
		self.buttonFrame.grid(column=0, row=0)
		self.saveDeckButton = Tkinter.Button(self.buttonFrame, text='Save', command=self.saveDeck)
		self.saveDeckButton.grid(column=0, row=0)
		self.loadDeckButton = Tkinter.Button(self.buttonFrame, text='Load', command=self.loadDeck)
		self.loadDeckButton.grid(column=1, row=0)
		self.clearDeckButton = Tkinter.Button(self.buttonFrame, text='Clear', command=self.clearDeck)
		self.clearDeckButton.grid(column=2, row=0)

		# Then the section where you can fill in data about your deck
		self.deckSettingsFrame = Tkinter.Frame(self)
		self.deckSettingsFrame.grid(column=0, row=1)
		Tkinter.Label(self.deckSettingsFrame, text="Name:").grid(column=0, row=0, sticky=Tkinter.E)
		self.nameEntryField = Tkinter.Entry(self.deckSettingsFrame, width=50)
		self.nameEntryField.grid(column=1, row=0, sticky=Tkinter.W)

		# A treeview with all the cards currently in the deck
		Tkinter.Label(self, text="Deck:").grid(column=0, row=10)
		self.deckTreeview = CardTreeview(self, width, int(height/2.5), GlobalValues.DISPLAY_DECK)
		self.deckTreeview.grid(column=0, row=11)

		self.addButtonsFrame = Tkinter.Frame(self, width=width)

		self.addToDeckButton = Tkinter.Button(self.addButtonsFrame, text="Add To Deck",
											  command=lambda: self.addCard(GlobalValues.cardDisplayFrame.currentlyDisplayedCard, GlobalValues.DISPLAY_DECK))
		self.addToDeckButton.grid(column=0, row=0)
		self.addToSideboardButton = Tkinter.Button(self.addButtonsFrame, text="Add To Sideboard",
												   command=lambda: self.addCard(GlobalValues.cardDisplayFrame.currentlyDisplayedCard, GlobalValues.DISPLAY_SIDEBOARD))
		self.addToSideboardButton.grid(column=1, row=0)

		self.changeCardsButtonFrame = Tkinter.Frame(self, width=width)
		self.increaseCardCountButton = Tkinter.Button(self.changeCardsButtonFrame, text="+",
													  command=lambda: self.changeCardCount(GlobalValues.cardDisplayFrame.currentlyDisplayedCard, 1))
		self.increaseCardCountButton.grid(column=0, row=0)
		self.decreaseCardCountButton = Tkinter.Button(self.changeCardsButtonFrame, text='-', command=lambda: self.changeCardCount(GlobalValues.cardDisplayFrame.currentlyDisplayedCard, -1))
		self.decreaseCardCountButton.grid(column=1, row=0)
		self.removeCardButton = Tkinter.Button(self.changeCardsButtonFrame, text='x', command=self.removeSelectedCard)
		self.removeCardButton.grid(column=2, row=0)
		self.moveCardBetweenListsButton = Tkinter.Button(self.changeCardsButtonFrame, text='v', command=self.moveCardBetweenLists)
		self.moveCardBetweenListsButton.grid(column=3, row=0)

		# TODO: Since neither of the button frames get gridded, the window resizes once one does get added. Think up an elegant solution

		# The sideboard treeview and the stats page share a space, add a tabbed pane for that
		self.sideboardStatsNotebook = ttk.Notebook(self)
		self.sideboardStatsNotebook.grid(column=0, row=20)

		# Sideboard cards display
		self.sideboardTab = Tkinter.Frame(self.sideboardStatsNotebook)
		self.sideboardStatsNotebook.add(self.sideboardTab, text="Sideboard")
		self.sideboardTreeview = CardTreeview(self.sideboardTab, width, int(height/2.5), GlobalValues.DISPLAY_SIDEBOARD)
		self.sideboardTreeview.grid(column=0, row=0)

		# The frame detailing stats for the current deck
		self.deckStatsTab = Tkinter.Frame(self.sideboardStatsNotebook)
		self.sideboardStatsNotebook.add(self.deckStatsTab, text="Deck Stats")
		self.updateDeckStats()

	def handleUnsavedChanges(self):
		# If the current deck has unsaved changes, ask if the user wants to save
		if self.hasUnsavedChanges:
			if tkMessageBox.askyesno("Unsaved changes", "Your current deck\nhas unsaved changes\nDo you want to save your deck?", parent=GlobalValues.root):
				self.saveDeck()

	def setDeckname(self, name):
		self.nameEntryField.delete(0, Tkinter.END)
		self.nameEntryField.insert(0, name)

	def saveDeck(self):
		# First ask for a file location
		targetLocation = tkFileDialog.asksaveasfilename(defaultextension='.odf', confirmoverwrite=True,
														filetypes=[("Ophidian Deck File", '.odf'), ("Plaintext", ".txt")],
														initialdir=GlobalValues.mainfolder, parent=GlobalValues.root,
														title="Save Deck As...")
		# If the user cancelled, stop here
		if len(targetLocation) == 0:
			return
		# Make sure the location exists
		if not os.path.exists(os.path.dirname(targetLocation)):
			os.makedirs(os.path.dirname(targetLocation))

		# If there's already a file there, ask if they want to overwrite it
		#  DISABLED because on Windows 7 the FileDialog itself asks if we want to overwrite
		# TODO: Verify OS's built-in file overwrite works the same in other OSes as it does on Windows
		'''
		if os.path.exists(targetLocation):
			if not tkMessageBox.askyesno("Overwrite?", "File already exists\nOverwrite?", parent=GlobalValues.root):
				return
		'''

		# Build the card dictionary
		# It's built like 'deck: {cardname: count, cardname2: count2, ...}, sideboard: {cardname: count, ...}
		cardDict = {}
		for treeview, key in ((self.deckTreeview, 'deck'), (self.sideboardTreeview, 'sideboard')):
			cardDict[key] = {}
			for itemname in treeview.treeview.get_children():
				cardDict[key][itemname] = treeview.treeview.item(itemname, 'values')[0]

		deckname = self.nameEntryField.get()
		if len(deckname) == 0:
			deckname = None

		saveformat = os.path.splitext(targetLocation)[1]
		saveSuccesful = False
		if saveformat == '.odf':
			if deckname:
				cardDict['deckname'] = deckname
			with open(targetLocation, 'w') as deckfile:
				deckfile.write(json.dumps(cardDict))
			saveSuccesful = True
		elif saveformat == '.txt':
			# This is just a list of all the cards, preceded by cardcount
			# First line is the deckname
			with open(targetLocation, 'w') as deckfile:
				if deckname:
					deckfile.write(deckname + '\n')
				for decktype, prefix in (('deck', ''), ('sideboard', 'SB: ')):
					for cardname, cardcount in cardDict[decktype].iteritems():
						deckfile.write(u"{}{} {}\n".format(prefix, cardcount, GlobalValues.cards[cardname]['name']).encode('utf-8'))
			saveSuccesful = True
		else:
			print "ERROR: Unknown save format '{}'!".format(saveformat)
			tkMessageBox.showwarning("Unknown format", "Sorry, files with the extension\n{}\naren't supported".format(saveformat))

		if saveSuccesful:
			self.hasUnsavedChanges = False
			tkMessageBox.showinfo("Save succesful", "Deck successfully saved!", parent=GlobalValues.root)
		else:
			tkMessageBox.showerror("Save error!", "Something went wrong\nwhen trying to save\n\nSorry!", parent=GlobalValues.root)

	def loadDeck(self, *args):
		# If the current deck has unsaved changes, ask if the user wants to save
		self.handleUnsavedChanges()

		# First ask for a file location
		deckfilename = tkFileDialog.askopenfilename(defaultextension='.odf', multiple=False,
														filetypes=[("Ophidian Deck File", '.odf'),
																   ("Plaintext", '.txt'), ("MTG Client", '.dec'), ("Magic Workstation", '.mwDeck'),
																   ("Cockatrice deck", '.cod')],
														initialdir=GlobalValues.mainfolder, parent=GlobalValues.root,
														title="Load Deck")
		# If the user cancelled, the deckfilename is '', check for that
		if len(deckfilename) == 0:
			return

		# Clear out any cards that may have been there previously
		self.clearDeck()

		saveformat = os.path.splitext(deckfilename)[1]
		loadWasSuccessful = False
		if saveformat == '.odf':
			# A dictionary with a 'deck' and 'sideboard' key, each with a dict, cardname as key and count as value
			with open(deckfilename, 'r') as deckfile:
				try:
					deck = json.load(deckfile)
				except ValueError:
					tkMessageBox.showerror("Invalid deck file", "The specified file\n{}\nis not a valid deck file", parent=GlobalValues.root)
					return
			if 'deckname' in deck:
				self.setDeckname(deck['deckname'])
			for listtype in ('deck', 'sideboard'):
				if listtype not in deck:
					print "WARNING: '{}' key not found in loaded file".format(listtype)
					GlobalValues.statusbar.addMessage("Error while loading deckfile '{}': key '{}' not found!".format(os.path.basename(deckfilename), listtype))
					continue
				treeview = self.deckTreeview if listtype == 'deck' else self.sideboardTreeview
				for cardname, count in deck[listtype].iteritems():
					treeview.addCard(cardname, max(count, 1))
			loadWasSuccessful = True
		elif saveformat in ('.txt', '.dec', '.mwDeck'):
			# Just a list of all the cards, preceded by cardcount.
			with open(deckfilename, 'r') as deckfile:
				# First line may be the deckname, check for that
				firstline = deckfile.readline().strip().decode('utf-8')
				try:
					if firstline.startswith('SB: '):
						raise ValueError
					int(firstline.split(' ')[0])
				except ValueError:
					if firstline.startswith('//'):
						firstline = firstline[2:]
					firstline = firstline.replace('Name:', '').strip()
					# file starts with a title, fill that in
					self.setDeckname(firstline)
				else:
					# Since we didn't find a title, the first line is already a card. Return to the start of the file to parse that line properly
					deckfile.seek(0)
				for line in deckfile:
					line = line.strip()
					if line.startswith('//') or len(line) == 0:
						continue
					linetype = 'deck'
					lineparts = line.decode('utf-8').split(' ')
					if lineparts[0] == 'SB:':
						linetype = 'sideboard'
						# Remove the 'SB' part
						lineparts = lineparts[1:]
					# Some programs add the set the card is from, in brackets between the count and the name. Remove that
					# TODO: Allow set selection for cards added to a deck, if people prefer that art and/or flavor text
					if lineparts[1].startswith('[') and lineparts[1].endswith(']'):
						lineparts.pop(1)
					# Sometimes they have a bracketed number suffix to indicate the specific art version in the set. Remove that too
					if lineparts[-1].startswith('(') and lineparts[-1].endswith(')') and len(lineparts[-1]) in (3, 4):
						lineparts = lineparts[:-1]
					treeview = self.deckTreeview if linetype == 'deck' else self.sideboardTreeview
					cardname = u" ".join(lineparts[1:]).lower()
					if cardname not in GlobalValues.cards:
						print u"ERROR: Unknown card '{}' in deck file '{}'".format(cardname, deckfilename)
						GlobalValues.statusbar.addMessage(u"WARNING: Deckfile contains unknown card '{}'".format(cardname))
					else:
						treeview.addCard(cardname, int(lineparts[0]))
			loadWasSuccessful = True
		elif saveformat == '.cod':
			# Cockatrice save format
			# It's XML, with two <zone>s inside a <cockatrice_deck>. One <zone> has name=main, the other name=side
			tree = ElementTree.parse(deckfilename).getroot()
			for child in tree:
				if child.tag == 'deckname':
					if len(child.text) > 0:
						self.setDeckname(child.text)
				elif child.tag == 'comments':
					continue
				elif child.tag == 'zone':
					if child.get('name') == 'main':
						treeview = self.deckTreeview
					elif child.get('name') == 'side':
						treeview = self.sideboardTreeview
					else:
						GlobalValues.statusbar.addMessage(u"Unknown zone '{}' in deckfile".format(child.get('name')))
						continue
					# The actual list with cards
					for cardElement in child:
						amount = int(cardElement.get('number'))
						name = cardElement.get('name').lower()
						if name not in GlobalValues.cards:
							GlobalValues.statusbar.addMessage(u"Cockatrice deckfile contains unknown card '{}'".format(name))
							continue
						treeview.addCard(name, amount)
				else:
					GlobalValues.statusbar.addMessage(u"Unknown tag '{}' found in deckfile!".format(child.tag))
			loadWasSuccessful = True
		else:
			tkMessageBox.showerror("Unknown Format", u"The file\n'{}'\n can't be opened,\nunknown format\n'{}'".format(os.path.basename(deckfilename), saveformat), parent=GlobalValues.root)

		if loadWasSuccessful:
			self.hasUnsavedChanges = False
			self.updateDeckStats()
			self.deckTreeview.sort()
			self.sideboardTreeview.sort()

	def clearDeck(self):
		self.handleUnsavedChanges()
		self.deckTreeview.clearCardlist()
		self.sideboardTreeview.clearCardlist()
		self.setDeckname('')
		self.hasUnsavedChanges = False

	def addCard(self, cardname, listtype=GlobalValues.DISPLAY_DECK):
		treeview = self.deckTreeview if listtype == GlobalValues.DISPLAY_DECK else self.sideboardTreeview
		if not treeview.hasCard(cardname):
			treeview.addCard(cardname, 1)
		else:
			self.changeCardCount(cardname, 1, listtype)
		treeview.selectCard(cardname)
		self.hasUnsavedChanges = True
		self.updateDeckStats()

	def removeCard(self, cardname, listtype=None):
		if not listtype:
			listtype = GlobalValues.currentSelection
		treeview = self.deckTreeview if listtype == GlobalValues.DISPLAY_DECK else self.sideboardTreeview
		treeview.removeCard(cardname)
		self.changeCardsButtonFrame.grid_remove()
		self.hasUnsavedChanges = True
		self.updateDeckStats()

	def removeSelectedCard(self):
		treeview = self.deckTreeview if GlobalValues.currentSelection == GlobalValues.DISPLAY_DECK else self.sideboardTreeview
		self.removeCard(treeview.getSelectedCard(), GlobalValues.currentSelection)

	def changeCardCount(self, cardname, changeAmount=0, treeviewType=None):
		if not treeviewType:
			treeviewType = GlobalValues.currentSelection
		treeview = self.deckTreeview if treeviewType == GlobalValues.DISPLAY_DECK else self.sideboardTreeview
		if not treeview.hasCard(cardname):
			print u"Asked to increase count for '{}' but card not in list!".format(cardname)
			GlobalValues.statusbar.addMessage("Can't reduce card count below 1 (Use the X button to remove the card)")
		else:
			treeview.modifyCardCount(cardname, changeAmount)
		self.hasUnsavedChanges = True
		self.updateDeckStats()

	def moveCardBetweenLists(self):
		if GlobalValues.currentSelection == GlobalValues.DISPLAY_SEARCH:
			print "WARNING: Asked to move card, but the SearchResults treeview is active"
			return
		sourceTreeview = self.deckTreeview if GlobalValues.currentSelection == GlobalValues.DISPLAY_DECK else self.sideboardTreeview
		targetTreeview = self.sideboardTreeview if sourceTreeview == self.deckTreeview else self.deckTreeview
		# Move card from deck to sideboard
		cardname = sourceTreeview.getSelectedCard()
		cardcount = sourceTreeview.getCardCount(cardname)  # We need the card count, so we can switch that over too
		sourceTreeview.removeCard(cardname)
		targetTreeview.addCard(cardname, cardcount)
		targetTreeview.selectCard(cardname)

	def setSelectionType(self, selectionType):
		self.addButtonsFrame.grid_remove()
		self.changeCardsButtonFrame.grid_remove()
		if selectionType == GlobalValues.DISPLAY_SEARCH:
			# Clear any selections we may have had
			self.deckTreeview.clearSelection()
			self.sideboardTreeview.clearSelection()
			# Activate the 'Add card to...' buttons
			self.addButtonsFrame.grid(column=0, row=15)
		elif selectionType == GlobalValues.DISPLAY_DECK or selectionType == GlobalValues.DISPLAY_SIDEBOARD:
			# Show the buttons to change card count
			self.changeCardsButtonFrame.grid(column=0, row=15)
			# Clear the selection in the appropriate treeview
			if selectionType == GlobalValues.DISPLAY_DECK:
				self.sideboardTreeview.clearSelection()
				# Make the 'move' button point from the deck to the sideboard
				self.moveCardBetweenListsButton.configure(text="v")
			elif selectionType == GlobalValues.DISPLAY_SIDEBOARD:
				self.deckTreeview.clearSelection()
				# Make the 'move' button point from the sideboard to the deck
				self.moveCardBetweenListsButton.configure(text='^')

	def updateDeckStats(self):
		# First clear the existing stats
		for widget in self.deckStatsTab.winfo_children():
			widget.destroy()

		# Then rebuild the stats display
		decksize = self.deckTreeview.getCardTotal()
		typecount = {'Artifact': 0, 'Creature': 0, 'Enchantment': 0, 'Instant': 0, 'Land': 0, 'Misc.': 0, 'Sorcery': 0}
		colorcounts = {'Blue': 0, 'Black': 0, 'Green': 0, 'Red': 0, 'White': 0, 'Colorless': 0}
		totalColors = 0  # Different from just the card count, since there's f.i. R G creatures
		cummulativeManacount = {}
		cardsWithManaCostCount = 0
		highestManaCost = -1

		for cardname in self.deckTreeview.getCardNames():
			card = GlobalValues.cards[cardname]
			cardcount = self.deckTreeview.getCard(cardname)['values'][0]
			isListedType = False
			for field in typecount:
				if field in card['types']:
					typecount[field] += cardcount
					isListedType = True
			if not isListedType:
				typecount['Misc.'] += cardcount
			if 'colors' in card:
				for field in colorcounts:
					if field in card['colors']:
						colorcounts[field] += cardcount
						totalColors += cardcount
			if 'cmc' in card:
				if card['cmc'] not in cummulativeManacount:
					cummulativeManacount[card['cmc']] = cardcount
				else:
					cummulativeManacount[card['cmc']] += cardcount
				cardsWithManaCostCount += cardcount
				if card['cmc'] > highestManaCost:
					highestManaCost = card['cmc']

		# Put card totals in the last row of both the type and color list
		Tkinter.Label(self.deckStatsTab, text="TOTAL:").grid(column=0, row=0)
		for column in (1, 5):
			Tkinter.Label(self.deckStatsTab, text="{:,}".format(decksize)).grid(column=column, row=0)

		# List the collected data
		for countdict, total, columnoffset in ((typecount, decksize, 0), (colorcounts, totalColors, 4)):
			for i, field in enumerate(sorted(countdict)):
				count = countdict[field]
				# What this row is
				Tkinter.Label(self.deckStatsTab, text=field).grid(column=columnoffset, row=i+1)
				# How many cards of this type
				Tkinter.Label(self.deckStatsTab, text="{:,}".format(count)).grid(column=columnoffset+1, row=i+1, padx=10)
				# Which percentage that is of the total deck size
				Tkinter.Label(self.deckStatsTab, text="{:,.1f} %".format(100.0 * count / max(1, total))).grid(column=columnoffset+2, row=i+1, padx=10)

		# Show a mana curve (sorted so it's from low to high
		Tkinter.Label(self.deckStatsTab).grid(column=0, row=20, pady=10)
		Tkinter.Label(self.deckStatsTab, text="CMC").grid(column=0, row=21)
		Tkinter.Label(self.deckStatsTab, text="count").grid(column=0, row=22)
		Tkinter.Label(self.deckStatsTab, text="% of deck").grid(column=0, row=23)
		for i, cmc in enumerate(sorted(cummulativeManacount)):
			percentage = 100.0 * cummulativeManacount[cmc] / cardsWithManaCostCount
			Tkinter.Label(self.deckStatsTab, text=cmc).grid(column=i+1, row=21)
			Tkinter.Label(self.deckStatsTab, text=cummulativeManacount[cmc]).grid(column=i+1, row=22)
			Tkinter.Label(self.deckStatsTab, text="{:.1f}".format(percentage)).grid(column=i+1, row=23)