from database.emdr import session
from database.emdr import Order
from sqlalchemy.sql import func

def get_item_prices(typeID, regionID):
	session.query(Order).filter(Order.typeID==typeID, Order.regionID==regionID)

def get_order(orderID):
	session.query(Order).filter(Order.orderID==orderID)

def get_item_statistics(typeID, regionID):
	q = session.query(
				  func.max(Order.price).label('max_price'),
	              func.min(Order.price).label('min_price'),
	              func.avg(Order.price).label('avg_price'),
	              Order.bid
	).filter(Order.typeID==typeID).filter(Order.regionID==regionID).group_by(Order.bid)

	query_results = q.all()

	result = dict()
	result['typeid'] = typeID
	result['regionid'] = regionID
	result['buy'] = dict()
	result['sell'] = dict()
	for query_result in query_results:
		if query_result[-1] == True: # It's a bid, meaning it's for buy orders.
			result['buy']['max'] = query_result[0]
			result['buy']['min'] = query_result[1]
			result['buy']['avg'] = query_result[2]
		else:                        # It's a sell order.
			result['sell']['max'] = query_result[0]
			result['sell']['min'] = query_result[1]
			result['sell']['avg'] = query_result[2]

	return result

if __name__ == '__main__':
	import logging
	logging.basicConfig()
	logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

	results = get_item_statistics(34, 10000002)
	print results