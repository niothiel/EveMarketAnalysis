from sqlalchemy import Column, Table, Integer, String
from sqlalchemy.orm import mapper, synonym

from database.static import gamedata_meta
from database.static.gamedata import Unit

groups_table = Table("dgmunits", gamedata_meta,
                     Column("unitID", Integer, primary_key = True),
                     Column("unitName", String),
                     Column("displayName", String))

mapper(Unit, groups_table,
       properties = {"ID" : synonym("unitID"),
                     "name" : synonym("unitName")})
