from database.emdr import Base
from sqlalchemy import Boolean, Column, DateTime, Float, Integer

class Order(Base):
	__tablename__ = 'orders'
	orderID = Column(Integer, primary_key=True)     # The order's unique key
	typeID = Column(Integer)
	regionID = Column(Integer)
	generatedAt = Column(DateTime)

	price = Column(Float)                           # Price of the order
	volRemaining = Column(Integer)                  # Remaining volume in the order
	range = Column(Integer)                         # Range the order extends (in jumps)
	volEntered = Column(Integer)                    # Starting volume of the order
	minVolume = Column(Integer)                     # Minimum volume that can be ordered
	bid = Column(Boolean)                           # Whether the order is a bid: True if it's a buy order
	issueDate = Column(DateTime)                    # Date and time that the order was issued
	duration = Column(Integer)                      # The amount of days the order will be active
	stationID = Column(Integer)                     # Station in which the order was placed
	solarSystemID = Column(Integer)                 # Solar system where the order was placed (NULLABLE).