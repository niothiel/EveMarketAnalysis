import bz2

from sqlalchemy import create_engine, MetaData
import os
import config
from util import downloadFile
from sqlalchemy.orm import sessionmaker

class ReadOnlyException(Exception):
	pass



# Check for the latest static database version.
import urllib2
db_url = urllib2.urlopen('https://raw.github.com/niothiel/EveMarketAnalysis/master/data/latest_db.txt').read()
zipped_filename = db_url.split('/')[-1]
unzipped_filename = zipped_filename[:-4]

db_path = os.path.join(config.path, 'data', unzipped_filename)
"""
if not os.path.exists(db_path):
	print 'Latest database not found!'
	if not os.path.exists('data/' + zipped_filename):
		downloadFile(db_url, 'data/' + zipped_filename)
	print 'Unzipping..'
	zipped_file = bz2.BZ2File('data/' + zipped_filename)
	with open('data/' + unzipped_filename, 'wb') as f:
		while True:
			buffer = zipped_file.read(8192)
			if not buffer:
				break

			f.write(buffer)

	os.remove('data/' + zipped_filename)
"""

staticdata_connectionstring = 'sqlite:///%s?check_same_thread=False' % db_path
staticdata_engine = create_engine(staticdata_connectionstring, echo = config.debug)

gamedata_meta = MetaData()
gamedata_meta.bind = staticdata_engine
gamedata_session = sessionmaker(bind=staticdata_engine, autoflush=False, expire_on_commit=False)()

#Import all the definitions for all our database stuff
from database.static.models import *

#Import queries
from database.static.queries import getItem, searchItems, getVariations, getItemsByCategory, directAttributeRequest, \
									getMarketGroup, getGroup, getCategory, getAttributeInfo, getMetaData, getMetaGroup

print 'Eos DB Initialized.'