from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Table, Float
from sqlalchemy.orm import relation, mapper, synonym

from database.db import gamedata_meta
from database.gamedata import Region

regions_table = Table("mapregions", gamedata_meta,
	Column("regionID", Integer, primary_key = True),
	Column("regionName", String))

mapper(Region, regions_table,
	properties = {
		"ID" : synonym("regionID"),
		"name" : synonym("regionName")
	})
