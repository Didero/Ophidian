import Tkinter


class SearchWidget(Tkinter.Frame):
	useRegex = False
	inverseCardMatches = False

	def __init__(self, widgetmanager, parentframe, displayname, variablename=None):
		Tkinter.Frame.__init__(self, parentframe)

		self.widgetmanager = widgetmanager
		self.parentframe = parentframe
		self.varname = variablename if variablename is not None else displayname.lower()

		# Standard control buttons that every search needs. Set padding to 1, to prevent them taking up far too much space on Linux
		# Create a button to remove this search
		self.destroyButton = Tkinter.Button(self, text='X', command=self.destroyWidget, padx=1)
		# A button to toggle whether the search is regex or not
		self.toggleRegexButton = Tkinter.Button(self, text='R', command=self.toggleRegex, padx=1)
		# And a button to toggle whether this search is a positive or negative search (include hits or exclude them)
		self.toggleInverseMatchesButton = Tkinter.Button(self, text='not', command=self.toggleInverseMatches, padx=1)
		# Create the label, so users know what the widget is for
		self.label = Tkinter.Label(self, text=displayname + ': ')

		self.createWidgets()

		# Finally actually place all the items into the frame
		self._place()

	def toggleRegex(self):
		self.useRegex = not self.useRegex
		# Make the button look pushed down if regex is on, and up when it isn't
		if self.useRegex:
			self.toggleRegexButton.configure(relief=Tkinter.SUNKEN)
		else:
			self.toggleRegexButton.configure(relief=Tkinter.RAISED)
		self.parseSearchFields()

	def parseSearchFields(self):
		pass

	def createWidgets(self):
		pass

	def _place(self):
		# Always place the label
		self.destroyButton.grid_remove()
		self.destroyButton.grid(column=0, row=0, sticky=Tkinter.W)
		self.toggleRegexButton.grid_remove()
		self.toggleRegexButton.grid(column=1, row=0, sticky=Tkinter.W)
		self.toggleInverseMatchesButton.grid_remove()
		self.toggleInverseMatchesButton.grid(column=2, row=0, sticky=Tkinter.W)
		self.label.grid_remove()
		self.label.grid(column=3, row=0, sticky=Tkinter.E)
		# Allow implementations to place their own widgets
		self.place(4, 0)

	def place(self, column, row):
		pass

	@staticmethod
	def placeWidgets(column, row, *widgets):
		for widget in widgets:
			widget.grid_forget()
			widget.grid(column=column, row=row)
			column += 1

	def destroyWidget(self, *args):
		self.widgetmanager.removeWidget(self)
		self.destroy()

	def toggleInverseMatches(self, *args):
		self.inverseCardMatches = not self.inverseCardMatches
		if self.inverseCardMatches:
			self.toggleInverseMatchesButton.configure(relief=Tkinter.SUNKEN)
		else:
			self.toggleInverseMatchesButton.configure(relief=Tkinter.RAISED)
		self.widgetmanager.updateSearchDisplay()

	def doesCardMatch(self, cardname):
		pass

	def takeFocus(self):
		pass