import os.path
import sys

debug = False
gamedataCache = True
saveddataCache = True
emdr_db_filename = 'data/emdr.db'

#Autodetect path, only change if the autodetection bugs out.
path = os.path.dirname(unicode(__file__, sys.getfilesystemencoding()))
