from sqlalchemy import Column, Table, String
from sqlalchemy.orm import mapper
from database.static.gamedata import MetaData
from database.static import gamedata_meta

metadata_table = Table("metadata", gamedata_meta,
                           Column("fieldName", String, primary_key=True),
                           Column("fieldValue", String))

mapper(MetaData, metadata_table)
