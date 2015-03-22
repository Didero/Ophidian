import re
import Tkinter, ttk

from SearchWidget import SearchWidget
import GlobalValues


class StringSearchWidget(SearchWidget):
	searchTerm = None

	def createWidgets(self):
		# First a drop-down to select the type of the search ('Contains', 'Starts with', etc)
		self.searchtypeChooserValue = Tkinter.StringVar()
		self.searchtypeChooser = ttk.Combobox(self, state='readonly', textvariable=self.searchtypeChooserValue, width=8,
										  values=['Contains', 'Starts With', 'Ends With', 'Equals'])
		self.searchtypeChooser.current(0)  # Select the first entry
		# Update the search display when this changes, without reparsing the search field
		self.searchtypeChooserValue.trace('w', lambda *args: self.widgetmanager.updateSearchDisplay())

		self.entryfieldValue = Tkinter.StringVar()
		self.entryfield = Tkinter.Entry(self, textvariable=self.entryfieldValue, width=15)
		self.entryfieldValue.trace('w', self.parseSearchFields)

	def place(self, startcolumn, startrow):
		self.placeWidgets(startcolumn, startrow, self.searchtypeChooser, self.entryfield)

	def parseSearchFields(self, *args):
		self.searchTerm = None
		if self.useRegex:
			self.searchtypeChooser.configure(state='disabled')  # Regexes don't use the searchtype selection
			if len(self.entryfieldValue.get()) > 0:
				try:
					self.searchTerm = re.compile(self.entryfieldValue.get(), re.IGNORECASE)
				except re.error:
					self.searchTerm = None
					self.entryfield.configure(background="red")
				else:
					self.entryfield.configure(background="white")
		else:
			self.searchtypeChooser.configure(state='readonly')  # Normal searches need the searchtype selection
			self.searchTerm = self.entryfieldValue.get().lower()
			# If the searchfield is empty, don't have it do any searches
			if len(self.searchTerm) == 0:
				self.searchTerm = None
		self.widgetmanager.scheduleSearchDisplayUpdate()

	def doesCardMatch(self, cardname):
		# If for some reason our search term didn't parse properly, ignore this widget
		if not self.searchTerm:
			return True
		card = GlobalValues.cards[cardname]
		if self.varname not in card:
			return False

		returnvalue = self.doesStringMatchSearch(card[self.varname])

		if self.inverseCardMatches:
			returnvalue = not returnvalue
		return returnvalue

	def doesStringMatchSearch(self, s):
		if self.useRegex:
			if self.searchTerm.search(s):
				return True
			else:
				return False
		searchtype = self.searchtypeChooserValue.get()
		if searchtype == 'Contains' and self.searchTerm in s.lower():
			return True
		elif searchtype == 'Starts With' and s.lower().startswith(self.searchTerm):
			return True
		elif searchtype == 'Ends With' and s.lower().endswith(self.searchTerm):
			return True
		elif searchtype == 'Equals' and s.lower() == self.searchTerm:
			return True
		return False

	def takeFocus(self):
		self.entryfield.focus_set()