from database.emdr import session
from database.emdr import Order

def get_item_prices(typeID, regionID):
	session.query(Order).filter(Order.typeID==typeID, Order.regionID==regionID)

def get_prices():
