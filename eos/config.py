import os.path
import sys

debug = False
gamedataCache = True
saveddataCache = True
#gamedata_connectionstring = 'sqlite:////D:/Dropbox/Programming/EveMarketAnalysis/data/eve.db'
gamedata_connectionstring = 'sqlite:///data/eve.db?check_same_thread=False'
#gamedata_connectionstring = 'mysql+mysqldb://root:asdf@127.0.0.1/evestatic'

#Autodetect path, only change if the autodetection bugs out.
path = os.path.dirname(unicode(__file__, sys.getfilesystemencoding()))
