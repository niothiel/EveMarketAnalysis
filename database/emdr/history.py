from database.emdr import Base
from sqlalchemy import Column, DateTime, Float, Integer

class History(Base):
	__tablename__ = 'history'
	typeID = Column(Integer, primary_key=True)
	regionID = Column(Integer, primary_key=True)
	generatedAt = Column(DateTime)

	date = Column(DateTime, primary_key=True)       # Date/Time the history was issued
	orders = Column(Integer)                        # Number of orders
	low = Column(Float)                             # Lowest price of the orders
	high = Column(Float)                            # Highest price of the orders
	average = Column(Float)                         # Average price of the orders
	quantity = Column(Integer)                      # Quantity of items in the orders