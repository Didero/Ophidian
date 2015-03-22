import os
import sys

isImageLibraryLoaded = False

mainfolder = os.path.dirname(os.path.abspath(sys.argv[0]))  # The first argument is always the location the script is run from. This also works when compiled to .exe
carddatafolder = os.path.join(mainfolder, 'data')

app = None
root = None
settings = None
statusbar = None
searchResultsFrame = None
cardDisplayFrame = None
chosenCardsFrame = None

cards = {}

# Constants to make it easier to tell different parts of the program which part is selected
DISPLAY_SEARCH = 0
DISPLAY_DECK = 1
DISPLAY_SIDEBOARD = 2
currentSelection = DISPLAY_SEARCH
