from sqlalchemy import Table, Column, Integer, ForeignKey, String
from sqlalchemy.orm import relation, mapper, synonym
from database.db import gamedata_meta
from database.db.staticdata.item import items_table
from database.gamedata import MetaGroup, Item, MetaType
from sqlalchemy.ext.associationproxy import association_proxy

metagroups_table = Table("invmetagroups", gamedata_meta,
                         Column("metaGroupID", Integer, primary_key = True),
                         Column("metaGroupName", String))

metatypes_table = Table("invmetatypes", gamedata_meta,
                        Column("typeID", Integer, ForeignKey("invtypes.typeID"), primary_key = True),
                        Column("parentTypeID", Integer, ForeignKey("invtypes.typeID")),
                        Column("metaGroupID", Integer, ForeignKey("invmetagroups.metaGroupID")))

mapper(MetaGroup, metagroups_table,
       properties = {"ID" : synonym("metaGroupID"),
                     "name" : synonym("metaGroupName")})

mapper(MetaType, metatypes_table,
       properties = {"ID" : synonym("metaGroupID"),
                     "parent" : relation(Item, primaryjoin = metatypes_table.c.parentTypeID == items_table.c.typeID),
                     "items" : relation(Item, primaryjoin = metatypes_table.c.typeID == items_table.c.typeID),
                     "info": relation(MetaGroup, lazy=False)})

MetaType.name = association_proxy("info", "name")

