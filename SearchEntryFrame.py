import Tkinter, ttk

import GlobalValues
from ScrollableFrame import ScrollableFrame
from StringSearchWidget import StringSearchWidget
from NumberSearchWidget import NumberSearchWidget
from SetnameSearchWidget import SetnameSearchWidget
from SetStringSearchWidget import SetStringSearchWidget
from SetNumberSearchWidget import SetNumberSearchWidget


class SearchEntryFrame(Tkinter.Frame):
	# TODO: Group search fields for the same variable, add option to choose to OR or AND them
	# TODO: Allow saving of search layout, so if somebody always wants, say, 3 CMC fields, they don't have to add those each time, but just load their preset
	# TODO: Create a Combobox Search Widget, which gets a list of options to choose from (f.i. the Color field only has 5 options, a text search doesn't make sense)
	#	Fields for which this makes sense: Color, Type (perhaps, build list from availabe types?), Layout, Rarity, Set?,
	# TODO: Think up a dictionary search widget, to search for format legalities
	searchWidgets = []
	nameToType = {'Artist': SetStringSearchWidget, 'CMC': NumberSearchWidget, 'Colors': StringSearchWidget, 'Flavor': SetStringSearchWidget,
				  'Layout': StringSearchWidget, 'Loyalty': NumberSearchWidget, 'Manacost': StringSearchWidget, 'Number': SetStringSearchWidget, 'MultiverseID': SetNumberSearchWidget, 'Name': StringSearchWidget,
				  'Power': NumberSearchWidget, 'Rarity': SetStringSearchWidget, 'Set': SetnameSearchWidget,
				  'Text': StringSearchWidget, 'Toughness': NumberSearchWidget, 'Type': StringSearchWidget, 'Watermark': StringSearchWidget}
	updateFunctionId = None

	def __init__(self, parentFrame, width, height):
		Tkinter.Frame.__init__(self, parentFrame, width=width, height=height)

		optionsFrame = Tkinter.Frame(self, height=50)
		optionsFrame.grid(column=0, row=0)

		# Add a drop-down box to add more searches
		self.addSearchWidgetFrame = Tkinter.Frame(optionsFrame)
		Tkinter.Label(self.addSearchWidgetFrame, text="Add search field:").grid(column=0, row=0)
		self.addSearchWidgetComboboxValue = Tkinter.StringVar()
		addSearchWidgetCombobox = ttk.Combobox(self.addSearchWidgetFrame, state='readonly', values=sorted(self.nameToType.keys()), textvariable=self.addSearchWidgetComboboxValue)
		addSearchWidgetCombobox.grid(column=1, row=0)
		self.addSearchWidgetFrame.grid(column=0, row=0, sticky=Tkinter.E)
		# React when an option is chosen
		addSearchWidgetCombobox.bind('<<ComboboxSelected>>', lambda *args: self.addSearchWidget(self.addSearchWidgetComboboxValue.get()))

		self.searchParametersFrame = ScrollableFrame(self, width=width, height=height-50)
		self.searchParametersFrame.grid(column=0, row=1)

		# Start out with the most common search fields already shown
		for field in ('Name', 'CMC', 'Text'):
			self.addSearchWidget(field, False)
		# Give the first widget created the focus, since that makes the most sense
		self.searchWidgets[0].takeFocus()

	def addSearchWidget(self, fieldname, haveWidgetTakeFocus=True):
		widgetCount = len(self.searchWidgets)

		# Don't keep the list at the selected widget, but reset it to the top to make it ready for re-use
		self.addSearchWidgetComboboxValue.set('')

		# Create the new widget and place it
		widget = self.nameToType[fieldname](self, self.searchParametersFrame.innerFrame, fieldname)
		self.searchWidgets.append(widget)
		widget.grid(column=0, row=widgetCount + 1, columnspan=2, sticky=Tkinter.W)
		# Put the cursor in the new widget, so it can immediately be used.
		#    Also fixes the 'ComboSelected' event firing when scrolling, spamming widgets
		if haveWidgetTakeFocus:
			widget.takeFocus()

	def removeWidget(self, widget):
		# Remove it from the list
		index = self.searchWidgets.index(widget)
		del self.searchWidgets[index]
		# And move all the following widgets (if any) up a row
		if len(self.searchWidgets) > index:
			for widgetIndex in xrange(index, len(self.searchWidgets)):
				self.searchWidgets[widgetIndex].grid_remove()
				self.searchWidgets[widgetIndex].grid(column=0, row=widgetIndex + 1)
		self.updateSearchDisplay()

	def updateSearchDisplay(self):
		GlobalValues.searchResultsFrame.clearCardlist()
		matchingCardnames = []
		for cardname in GlobalValues.cards.keys():
			addCard = True
			for widget in self.searchWidgets:
				if not widget.doesCardMatch(cardname):
					addCard = False
					break
			if addCard:
				matchingCardnames.append(cardname)
		GlobalValues.searchResultsFrame.addCards(matchingCardnames)

	def scheduleSearchDisplayUpdate(self):
		if self.updateFunctionId:
			self.after_cancel(self.updateFunctionId)
		self.updateFunctionId = self.after(250, self.updateSearchDisplay)