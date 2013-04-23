from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Table, Float
from sqlalchemy.orm import relation, mapper

from eos.db import gamedata_meta
from eos.types import ItemMaterial, Item

itemmaterials_table = Table("invtypematerials", gamedata_meta,
	Column("typeID", Integer, ForeignKey("invtypes.typeID"), primary_key=True),
	Column("materialTypeID", Integer, ForeignKey("invtypes.typeID"), primary_key=True),
	Column("quantity", Integer))

mapper(ItemMaterial, itemmaterials_table,
	properties={
		"item": relation(Item, backref='materials', foreign_keys=itemmaterials_table.c.typeID),
	    "requireditem": relation(Item, backref='matrequiredfor', foreign_keys=itemmaterials_table.c.materialTypeID)
	})