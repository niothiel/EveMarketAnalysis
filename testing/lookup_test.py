from database.db.staticdata.queries import *
import database

session = database.db.gamedata_session

def print_pricing_info(item_name):
	#item = session.query(Item).filter(Item.name == item_name).one()
	item = getItem(item_name)
	item_typeid = int(item.typeID)

	from market.evecentral import EveCentral
	prices = EveCentral.getPrices([item_typeid])
	if len(prices) == 0:
		print 'Error, no prices fetched!'
	else:
		print prices.values()[0]

def main():
	itemnamelist = []
	for item in session.query(Item).all():
		itemnamelist.append(item.name)

	while True:
		input_name = raw_input('Item name to look up: ')

		possibleitemnames = [name for name in itemnamelist if input_name in name]
		num_results = len(possibleitemnames)
		if num_results == 0:
			print 'Error: No results!'
		elif num_results == 1:
			print_pricing_info(possibleitemnames[0])
			pass
		elif num_results > 1 and num_results < 15:
			for i, item in enumerate(possibleitemnames):
				print str(i) + '.', item

			num = int(raw_input('Selection: '))
			itemname = possibleitemnames[num]
			print_pricing_info(itemname)
		else:
			print 'Error: Too many results!', num_results

if __name__ == '__main__':
	main()