import Tkinter

import GlobalValues
from CardTreeview import CardTreeview


class SearchResultsFrame(Tkinter.Frame):
	def __init__(self, parentframe, width, height):
		# TODO: Double-click card entry to add it to the deck list

		Tkinter.Frame.__init__(self, parentframe, width=width, height=height)

		self.cardcountLabel = Tkinter.Label(self)
		self.cardcountLabel.grid(column=0, row=0)

		self.cardTreeview = CardTreeview(self, width, height, listtype=GlobalValues.DISPLAY_SEARCH)
		self.cardTreeview.grid(column=0, row=1)
		self.updateCardcountLabel()

		# Since the 'count' column is pretty useless, hide it
		columns = tuple(list(self.cardTreeview.columnsOrder)[1:])
		self.cardTreeview.treeview.configure(displaycolumns=columns)

	def updateCardcountLabel(self):
		self.cardcountLabel.configure(text="{:,} cards found".format(len(self.cardTreeview.treeview.get_children())))

	def addCards(self, cardnameList):
		self.cardTreeview.addCards(cardnameList)
		self.updateCardcountLabel()

	def clearCardlist(self):
		self.cardTreeview.clearCardlist()
		self.updateCardcountLabel()

	def clearSelection(self):
		self.cardTreeview.clearSelection()
