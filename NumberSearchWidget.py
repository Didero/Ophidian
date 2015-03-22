import re
import Tkinter, ttk

from SearchWidget import SearchWidget
import GlobalValues


class NumberSearchWidget(SearchWidget):
	searchTerm = None

	def createWidgets(self):
		# First a drop-down to select the range of the search
		self.rangeComboboxValue = Tkinter.StringVar()
		self.rangeCombobox = ttk.Combobox(self, state='readonly', textvariable=self.rangeComboboxValue, width=3,
										  values=['<', '<=', '==', '>=', '>'])
		self.rangeCombobox.current(0)  # Select the first entry
		# Update the search display when this changes, without reparsing the search field
		self.rangeComboboxValue.trace('w', lambda *args: self.widgetmanager.updateSearchDisplay())

		# Then the field to select the number
		self.numberEntryValue = Tkinter.StringVar()
		self.numberEntry = Tkinter.Entry(self, textvariable=self.numberEntryValue)
		self.numberEntryValue.trace('w', self.parseSearchFields)  # Fire on any changes to this entry field

	def parseSearchFields(self, *args):
		self.searchTerm = None
		if self.useRegex:
			self.rangeCombobox.configure(state='disabled')
			if len(self.numberEntryValue.get()) > 0:
				try:
					self.searchTerm = re.compile(self.numberEntryValue.get())
				except re.error:
					self.numberEntry.configure(background='red')
				else:
					self.numberEntry.configure(background='white')
		elif len(self.numberEntryValue.get()) > 0:
			self.rangeCombobox.configure(state='readonly')  # Make sure it's enabled in case a regex toggle disabled it
			try:
				self.searchTerm = float(self.numberEntryValue.get())
			except ValueError:
				self.numberEntry.configure(background='red')
			else:
				self.numberEntry.configure(background='white')
		else:
			# No regex, no entry. Reset the look to the default state, in case people f.i. cleared an errored entry
			self.numberEntry.configure(background='white')
			self.rangeCombobox.configure(state='readonly')
		self.widgetmanager.scheduleSearchDisplayUpdate()

	def place(self, column, row):
		self.placeWidgets(column, row, self.rangeCombobox, self.numberEntry)

	def doesCardMatch(self, cardname):
		if not self.searchTerm:
			return True
		if self.varname not in GlobalValues.cards[cardname]:
			return False

		returnvalue = self.doesNumberMatchSearch(GlobalValues.cards[cardname][self.varname])

		if self.inverseCardMatches:
			returnvalue = not returnvalue
		return returnvalue

	def doesNumberMatchSearch(self, number):
		if self.useRegex:
			if self.searchTerm.search(str(number)):
				return True
			return False
		else:
			rangeOption = self.rangeComboboxValue.get()
			if rangeOption.startswith('<') and number < self.searchTerm:
				return True
			elif rangeOption.startswith('>') and number > self.searchTerm:
				return True
			elif rangeOption.endswith('=') and number == self.searchTerm:
				return True
			return False

	def takeFocus(self):
		self.numberEntry.focus_set()