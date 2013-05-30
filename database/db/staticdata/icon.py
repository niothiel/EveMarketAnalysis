from sqlalchemy import Column, String, Integer, Table
from sqlalchemy.orm import mapper, synonym, deferred

from database.db import gamedata_meta
from database.gamedata import Icon

icons_table = Table("icons", gamedata_meta,
                    Column("iconID", Integer, primary_key = True),
                    Column("description", String),
                    Column("iconFile", String))

mapper(Icon, icons_table,
       properties = {"ID" : synonym("iconID"),
                     "description" : deferred(icons_table.c.description)})
