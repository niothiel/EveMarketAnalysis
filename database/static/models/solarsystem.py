from sqlalchemy import Column, String, Integer, Table, Float
from sqlalchemy.orm import mapper, synonym

from database.static import gamedata_meta
from database.static.gamedata import SolarSystem

solarsystems_table = Table("mapsolarsystems", gamedata_meta,
	Column("regionID", Integer),
	Column("constellationID", Integer),
	Column("solarSystemID", Integer, primary_key=True),
	Column("solarSystemName", String),
	Column("security", Float))

mapper(SolarSystem, solarsystems_table,
	properties = {
	"ID" : synonym("solarSystemID"),
	"name" : synonym("solarSystemName")
	})

