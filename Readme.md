# Ophidian
A Magic: The Gathering deck builder made with Python and Tkinter

## How To Use
If you downloaded a Release, it should have an executable file. Just run that.
To run from sourcecode, make sure you have the latest version of Python 2 installed, and run 'start.py'.
Regardless, put Ophidian in a place where it can write files to disk, because it will download a data file to its location, and card images if that's enabled and possible (see Requirements).

## Requirements
Most of Ophidian uses standard Python 2.7 modules.
The only exception is the displaying of card art, that requires PIL (or Pillow). If Ophidian can't find PIL, it will still run, but it will show a warning and skip downloading and showing card images.

## Credits
Wizards Of The Coast: Of course without their captivating card game, none of this would have happened.
MTGjson.com: Without this easy-to-use card information source, I wouldn't even have considered starting this project.
Mara: For advice and testing. And motivation!

Google and StackOverflow: I don't think I'd be able to code without the two of you.