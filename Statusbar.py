import time
import Tkinter


class Statusbar(Tkinter.Frame):
	messageQueue = []
	messageDisplayTime = 3000  # In milliseconds
	messageBacklogCutoff = 6

	label = None
	isUpdateLoopRunning = False

	def __init__(self, parentframe):
		Tkinter.Frame.__init__(self, parentframe)
		self.label = Tkinter.Label(self)
		self.label.grid(column=0, row=0, sticky=Tkinter.W)

	def addMessage(self, message):
		self.messageQueue.append(message)
		# If there's no update loop going right now, set it off
		if not self.isUpdateLoopRunning:
			self.updateDisplayedMessage()

	def updateDisplayedMessage(self):
		messagesLeft = len(self.messageQueue)
		# Nothing left to show, show nothing
		if messagesLeft == 0:
			self.label.configure(text='')
			self.isUpdateLoopRunning = False
		else:
			# If there's too many messages waiting, remove the oldest few
			if messagesLeft > self.messageBacklogCutoff:
				self.messageQueue = self.messageQueue[:self.messageBacklogCutoff]
			# Show the first message in the queue
			self.label.configure(text=self.messageQueue.pop(0))
			# Call this same function again in a while
			self.after(self.messageDisplayTime, self.updateDisplayedMessage)
			self.isUpdateLoopRunning = True