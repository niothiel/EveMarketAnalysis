from sqlalchemy import Column, Integer, Boolean, ForeignKey, Table, Float
from sqlalchemy.orm import relation, mapper

from database.static import gamedata_meta
from database.static.gamedata import RamType, Item

ramtyperequirements_table = Table("ramtyperequirements", gamedata_meta,
	Column("typeID", Integer, ForeignKey("invtypes.typeID"), primary_key=True),
	Column("activityID", Integer, primary_key=True),
	Column("requiredTypeID", Integer, ForeignKey("invtypes.typeID"), primary_key=True),
	Column("quantity", Integer),
	Column("damagePerJob", Float),
	Column("recycle", Boolean))

mapper(RamType, ramtyperequirements_table,
	properties={
		"item": relation(Item, backref='ramtypes', foreign_keys=ramtyperequirements_table.c.typeID),
	    "requireditem": relation(Item, backref='ramrequiredfor', foreign_keys=ramtyperequirements_table.c.requiredTypeID)
	})