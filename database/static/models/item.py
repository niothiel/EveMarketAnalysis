from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Table, Float
from sqlalchemy.orm import relation, mapper, synonym, deferred
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm.collections import attribute_mapped_collection

from database.static import gamedata_meta
from database.static.gamedata import Attribute, Item, MetaType, Group

items_table = Table("invtypes", gamedata_meta,
                    Column("typeID", Integer, primary_key = True),
                    Column("typeName", String, index=True),
                    Column("description", String),
                    Column("raceID", Integer),
                    Column("volume", Float),
                    Column("mass", Float),
                    Column("capacity", Float),
                    Column("published", Boolean),
                    Column("marketGroupID", Integer, ForeignKey("invmarketgroups.marketGroupID")),
                    #Column("iconID", Integer, ForeignKey("icons.iconID")),
                    Column("groupID", Integer, ForeignKey("invgroups.groupID"), index=True))



from .metaGroup import metatypes_table

mapper(Item, items_table,
       properties = {"group" : relation(Group, backref = "items"),
                     #"icon" : relation(Icon),
                     "_Item__attributes" : relation(Attribute, collection_class = attribute_mapped_collection('name')),
                     "metaGroup" : relation(MetaType,
                                            primaryjoin = metatypes_table.c.typeID == items_table.c.typeID,
                                            uselist = False),
                     "ID" : synonym("typeID"),
                     "name" : synonym("typeName"),
                     "description" : deferred(items_table.c.description)})

Item.category = association_proxy("group", "category")
