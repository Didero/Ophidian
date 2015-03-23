import time
import Tkinter

import GlobalValues
from ScrollableTreeview import ScrollableTreeview


class CardTreeview(ScrollableTreeview):
	cardNamesToDisplay = []
	sortedByColumn = 'name'
	columnsOrder = ('count', 'name', 'cmc', 'type', 'power', 'toughness')
	columnsDisplayData = {'count': {'type': 'number', 'displayname': '#'},
						  'name': {'type': 'text'},
						  'cmc': {'type': 'widenumber', 'displayname': 'CMC'},
						  'type': {'type': 'text'},
						  'power': {'type': 'number', 'displayname': 'P'},
						  'toughness': {'type': 'number', 'displayname': 'T'}}
	columnTypeInfo = {'text': {'width': 160, 'minwidth': 50, 'anchor': Tkinter.W},
					  'number': {'width': 30, 'minwidth': 30, 'anchor': Tkinter.CENTER},
					  'widenumber': {'width': 40, 'minwidth': 30, 'anchor': Tkinter.CENTER}}

	lastSelectionTime = 0
	currentlySelectedCard = None

	def __init__(self, parentFrame, width, height, listtype):
		ScrollableTreeview.__init__(self, parentFrame, width=width, height=height)

		self.listtype = listtype
		self.treeview.configure(selectmode='browse', columns=self.columnsOrder)
		self.treeview['show'] = 'headings'  # Hide the first column
		self.treeview.bind('<<TreeviewSelect>>', self.onCardSelection)  # Display card info when an item is selected
		self.treeview.bind('<Double-1>', self.onDoubleClick)  # This handles a double click on an already selected card, onCardSelection() handles this for unselected cards

		# Set up all the columns properly
		for columnName in self.columnsOrder:
			columnDisplayData = self.columnsDisplayData[columnName]
			displayname = columnDisplayData['displayname'] if 'displayname' in columnDisplayData else columnName.capitalize()
			# On heading click, sort the column by that value. Copy the column name into a local lambda var, otherwise you can only sort by the last column
			self.treeview.heading(columnName, text=displayname, command=lambda col=columnName: self.sortByColumn(col, False))
			self.treeview.column(columnName, **self.columnTypeInfo[columnDisplayData['type']])

	def hasCard(self, cardname):
		return self.treeview.exists(cardname)

	def getCard(self, cardname):
		if self.hasCard(cardname):
			return self.treeview.item(cardname)
		else:
			return None

	def getCardTotal(self):
		return len(self.treeview.get_children())

	def getCardNames(self):
		return self.treeview.get_children()

	def addCard(self, cardname, cardcount=1):
		cardinfo = GlobalValues.cards[cardname]
		columnvalues = [cardcount]
		for column in self.columnsOrder[1:]:
			if column not in cardinfo:
				columnvalues.append('')
			else:
				columnvalues.append(cardinfo[column])
		columnvalues = tuple(columnvalues)
		self.treeview.insert('', 'end', iid=cardname, values=columnvalues)

	def addCards(self, cardnameList):
		for cardname in sorted(cardnameList):
			self.addCard(cardname)

	def clearCardlist(self):
		for child in self.treeview.get_children():
			self.treeview.delete(child)
		self.currentlySelectedCard = None

	def removeCard(self, cardname):
		if self.hasCard(cardname):
			self.treeview.delete(cardname)

	def getCardCount(self, cardname):
		if not self.hasCard(cardname):
			return 0
		return self.getCard(cardname)['values'][0]

	def modifyCardCount(self, cardname, countChange):
		if not self.hasCard(cardname):
			return False
		itemvalues = self.getCard(cardname)['values']
		itemvalues[0] += countChange
		if itemvalues[0] > 0:
			self.treeview.item(cardname, values=itemvalues)
			return True
		else:
			print "Warning: Asked to change card count to value below 0!"
			return False

	def onCardSelection(self, *args):
		selection = self.treeview.selection()
		if len(selection) > 0:
			self.treeview.focus_set()  # Scrolling now moves this treeview
			selection = selection[0]  # The selection is a tuple with one element. Simplify that
			# Check if an unselected card was double-clicked
			if self.listtype == GlobalValues.DISPLAY_SEARCH and self.currentlySelectedCard == selection and time.time() - self.lastSelectionTime <= 0.5:
				GlobalValues.chosenCardsFrame.addCard(selection, GlobalValues.DISPLAY_DECK)
				GlobalValues.chosenCardsFrame.deckTreeview.selectCard(selection)
			else:
				GlobalValues.currentSelection = self.listtype
				GlobalValues.cardDisplayFrame.displayCard(selection)
				# If the clicked list wasn't a search list, clear the search list selection
				if self.listtype != GlobalValues.DISPLAY_SEARCH:
					GlobalValues.searchResultsFrame.clearSelection()
				# The ChosenCards frame handles its own selection changes
				GlobalValues.chosenCardsFrame.setSelectionType(self.listtype)
			# Store selection data for next time
			self.lastSelectionTime = time.time()
			self.currentlySelectedCard = selection

	def onDoubleClick(self, *args):
		if self.listtype == GlobalValues.DISPLAY_SEARCH:
			# Double-clicking an item in the search list should add the card to the deck
			selectedCard = self.treeview.selection()[0]
			GlobalValues.chosenCardsFrame.addCard(selectedCard, GlobalValues.DISPLAY_DECK)
			GlobalValues.chosenCardsFrame.deckTreeview.selectCard(selectedCard)

	def selectCard(self, cardname):
		if self.hasCard(cardname):
			self.treeview.selection_set((cardname,))
			self.treeview.see(cardname)
		else:
			print u"Asked to scroll to '{}' but card not in list!".format(cardname)

	def getSelectedCard(self):
		selection = self.treeview.selection()
		return selection[0] if len(selection) > 0 else None

	def clearSelection(self):
		self.treeview.selection_remove(self.treeview.selection())
		self.currentlySelectedCard = None

	def sortByColumn(self, sortColumn, sortReversed):
		# From here: http://stackoverflow.com/questions/1966929/tk-treeview-column-sort
		# First make a list of all the items and the value of that column
		valuelist = [(self.treeview.set(item, sortColumn), item) for item in self.treeview.get_children()]
		# Numbers need different sorting, otherwise '100' gets sorted above '2'
		if self.columnsDisplayData[sortColumn]['type'] in ('number', 'widenumber'):
			valuelist.sort(reverse=sortReversed, key=lambda v: float(v[0]) if v[0] != '' else '')
		else:
			valuelist.sort(reverse=sortReversed)


		# Now put the items in the treeview in their proper place
		for index, (value, item) in enumerate(valuelist):
			self.treeview.move(item, '', index)

		self.sortedByColumn = sortColumn

		# After the sort, set the column to sort in the other direction next time it's clicked
		self.treeview.heading(sortColumn, command=lambda: self.sortByColumn(sortColumn, not sortReversed))

	def sort(self):
		self.sortByColumn(self.sortedByColumn, False)
