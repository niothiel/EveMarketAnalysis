import os.path
import sys

debug = False
gamedataCache = True
saveddataCache = True
gamedata_connectionstring = 'sqlite:///data/eve.db?check_same_thread=False'

#Autodetect path, only change if the autodetection bugs out.
path = os.path.dirname(unicode(__file__, sys.getfilesystemencoding()))
