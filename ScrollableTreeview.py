import Tkinter, ttk


class ScrollableTreeview(Tkinter.Frame):
	def __init__(self, parentframe, width, height):
		Tkinter.Frame.__init__(self, parentframe, width=width, height=height)
		# TODO: The treeview doesn't want to take up the full space of the canvas for some reason. Fix that
		# TODO: The last line of the treeview overlaps with the scrollbar. Fix that
		#  Both are (somewhat hackily) fixed by just telling the treeview how many rows it should occupy

		self.width = width
		self.height = height

		self.canvas = Tkinter.Canvas(self, width=self.width, height=self.height, highlightthickness=0)
		self.canvas.grid(column=0, row=0, sticky=Tkinter.NSEW)

		self.treeview = ttk.Treeview(self.canvas)
		self.treeview['height'] = height / 22  # Assuming each row is 20 pixels, and the header row is a bit larger than that, and taking the scrollbar into account
		self.treeview.grid(column=0, row=0, sticky=Tkinter.NSEW)

		self.canvas.create_window((0, 0), window=self.treeview, anchor=Tkinter.NW)
		self.treeview.bind('<Configure>', self.onTreeConfigure)

		# Scrollbars! The vertical scrollbar can manage the tree directly, the horizontal one will move the canvas
		self.verticalScrollbar = Tkinter.Scrollbar(self, orient=Tkinter.VERTICAL, command=self.treeview.yview)
		self.verticalScrollbar.grid(column=1, row=0, sticky=Tkinter.NS)
		self.horizontalScrollbar = Tkinter.Scrollbar(self, orient=Tkinter.HORIZONTAL, command=self.canvas.xview)
		self.horizontalScrollbar.grid(column=0, row=1, sticky=Tkinter.EW)

		# Tell the other stuff to talk to the scrollbars
		self.treeview.configure(yscrollcommand=self.verticalScrollbar.set)
		self.canvas.configure(xscrollcommand=self.horizontalScrollbar.set)

		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(0, weight=1)

	def onTreeConfigure(self, event):
		"""Keep the canvas properly scrolled when configuring"""
		self.canvas.configure(scrollregion=self.canvas.bbox('all'), width=self.width, height=self.height)
