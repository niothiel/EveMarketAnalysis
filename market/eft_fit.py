from collections import Counter
from database.static.queries import getItem

def get_items(eft_text):
	name = None
	ship = None
	items_list = []
	fit_lines = eft_text.split('\n')

	for line in fit_lines:
		line = line.strip()

		# Skip newlines
		if line == '':
			continue

		# Not going to bother with equals, as I don't know all of the edge cases yet.
		if '=' in line:
			continue

		# Skip empty slots
		if 'empty' in line:
			continue

		# If it's a title line.
		if line[0] == '[':
			line = line.strip('[]')
			ship, name = line.split(',')
			ship = ship.strip()
			name = name.strip()
			items_list.append(ship)
		elif ',' in line:
			module, charge = line.split(',')
			items_list.append(module)
			# We're not going to worry about the charges for now.
		else:
			items_list.append(line)

	item_quantities = dict(Counter(items_list))
	items = list()
	for item, quantity in item_quantities.iteritems():
		item_dict = {
			'name': item,
			'quantity': quantity,
		    'typeid': None
		}

		# Populate typeID
		db_item = getItem(item)
		if db_item:
			item_dict['typeid'] = db_item.typeID

		items.append(item_dict)
	return {
		'ship': ship,
		'name': name,
		'items': items
	}

if __name__ == '__main__':
	items = get_items("""
[Tristan, pew pew]
Damage Control II
Small Armor Repairer II
Drone Damage Amplifier II
Limited 1MN Microwarpdrive I
Small Electrochemical Capacitor Booster I,Cap Booster 25
J5 Prototype Warp Disruptor I
125mm Compressed Coil Gun I,Caldari Navy Lead Charge S
125mm Compressed Coil Gun I,Caldari Navy Lead Charge S

Small Anti-Explosive Pump I
Small Auxiliary Nano Pump I
Small Auxiliary Nano Pump I
Drones_Inactive=Hobgoblin II,5
""")
	print items