from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Table
from sqlalchemy.orm import relation, mapper, synonym, deferred

from database.db import gamedata_meta
from database.gamedata import Item, MarketGroup, Icon

marketgroups_table = Table("invmarketgroups", gamedata_meta,
                           Column("marketGroupID", Integer, primary_key = True),
                           Column("marketGroupName", String),
                           Column("description", String),
                           Column("hasTypes", Boolean),
                           Column("parentGroupID", Integer, ForeignKey("invmarketgroups.marketGroupID", initially="DEFERRED", deferrable=True)),
                           Column("iconID", Integer, ForeignKey("icons.iconID")))

mapper(MarketGroup, marketgroups_table,
       properties = {"items" : relation(Item, backref = "marketGroup"),
                     "parent" : relation(MarketGroup, backref = "children", remote_side = [marketgroups_table.c.marketGroupID]),
                     "icon" : relation(Icon),
                     "ID" : synonym("marketGroupID"),
                     "name" : synonym("marketGroupName"),
                     "description" : deferred(marketgroups_table.c.description)})
