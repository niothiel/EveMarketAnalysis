from sqlalchemy import Column, Integer, ForeignKey, Table
from sqlalchemy.orm import relation, mapper

from database.static import gamedata_meta
from database.static.gamedata import ItemMaterial, Item

itemmaterials_table = Table("invtypematerials", gamedata_meta,
	Column("typeID", Integer, ForeignKey("invtypes.typeID"), primary_key=True),
	Column("materialTypeID", Integer, ForeignKey("invtypes.typeID"), primary_key=True),
	Column("quantity", Integer))

mapper(ItemMaterial, itemmaterials_table,
	properties={
		"item": relation(Item, backref='materials', foreign_keys=itemmaterials_table.c.typeID),
	    "requireditem": relation(Item, backref='matrequiredfor', foreign_keys=itemmaterials_table.c.materialTypeID)
	})