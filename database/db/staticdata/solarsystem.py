from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Table, Float
from sqlalchemy.orm import relation, mapper, synonym

from database.db import gamedata_meta
from database.gamedata import SolarSystem

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

