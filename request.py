#/usr/bin/python
import json
import xml.etree.ElementTree as ET
import urllib2
from pprint import pprint

systems = {
	'rens': 10000030,
	'jita': 30000142
}

regions = {
	'the_forge': 10000002,
	'heimatar': 30002510
}

evecMarketstat = 'http://api.eve-central.com/api/marketstat?'
evemPriceHistory = 'http://api.eve-marketdata.com/api/item_history2.json?char_name=asdf&region_ids=10000002&days=5&'
#statStr = 'http://api.eve-central.com/api/marketstat?typeid=%d&regionlimit=10000030'

typeToName = {}

def formatNum(price):
	if price < 1000:
		return str(price)
	if price < 1000000:
		return '%.1fk' % (price / 1000)
	
	return '%.1fM' % (price / 1000000)

class MarketItem:
	def __init__(self):
		self.name = None
		self.buyOrders = 0
		self.buyPrice = 0
		self.sellOrders = 0
		self.sellPrice = 0
		self.totalOrders = 0
		self.priceDifference = 0
		self.volumeDifference = 0
		self.soldOrderHistory = None
		self.soldOrders = 0

	def __repr__(self):
		s = self.name + '\n'
		s += 'Buy:\t' + str(self.buyOrders) + '\t@ ' + formatNum(self.buyPrice) + '\n'
		s += 'Sell:\t' + str(self.sellOrders) + '\t@ ' + formatNum(self.sellPrice) + '\n'
		s += 'Orders Filled: \t' + str(self.soldOrders) + '\n'
		#s += 'Order history: ' + str(soldOrderHistory) + '\n'

		s += 'Price Difference: %0.2f\n' % self.priceDifference
		s += 'Volume Difference: %0.2f' % self.volumeDifference
		return s

	def __str__(self):
		return self.__repr__()

def initTypeToNameDB():
	f = open('typeid.txt', 'r')
	for line in f:
		splitString = line.split('\t')
		typeId = splitString[0].strip()
		name = splitString[1].strip()
		typeToName[typeId] = name
	f.close()

def getItemName(typeId):
	if str(typeId) in typeToName:
		return typeToName[str(typeId)]
	else:
		return None

def getItems(typeIds, system=None, region=None):
	if len(typeIds) == 0:
		return []

	if system == None and region == None:			# If nothing's specified, just return
		return []

	# Generate the url to use for the query
	url = evecMarketstat
	if system <> None:					# Set the system if we have one
		url += 'usesystem=%d&' % systems[system]
	if region <> None:					# Set the region if we have one
		url += 'regionlimit=%d&' % regions[region]
	for typeId in typeIds:					# Add all the typeids
		if getItemName(typeId) <> None:			# Check to make sure the thing actually exists.
			url += 'typeid=%d&' % typeId
	url = url[:-1]						# Strip the ending &

	print 'Using URL:', url

	htmlReply = urllib2.urlopen(url).read()
	root = ET.fromstring(htmlReply)[0]
	
	items = []
	for typeNodes in root:
		item = getItemFromNode(typeNodes)
		if item <> None:
			items.append(item)

	return items

def getItemFromNode(itemNode):
	typeId = int(itemNode.attrib['id'])

	if getItemName(typeId) == None:
		return
		
	# Getting the stuff from eve-marketdata.com. Effin messy.
	# Generate the url to use for the query
	url = evemPriceHistory + 'type_ids=%d' % typeId
	print 'Using URL:', url
	htmlReply = urllib2.urlopen(url).read()
	priceHistory = json.loads(htmlReply)
	priceHistory = priceHistory['emd']['result']
	#pprint( priceHistory )
	#exit(1)

	buyNode = itemNode.find('buy')
	sellNode = itemNode.find('sell')
	allNode = itemNode.find('all')

	m = MarketItem()
	m.name = getItemName(typeId)
	m.buyOrders = int(buyNode.find('volume').text)
	m.buyPrice = float(buyNode.find('max').text)
	m.sellOrders = int(sellNode.find('volume').text)
	m.sellPrice = float(sellNode.find('min').text)
	m.totalOrders = int(allNode.find('volume').text)
	
	# Again, bit awkward, adding the total order history
	m.soldOrderHistory = []
	sumOrders = 0
	numDataPoints = len(priceHistory)
	for entry in priceHistory:
		numOrders = int(entry['row']['orders'])
		#m.soldOrderHistory.append(entry['row'])
		sumOrders += numOrders
	
	if numDataPoints <> 0:
		m.soldOrders = float(sumOrders) / numDataPoints

	if m.buyOrders == 0 or m.buyPrice == 0 or m.sellOrders == 0 or m.sellPrice == 0:
		m.priceDifference = 0
		m.volumeDifference = 0
	else:
		m.priceDifference = abs(m.buyPrice - m.sellPrice) / m.buyPrice * 100
		m.volumeDifference = abs(m.buyOrders - m.sellOrders) / float(m.totalOrders) * 100

	return m

def itemCriteria(item):
	if item.priceDifference < 15:
		return False
	if item.priceDifference > 100:
		return False
	elif item.totalOrders < 100:
		return False
	elif item.volumeDifference > 70:
		return False
	elif item.buyPrice < 20000:
		return False
	elif item.soldOrders < 80:
		return False
	elif 'Blueprint' in item.name:
		return False
	else:
		return True

def sortCriteria(item):
	return item.soldOrders

def main():
	initTypeToNameDB()

	typeIds = range(34, 41) + range(178, 202) + range(377, 551) + range(551, 1357) + range(16305, 16536)
	itemList = getItems(typeIds, 'jita')

	itemList = filter(itemCriteria, itemList)
	itemList = sorted(itemList, key=sortCriteria)

	for item in itemList:
		print item, '\n'

if __name__ == '__main__':
	main()
