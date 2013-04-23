#===============================================================================
# Copyright (C) 2010 Diego Duclos
#
# This file is part of eos.
#
# eos is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# eos is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with eos.  If not, see <http://www.gnu.org/licenses/>.
#===============================================================================

from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Table, Float
from sqlalchemy.orm import relation, mapper, synonym

from eos.db import gamedata_meta
from eos.types import SolarSystem

solarsystems_table = Table("mapsolarsystems", gamedata_meta,
	Column("regionID", Integer),
	Column("constellationID", Integer),
	Column("solarSystemID", Integer, primary_key=True),
	Column("solarSystemName", String),
	Column("security", Float))

mapper(SolarSystem, solarsystems_table,
	properties = {
	"ID" : synonym("solarSystemID"),
	"name" : synonym("solarSystemName")
	})

