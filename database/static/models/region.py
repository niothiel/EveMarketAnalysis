from sqlalchemy import Column, String, Integer, Table
from sqlalchemy.orm import mapper, synonym

from database.static import gamedata_meta
from database.static.gamedata import Region

regions_table = Table("mapregions", gamedata_meta,
	Column("regionID", Integer, primary_key = True),
	Column("regionName", String))

mapper(Region, regions_table,
	properties = {
		"ID" : synonym("regionID"),
		"name" : synonym("regionName")
	})
