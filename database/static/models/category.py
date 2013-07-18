from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Table
from sqlalchemy.orm import relation, mapper, synonym, deferred

from database.static import gamedata_meta
from database.static.gamedata import Category, Icon

categories_table = Table("invcategories", gamedata_meta,
                         Column("categoryID", Integer, primary_key = True),
                         Column("categoryName", String),
                         Column("description", String),
                         Column("published", Boolean),
                         Column("iconID", Integer, ForeignKey("icons.iconID")))

mapper(Category, categories_table,
       properties = {"icon" : relation(Icon),
                     "ID" : synonym("categoryID"),
                     "name" : synonym("categoryName"),
                     "description" : deferred(categories_table.c.description)})
