import Tkinter


class ScrollableFrame(Tkinter.Frame):
	def __init__(self, parentFrame, width, height):
		Tkinter.Frame.__init__(self, parentFrame)

		self.canvasWidth = width
		self.canvasHeight = height

		# For some reason you can't scroll Frames though, so we have to put everything in a Frame in a Canvas
		self.canvas = Tkinter.Canvas(self, width=self.canvasWidth, height=self.canvasHeight, highlightthickness=0)
		self.canvas.grid(column=0, row=0)
		self.scrollbar = Tkinter.Scrollbar(self, command=self.canvas.yview)
		self.scrollbar.grid(column=1, row=0, sticky=Tkinter.NS)
		self.canvas.configure(yscrollcommand=self.scrollbar.set)

		self.innerFrame = Tkinter.Frame(self.canvas, width=self.canvasWidth, height=self.canvasHeight)
		self.innerFrame.grid(column=0, row=0)

		self.canvas.create_window((0, 0), window=self.innerFrame, anchor=Tkinter.NW)
		self.innerFrame.bind('<Configure>', self.onSearchParametersFrameConfigure)

	def onSearchParametersFrameConfigure(self, event):
		"""Keep the canvas properly scrolled when configuring"""
		self.canvas.configure(scrollregion=self.canvas.bbox('all'), width=self.canvasWidth, height=self.canvasHeight)
