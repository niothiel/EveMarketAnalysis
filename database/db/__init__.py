import threading

from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import sessionmaker

from database import config

class ReadOnlyException(Exception):
    pass

gamedata_connectionstring = config.gamedata_connectionstring
gamedata_engine = create_engine(gamedata_connectionstring, echo = config.debug)

gamedata_meta = MetaData()
gamedata_meta.bind = gamedata_engine
gamedata_session = sessionmaker(bind=gamedata_engine, autoflush=False, expire_on_commit=False)()

#Import all the definitions for all our database stuff
from database.db.staticdata import *

#Import queries
from database.db.staticdata.queries import getItem, searchItems, getVariations, getItemsByCategory, directAttributeRequest, \
                                    getMarketGroup, getGroup, getCategory, getAttributeInfo, getMetaData, getMetaGroup

print 'Eos DB Initialized.'