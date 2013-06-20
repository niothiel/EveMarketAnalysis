import zlib
import zmq
import json
from datetime import datetime
from util import parse_isodate

from database.emdr import session, Order, History

buy_orders = 0
sell_orders = 0

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

			global buy_orders
			global sell_orders
			if order.bid == 1:
				buy_orders += 1
			else:
				sell_orders += 1

			print 'buy:', buy_orders, 'sell:', sell_orders

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
		for row in rowset['rows']:
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
				stored_history = session.query(History).filter(\
					History.date==history.date, History.typeID==history.typeID, History.regionID==history.regionID).one()
			except:
				session.add(history)
				return

			if stored_history.generatedAt < history.generatedAt:
				history = session.merge(history)
				session.add(history)

def emdr_service():
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
	emdr_service()