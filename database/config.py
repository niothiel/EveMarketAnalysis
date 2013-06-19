import os.path
import sys

debug = False
gamedataCache = True
saveddataCache = True

#Autodetect path, only change if the autodetection bugs out.
path = os.path.dirname(unicode(__file__, sys.getfilesystemencoding()))
