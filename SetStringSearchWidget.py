import GlobalValues
from StringSearchWidget import StringSearchWidget


class SetStringSearchWidget(StringSearchWidget):
	def doesCardMatch(self, cardname):
		# If for some reason our search term didn't parse properly, ignore this widget
		if not self.searchTerm:
			return True

		returnvalue = False
		for setdata in GlobalValues.cards[cardname]['sets'].itervalues():
			if self.varname not in setdata:
				continue
			if self.doesStringMatchSearch(setdata[self.varname]):
				returnvalue = True
				break

		if self.inverseCardMatches:
			returnvalue = not returnvalue
		return returnvalue
