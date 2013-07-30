from database.emdr import session
#from database.emdr import Session
from database.emdr import Order
from sqlalchemy.sql import func

from database.static.queries import getSystem, getRegion, getItem

def get_item_prices(typeID, regionID):
	session.query(Order).filter(Order.typeID==typeID, Order.regionID==regionID)

def get_order(orderID):
	session.query(Order).filter(Order.orderID==orderID)

# Need to explicitly specify either: regionID, systemID, or stationID
def get_item_statistics(typeID, region=None, system=None, station=None):
	# TODO: IMPORTANT: Fix session management, as for some reason the data is not being updated throughout the runtime unless we have a brand new session.
	# http://flask.pocoo.org/mailinglist/archive/2012/8/27/flask-sqlalchemy-caching-results/#c98a920679bb3beae1db4c85bbe92473

	#session = Session()

	# TODO: Make the average price a weighted one... instead of just per entry, take into account the volume.
	q = session.query(
				  func.max(Order.price).label('max_price'),
	              func.min(Order.price).label('min_price'),
	              func.avg(Order.price).label('avg_price'),
	              func.min(Order.generatedAt).label('generated_at'),
	              Order.bid
	).filter(Order.typeID==typeID)
	q = _add_location(q, region, system, station)
	q = q.group_by(Order.bid)

	query_results = q.all()

	result = dict()
	result['typeid'] = typeID
	result['region'] = region
	#result['timestamp'] = query_results[0][-2]
	print 'Querying for:', typeID

	for query_result in query_results:
		if query_result[-1] == True: # It's a bid, meaning it's for buy orders.
			result['buy'] = dict()
			result['buy']['max'] = query_result[0]
			result['buy']['min'] = query_result[1]
			result['buy']['avg'] = query_result[2]
		else:                        # It's a sell order.
			result['sell'] = dict()
			result['sell']['max'] = query_result[0]
			result['sell']['min'] = query_result[1]
			result['sell']['avg'] = query_result[2]
			print result['sell']['min']

	# Turns out that even when querying, you always have to call session.commit()! Otherwise you will get old data.
	session.commit()
	return result

# TODO: Implement stations.. everywhere.
def _add_location(query, region, system, station):
	if region:
		query = query.filter(Order.regionID==getRegion(region).ID)
	if system:
		query = query.filter(Order.solarSystemID==getSystem(system).ID)

	return query

def get_buy_sell(region=None, system=None, station=None):
	q = session.query(
		Order.typeID,
		func.max(Order.price).label('max_price'),
		func.min(Order.price).label('min_price'),
		Order.bid
	)
	q = _add_location(q, region, system, station)
	q = q.group_by(Order.typeID, Order.bid)

	query_results = q.all()
	margins = dict()
	for result in query_results:
		typeid = result[0]
		margins.setdefault(typeid, dict())
		if result[-1] == True: # It's a bid, meaning someone is trying to buy.
			margins[typeid]['buy'] = result[1] # Use the max buy price.
		else:
			margins[typeid]['sell'] = result[2] # Use the min sell price.

	results = list()
	for typeid, item in margins.iteritems():
		db_item = getItem(int(typeid))

		# If the item isn't found in our database, skip over it.
		if not db_item:
			continue

		# If we don't have BOTH buy and sell values for the item, skip over it.
		if 'buy' not in item or 'sell' not in item:
			continue

		item['name'] = db_item.name
		item['typeid'] = typeid
		results.append(item)

	return results

if __name__ == '__main__':
	#import logging
	#logging.basicConfig()
	#logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

	results = get_item_statistics(34, system='Jita')
	print results

	#results = get_buy_sell(system='Jita')
	#from pprint import pprint
	#pprint(results)