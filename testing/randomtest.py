from market.marketbuilder import getItems
from database.db.staticdata.queries import *
import database
from database.types import *
from multiprocessing import *

session = database.db.gamedata_session

def get_required_mats(item_typeid):
	orig_item = getItem(item_typeid)
	#print orig_item.name

	ramtype = {}
	try:
		bp_item = getItem(orig_item.name + ' Blueprint')
		#print bp_item.name

		query = session.query(RamType).filter(RamType.typeID == bp_item.typeID).filter(RamType.activityID == 1)
		for item in query:
			i = item.requireditem
			if i.marketGroup.parent.name == 'Skills':
				continue
			ramtype[item.requiredTypeID] = item.quantity
	except:
		pass

	typemats = {}
	query = session.query(ItemMaterial)
	query = query.filter(ItemMaterial.typeID == orig_item.typeID)
	for item in query:
		#print item.materialTypeID, item.quantity
		typemats[item.materialTypeID] = item.quantity

	return {
		'ram': ramtype,
	    'mats': typemats
	}

def sell_or_salvage(typeid):
	item_query = getItems([typeid])
	if not len(item_query):
		print 'Skipping item: ', getItem(typeid).name
		return

	item_price = item_query[0].sellPrice


	mats = get_required_mats(typeid)
	#pprint(mats)

	mat_cost = 0
	for mat_typeid, quantity in mats['mats'].iteritems():
		mat_price = getItems([mat_typeid])[0].sellPrice
		mat_cost += mat_price * quantity

	for mat_typeid, quantity in mats['ram'].iteritems():
		mat_price = getItems([mat_typeid])[0].sellPrice
		mat_cost += mat_price * quantity


	if item_price < mat_cost:
		print 'Price:', item_price
		print 'Salvage Price:', mat_cost
		name = getItem(typeid).name
		print 'Salvage: ',
		print name
	#else:
	#	print 'Sell: ',


def get_jita_assets():
	from market.eveapi import keyId, vCode, CharacterApiReader

	apiReader = CharacterApiReader(keyId, vCode, 'Lotheril Oramar')
	assets = apiReader.getAssets()
	assets_jita = [item for item in assets if item['locationID'] == 60003760]
	return assets_jita

def get_bottom_level_marketgroup(marketGroup):
	session = database.db.gamedata_session

	children = session.query(MarketGroup).filter(MarketGroup.parentGroupID == marketGroup.ID)
	if not children.count():
		return [marketGroup]
	else:
		l = []
		for child_marketgroup in children:
			l.extend(get_bottom_level_marketgroup(child_marketgroup))
		return l

def main():
	from database.db.staticdata.queries import *
	session = database.db.gamedata_session
	import cProfile
	cProfile.run('getMarketGroupItems(\'Blueprints\')', sort=1)
	#cProfile.run('[group.items for group in get_bottom_level_marketgroup(getMarketGroup(4))]', sort=1)
	return 0

	items = getMarketGroupItems('Blueprints')
	for item in items:
		print item.name

	import market.eveapi_eos
	api = market.eveapi_eos.EVEAPIConnection()
	auth = api.auth(keyID=1483700, vCode='tKvQgldcNC5XjFYCFy4IV7W5tliQVKAmkyPSl2xw7kqF6Rx9bUM4PrmmD8CtxrhW')

	chars = auth.account.Characters()
	print chars.characters
	print dir(chars.characters)

	from database.db.staticdata.queries import *
	session = database.db.gamedata_session

	print session.query(Item).all()
	marketGroup = getMarketGroup(4)
	marketgroups = get_bottom_level_marketgroup(marketGroup)

	items = []
	for marketgroup in marketgroups:
		items.extend(marketgroup.items)
	items.sort(key=lambda item: item.name)

	for item in items:
		print item.ID, item.name, item.blueprint

	assets_jita = get_jita_assets()
	for asset in assets_jita:
		typeid = asset['typeID']
		sell_or_salvage(typeid)

def foo():
	pass

p = Process(target=foo)
p.start()
#if __name__=='__main__':
#	main()