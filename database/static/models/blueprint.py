from sqlalchemy import Column, Integer, ForeignKey, Table
from sqlalchemy.orm import relation, mapper, backref

from database.static import gamedata_meta
from database.static.gamedata import Blueprint, Item

blueprints_table = Table("invblueprinttypes", gamedata_meta,
	Column("blueprintTypeID", Integer, ForeignKey("invtypes.typeID"), primary_key = True),
	Column("parentBlueprintTypeID", Integer, ForeignKey("invtypes.typeID")),
	Column("productTypeID", Integer, ForeignKey("invtypes.typeID")),
	Column("productionTime", Integer),
	Column("techLevel", Integer),
	Column("researchProductivityTime", Integer),
	Column("researchMaterialTime", Integer),
	Column("researchCopyTime", Integer),
	Column("researchTechTime", Integer),
	Column("productivityModifier", Integer),
	Column("materialModifier", Integer),
	Column("wasteFactor", Integer),
	Column("maxProductionLimit", Integer))


mapper(Blueprint, blueprints_table,
	properties = {"item": relation(Item, backref = backref('blueprint', uselist=False), foreign_keys=blueprints_table.c.productTypeID),
	              "parent": relation(Item, foreign_keys=blueprints_table.c.parentBlueprintTypeID),
	              "product": relation(Item, foreign_keys=blueprints_table.c.productTypeID)})