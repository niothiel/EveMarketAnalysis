import MySQLdb
from itemdb import ItemDb
from request import getItems

itemdb = ItemDb()

def test():
	itemlist = []
	with open('data/testmanu.txt', 'r') as fin:
		for line in fin:
			line = line.strip()
			line = line.split()

			item = {
				'name': ' '.join(line[:-2]),
				'm_price': float(line[-2]),
				'j_price': float(line[-1])
			}
			itemlist.append(item)

	itemlist = sorted(itemlist, key=lambda item: item['m_price'] - item['j_price'])
	for item in itemlist:
		print item['name'], '\t', item['m_price'], '\t', item['j_price']

def main():
	test()
	return

	conn = MySQLdb.connect(host='127.0.0.1', user='root', passwd='asdf', db='evetest')
	cursor = conn.cursor()
	cursor.execute('SELECT * FROM invtypematerials JOIN invtypes ON invtypematerials.typeID=invtypes.typeID')

	build_reqs = {}
	for row in cursor:
		typeid = row[0]
		if typeid not in build_reqs.keys():
			build_reqs[typeid] = []

		build_reqs[typeid].append(row)

	for typeid, value in build_reqs.iteritems():
		name = itemdb.get_name(typeid)

		items = getItems([typeid])
		if len(items) == 0:
			continue
		jita_price = items[0].sellPrice
		manufacturing_price = 0
		for row in value:
			mineral_typeid = row[1]
			mineral_qty = row[2]
			mineral_price = getItems([mineral_typeid])[0].sellPrice

			manufacturing_price += mineral_qty * mineral_price

		if jita_price > manufacturing_price:
			print name, manufacturing_price, jita_price

if __name__=='__main__':
	main()