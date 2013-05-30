#===============================================================================
# Copyright (C) 2010 Diego Duclos
#
# This file is part of database.
#
# database is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# database is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with database.  If not, see <http://www.gnu.org/licenses/>.
#===============================================================================

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
from database.db.gamedata import *

#Import queries
from database.db.gamedata.queries import getItem, searchItems, getVariations, getItemsByCategory, directAttributeRequest, \
                                    getMarketGroup, getGroup, getCategory, getAttributeInfo, getMetaData, getMetaGroup

print 'Eos DB Initialized.'