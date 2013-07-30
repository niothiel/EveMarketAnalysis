CSRF_ENABLED = False

import os.path
import sys

debug = False
gamedataCache = True
saveddataCache = True

DB_USER = 'root'
DB_PASS = 'root'
DB_LOCATION = '10.10.10.240'
DB_NAME = 'emdr'

DB_CONNECTIONSTRING = 'mysql+mysqldb://%s:%s@%s/%s' % (DB_USER, DB_PASS, DB_LOCATION, DB_NAME)

#Autodetect path, only change if the autodetection bugs out.
path = os.path.dirname(unicode(__file__, sys.getfilesystemencoding()))
