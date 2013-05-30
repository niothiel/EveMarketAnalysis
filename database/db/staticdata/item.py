#===============================================================================
# Copyright (C) 2010 Diego Duclos
#
# This file is part of database.
#
# database is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# database is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with database.  If not, see <http://www.gnu.org/licenses/>.
#===============================================================================

from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Table, Float
from sqlalchemy.orm import relation, mapper, synonym, deferred
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm.collections import attribute_mapped_collection

from database.db import gamedata_meta
from database.types import Attribute, Blueprint, Item, MetaType, Group

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
