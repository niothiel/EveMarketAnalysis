import sys
import zlib
import zmq
import simplejson
from util import parse_isodate
import traceback

import multiprocessing

from database.emdr import session, Order, History

order_ids = set()
buy_orders = 0
sell_orders = 0

"""
def processOrdersPacket(market_data):
	global order_ids
	global buy_orders
	global sell_orders

	columns = market_data['columns']
	for rowset in market_data['rowsets']:
		for row in rowset['rows']:
			rowdict = dict(zip(columns, row))

			if rowdict['orderID'] not in order_ids:
				order_ids.add(rowdict['orderID'])

				if rowdict['bid']:
					buy_orders += 1
				else:
					sell_orders += 1
			if len(order_ids) % 10 == 0:
				try:
					print 'Buy:', buy_orders, 'Sell:', sell_orders, 'Ratio (Sell/Buy):', float(sell_orders) / buy_orders
				except:
					pass
"""
def processOrdersPacket(market_data):
	global buy_orders
	global sell_orders
	global order_ids

	for rowset in market_data['rowsets']:
		for row in rowset['rows']:
			order = Order()
			order.typeID = rowset['typeID']
			order.regionID = rowset['regionID']
			order.generatedAt = parse_isodate(rowset['generatedAt'])

			vals = zip(market_data['columns'], row)
			for k, v in vals:
				setattr(order, k, v)

			if order.orderID not in order_ids:
				order_ids.add(order.orderID)
				if order.bid:
					buy_orders += 1
				else:
					sell_orders += 1

				if len(order_ids) % 10 == 0:
					try:
						pass
						print 'Buy:', buy_orders, 'Sell:', sell_orders, 'Ratio (Sell/Buy):', float(sell_orders) / buy_orders
					except:
						pass

			order.issueDate = parse_isodate(order.issueDate)
			stored_order = None

			# If there is no order with that id, just add it to DB.
			stored_order_query = session.query(Order).filter(Order.orderID==order.orderID)

			if stored_order_query.count() == 0:
				session.add(order)
			elif stored_order_query.count() > 1:
				print 'Orderid not unique!', order.orderID
				exit(1)
			elif stored_order_query.first().generatedAt < order.generatedAt:
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

	# Initialize the input data queue for the processes, as well as the output result queue.
	manager = multiprocessing.Manager()
	emdr_queue = manager.Queue()
	result_queue = manager.Queue()

	# Spawn five processes to take care of our beautiful firehouse of data.
	#for x in range(5):
	#	multiprocessing.Process(target=worker, args=(emdr_queue, result_queue)).start()

	print 'Relay started, waiting for data...'
	while True:
		# Enqueue the messages as they come in
		#emdr_queue.put(subscriber.recv())

		# Receive raw market JSON strings.
		market_json = zlib.decompress(subscriber.recv())

		# Un-serialize the JSON data to a Python dict.
		market_data = simplejson.loads(market_json)

		# Parse all of the data
		if market_data['resultType'] == 'orders':
			processOrdersPacket(market_data)
		#elif market_data['resultType'] == 'history':
		#	processHistoryPacket(market_data)
		session.commit()

		#while True:
		#	try:
		#		print result_queue.get(block=False)
		#	except:
		#		break


def worker(queue, done_queue):
	while True:
		try:
			# Receive raw market JSON strings.
			market_json = zlib.decompress(queue.get())

			# Un-serialize the JSON data to a Python dict.
			market_data = simplejson.loads(market_json)

			# Parse all of the data
			if market_data['resultType'] == 'orders':
				processOrdersPacket(market_data)
			#elif market_data['resultType'] == 'history':
			#	processHistoryPacket(market_data)
			session.commit()
		except:
			# Need to do more debugging here as this occurs in a separate process and it can get kind of sketchy
			print 'Error in a worker thread!', sys.exc_info()
			print traceback.print_tb(sys.exc_info()[2], None, sys.stdout)
			sys.stdout.flush()
			exit(1)

if __name__ == '__main__':
	emdr_service()
	#emdr_service_2()