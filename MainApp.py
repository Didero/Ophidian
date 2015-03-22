import json
import os
import Tkinter
import tkMessageBox

import GlobalValues
from Settings import Settings
from CardFileDownloader import CardFileDownloader
from SearchEntryFrame import SearchEntryFrame
from SearchResultsFrame import SearchResultsFrame
from CardDisplayFrame import CardDisplayFrame
from ChosenCardsFrame import ChosenCardsFrame
from Statusbar import Statusbar


class MainApp(object):
	searchWidgets = []

	def __init__(self):
		# TODO: Set up proper logging (with the logging module)
		# TODO: Handle window resizing (distributing extra space to columns, probably the columns with treeviews first
		GlobalValues.root = Tkinter.Tk()

		GlobalValues.root.title("Ophidian - MTG Card Searcher and Deck Builder v0.1.0")
		# 'Ophidian'? It's both the larger snake species, an MTG creature and a D&D snake-like monster
		#  Get it? Snake? Python? Anyway the D&D Ophidian turns creatures it bites into Ophidians, and the
		#   Ophidian MTG creature allows you to draw a card if it attacks unopposed. Both are kind of apt
		#   'Ophidian 2350' is also a separate collectible card game though

		# Intercept the 'window close' event, so we can check if there's stuff like unsaved changes before actually closing
		GlobalValues.root.protocol('WM_DELETE_WINDOW', self.onProgramClose)

		GlobalValues.settings = Settings()

		# Set the global data folder to the one from settings
		GlobalValues.carddatafolder = GlobalValues.settings.getSetting('datafolder', os.path.join(GlobalValues.mainfolder, 'data'))

		# Start with the Status Bar, so other parts can use it right away
		GlobalValues.statusbar = Statusbar(GlobalValues.root)
		GlobalValues.statusbar.grid(column=0, row=5, columnspan=2, sticky=Tkinter.W)

		searchEntryFrame = SearchEntryFrame(GlobalValues.root, width=300, height=250)
		searchEntryFrame.grid(column=0, row=0, sticky=Tkinter.N)

		GlobalValues.searchResultsFrame = SearchResultsFrame(GlobalValues.root, width=300, height=400)
		GlobalValues.searchResultsFrame.grid(column=0, row=1)

		GlobalValues.cardDisplayFrame = CardDisplayFrame(GlobalValues.root, width=500, height=650)
		GlobalValues.cardDisplayFrame.grid(column=1, row=0, rowspan=2, sticky=Tkinter.NW)

		GlobalValues.chosenCardsFrame = ChosenCardsFrame(GlobalValues.root, width=350, height=600)
		GlobalValues.chosenCardsFrame.grid(column=2, row=0, rowspan=2, sticky=Tkinter.NSEW)

		# Add a checkbox to toggle card image downloading and display, but only if we can actually show images
		if GlobalValues.isImageLibraryLoaded:
			self.showImageCheckbuttonValue = Tkinter.IntVar()
			toggleImageDisplayCheckbox = Tkinter.Checkbutton(GlobalValues.root, text="Show Card Images")
			toggleImageDisplayCheckbox.configure(variable=self.showImageCheckbuttonValue, command=self.toggleShowingImages)
			toggleImageDisplayCheckbox.grid(column=2, row=5, sticky=Tkinter.E)
			if GlobalValues.settings.getSetting('showImages', True):
				toggleImageDisplayCheckbox.select()

		# Check if we need to update the card database
		cardFileDownloader = CardFileDownloader(GlobalValues.root)
		updateResult = cardFileDownloader.handleCardFileUpdate(True)

		# Load the cards
		if not os.path.exists(os.path.join(GlobalValues.carddatafolder, 'cards.json')):
			tkMessageBox.showerror("Cardfile not foun", "The card database\ncould not be found\n\nPlease try restarting the program\nand letting the updater run", parent=GlobalValues.root)
			GlobalValues.root.quit()
		else:
			with open(os.path.join(GlobalValues.carddatafolder, 'cards.json'), 'r') as cardfile:
				GlobalValues.cards = json.load(cardfile)

			# Fill out the results list
			GlobalValues.searchResultsFrame.addCards(GlobalValues.cards.keys())

			GlobalValues.root.mainloop()

	def toggleShowingImages(self):
		GlobalValues.settings.setSetting('showImages', True if self.showImageCheckbuttonValue.get() == 1 else False)
		GlobalValues.cardDisplayFrame.toggleShowingImages()

	@staticmethod
	def onProgramClose():
		# Save the settings
		GlobalValues.settings.saveSettings()
		# Let the chosen cards frame ask the user to save, if it has unsaved changes
		GlobalValues.chosenCardsFrame.handleUnsavedChanges()
		# Now do the actual shutdown
		GlobalValues.root.quit()