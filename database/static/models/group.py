from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Table
from sqlalchemy.orm import relation, mapper, synonym, deferred

from database.static import gamedata_meta
from database.static.gamedata import Group, Icon, Category

groups_table = Table("invgroups", gamedata_meta,
                     Column("groupID", Integer, primary_key = True),
                     Column("groupName", String),
                     Column("description", String),
                     Column("published", Boolean),
                     Column("categoryID", Integer, ForeignKey("invcategories.categoryID")),
                     Column("iconID", Integer, ForeignKey("icons.iconID")))

mapper(Group, groups_table,
       properties = {"category" : relation(Category, backref = "groups"),
                     "icon" : relation(Icon),
                     "ID" : synonym("groupID"),
                     "name" : synonym("groupName"),
                     "description" : deferred(groups_table.c.description)})
