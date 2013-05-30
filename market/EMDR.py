import zlib
import zmq
import json
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from util import parse_isodate

db = create_engine('sqlite:///emdr.db', echo=False)
session = sessionmaker(bind=db)()

Base = declarative_base()

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

def processOrdersPacket(market_data):
	for rowset in market_data['rowsets']:
		for row in rowset['rows']:
			order = Order()
			order.typeID = rowset['typeID']
			order.regionID = rowset['regionID']
			order.generatedAt = parse_isodate(rowset['generatedAt'])

			vals = zip(market_data['columns'], row)
			for k, v in vals:
				setattr(order, k, v)

			order.issueDate = parse_isodate(order.issueDate)
			stored_order = None
			# If there is no order with that id, just add it to DB.
			try:
				stored_order = session.query(Order).filter(Order.orderID==order.orderID).one()
			except:
				session.add(order)
				return

			# If there is, check the dates of the one in the database vs the ones we have now and update.
			if stored_order.generatedAt < order.generatedAt:
				order = session.merge(order)
				session.add(order)

def processHistoryPacket(market_data):
	for rowset in market_data['rowsets']:
		for row in rowset:
			history = History()
			history.typeID = rowset['typeID']
			history.regionID = rowset['regionID']
			history.generatedAt = parse_isodate(rowset['generatedAt'])

			vals = zip(market_data['columns'], row)
			for k, v in vals:
				setattr(history, k, v)

			history.date = parse_isodate(history.date)
			stored_history = None
			try:
				stored_history = session.query(History).filter(History.date==history.date).one()
			except:
				session.add(history)
				return

			if stored_history.generatedAt < history.generatedAt:
				history = session.merge(history)
				session.add(history)

def main():
	Base.metadata.create_all(db)
	context = zmq.Context()
	subscriber = context.socket(zmq.SUB)

	# Connect to the first publicly available relay.
	subscriber.connect('tcp://relay-us-central-1.eve-emdr.com:8050')
	# Disable filtering.
	subscriber.setsockopt(zmq.SUBSCRIBE, "")

	print 'Relay started, waiting for data...'

	#f = open('emdr_data.txt', 'w')
	total_length = 0
	start = datetime.now()
	max_read = 0
	while True:
		# Receive raw market JSON strings.
		market_json = zlib.decompress(subscriber.recv())
		#print 'Read... ', len(market_json)
		length = len(market_json)
		if length > max_read:
			max_read = length
			print max_read
		total_length += len(market_json)
		# Un-serialize the JSON data to a Python dict.
		market_data = json.loads(market_json)

		#dt = datetime.now() - start
		#dt = dt.total_seconds()
		#print 'Data Rate:', (total_length / 1024.0 / dt), 'KB/s'

		# Dump the market data to stdout. Or, you know, do more fun
		# things here.
		if market_data['resultType'] == 'orders':
			processOrdersPacket(market_data)
		elif market_data['resultType'] == 'history':
			processHistoryPacket(market_data)

		session.commit()

if __name__ == '__main__':
	main()