import os, sys

import GlobalValues
# Make sure 'import' also searches inside the 'libraries' folder, so those libs don't clutter up the main directory
sys.path.append(os.path.join(GlobalValues.mainfolder, 'libraries'))

from MainApp import MainApp

if __name__ == '__main__':
	GlobalValues.app = MainApp()