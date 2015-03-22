import GlobalValues
from StringSearchWidget import StringSearchWidget


class SetnameSearchWidget(StringSearchWidget):
	def doesCardMatch(self, cardname):
		# If for some reason our search term didn't parse properly, ignore this widget
		if not self.searchTerm:
			return True

		returnvalue = False
		for setname in GlobalValues.cards[cardname]['sets']:
			if self.doesStringMatchSearch(setname):
				returnvalue = True
				break

		if self.inverseCardMatches:
			returnvalue = not returnvalue
		return returnvalue

