#/usr/bin/python
from datetime import datetime, time, timedelta
import pickle
import json
import xml.etree.ElementTree as ET
import urllib2
from pprint import pprint
from orders import OrdersTable
from util import chunks, formatNum

systems = {
	'rens': 10000030,
	'jita': 30000142
}

regions = {
	'the_forge': 10000002,
	'heimatar': 30002510
}

evecMarketstat =	'http://api.eve-central.com/api/marketstat?'
evemPriceHistory =	'http://api.eve-marketdata.com/api/item_history2.json?char_name=asdf&days=5&'

typeToName = {}
volumeHistory = None

class MarketItem:
	def __init__(self):
		self.typeId = -1
		self.name = None
		self.buyOrders = None
		self.buyPrice = -1
		self.sellOrders = None
		self.sellPrice = -1
		self.totalOrders = -1
		self.priceDifference = -1
		self.volumeDifference = -1
		self.soldOrderHistory = None
		self.soldOrders = -1

	def __repr__(self):
		s = self.name + '\n'
		s += 'Buy:\t' + str(self.buyOrders) + '\t@ ' + formatNum(self.buyPrice) + '\n'
		s += 'Sell:\t' + str(self.sellOrders) + '\t@ ' + formatNum(self.sellPrice) + '\n'
		s += 'Orders Filled: \t' + str(self.soldOrders) + '\n'
		s += 'Order history: ' + str(self.soldOrderHistory) + '\n'

		s += 'Price Difference: %0.2f\n' % self.priceDifference
		s += 'Volume Difference: %0.2f\n' % self.volumeDifference
		return s

	def __str__(self):
		return self.__repr__()

	def fromEveCentral(self, itemNode):
		self.typeId = int(itemNode.attrib['id'])
		self.name = getItemName(self.typeId)

		if self.name == None:
			return

		buyNode = itemNode.find('buy')
		sellNode = itemNode.find('sell')
		allNode = itemNode.find('all')

		self.buyOrders = int(buyNode.find('volume').text)
		self.buyPrice = float(buyNode.find('max').text)
		self.sellOrders = int(sellNode.find('volume').text)
		self.sellPrice = float(sellNode.find('min').text)
		self.totalOrders = int(allNode.find('volume').text)

		if self.buyOrders <> 0 and self.buyPrice <> 0 and self.sellOrders <> 0 and self.sellPrice <> 0:
			self.priceDifference = abs(self.buyPrice - self.sellPrice) / self.buyPrice * 100
			self.volumeDifference = abs(self.buyOrders - self.sellOrders) / float(self.totalOrders) * 100
	
	def fromVolumeDb(self, db):
		if self.typeId not in db.keys():
			return
		
		entry = db[self.typeId]
		self.soldOrderHistory = entry
		
		self.soldOrders = 0
		
		if 'buy' in entry.keys():
			self.soldOrders += entry['buy']
		
		if 'sell' in entry.keys():
			self.soldOrders += entry['sell']
		
	def sortCriteria(self, item):
		#itemBuy = item.buyPrice * 1.03
		#itemSell = item.sellPrice * 0.95
		
		#volume = item.soldOrders * 0.20
		
		#totalInvestment = itemBuy * volume
		#totalRevenue = itemSell * volume
		
		#self.totalProfit = totalRevenue - totalInvestment
		#return self.totalProfit
		
		return self.priceDifference 
		
def initTypeToNameDB():
	f = open('data/typeid.txt', 'r')
	for line in f:
		splitString = line.split('\t')
		typeId = splitString[0].strip()
		name = splitString[1].strip()
		typeToName[typeId] = name
	f.close()

def getItemName(typeId):
	if len(typeToName) == 0:
		initTypeToNameDB()
	
	if str(typeId) in typeToName:
		return typeToName[str(typeId)]
	else:
		return None

def _getItems(typeIds, region, volumeHistory):
	if len(typeIds) == 0:
		return []

	# Generate the url to use for the query
	urlCentral = evecMarketstat
	urlData = evemPriceHistory

	if region <> None:					# Set the region if we have one
		urlCentral += 'regionlimit=%d&' % regions[region]
		urlData += 'region_ids=%d&' % regions[region]

	urlData += 'type_ids='

	for typeId in typeIds:				# Add all the typeids
		if getItemName(typeId) <> None:	# Check to make sure the thing actually exists.
			urlCentral += 'typeid=%d&' % typeId
			urlData += '%d,' % typeId

	urlCentral = urlCentral[:-1]		# Strip the ending &
	urlData = urlData[:-1]

	print 'Getting items:', typeIds[0], 'to', typeIds[-1]

	htmlReply = urllib2.urlopen(urlCentral).read()
	try:
		root = ET.fromstring(htmlReply)[0]
	except:
		print htmlReply

	#eveMarketDataReply = urllib2.urlopen(urlData).read()
	#eveMarketDataDict = json.loads(eveMarketDataReply)

	items = []
	for typeNode in root:
		item = MarketItem()
		item.fromEveCentral(typeNode)
		#item.fromEveMarketData(eveMarketDataDict)
		item.fromVolumeDb(volumeHistory)
		items.append(item)

	return items

def getItems(region='the_forge', callbackFunc=None):
	typeIds = range(1, 33001)
	
	# Check if we have a cached version of the items db from the last 15 minutes
	try:
		with open('data/items.pickle', 'rb') as fin:
			pickedItems = pickle.load(fin)
			cutoffDate = datetime.utcnow() - timedelta(minutes=15)
			if pickedItems['time'] > cutoffDate:
				return pickedItems['items']
	except:
		pass	
	
	orders = OrdersTable()
	vH = orders.getJitaVolumesLastDay()
	
	totalItems = []
	numProcessed = 0
	for chunk in chunks(typeIds, 1000):
		totalItems += _getItems(chunk, region, vH)
		
		numProcessed += 1000
		
		# Update the application to show status.
		if callbackFunc <> None:
			callbackFunc(numProcessed / float(typeIds[-1]))

	# Always pickle and save the items db
	picklingList = {}
	picklingList['time'] = datetime.utcnow()
	picklingList['items'] = totalItems
	with open('data/items.pickle', 'wb') as fout:
		pickle.dump(picklingList, fout)
	
	return totalItems

def itemCriteria(item):
	if item.priceDifference < 15:
		return False
	elif item.priceDifference > 75:
		return False
	elif item.totalOrders < 100:
		return False
	elif item.volumeDifference > 75:
		return False
	elif item.buyPrice < 90000:
		return False
	elif item.soldOrders < 120:
		return False
	elif item.soldOrders > 8000:
		return False
	elif item.buyPrice > item.sellPrice:
		return False
	elif 'Blueprint' in item.name:
		return False
	
	return True

def grabItemNames():
	'''
	Gets the item names from pinging eve-central. Slow, but gets the job done.
	'''
	templateUrl = 'http://api.eve-central.com/api/quicklook?usesystem=30000142&typeid=%d'
	with open('testtypes.txt', 'w') as f:
		for typeId in range(1, 37000):
			url = templateUrl % typeId
			html = urllib2.urlopen(url).read()
			
			if 'Type not found' in html:
				print str(typeId)
				continue
			
			try:
				root = ET.fromstring(html)
			except:
				print 'Item:', typeId, 'doesn\'t exist'
			
			root = root[0]
			result = str(typeId) + '\t' + root.find('itemname').text 
			print result
			f.write(result + '\n')

def main():
	initTypeToNameDB()

	#typeIds = range(1, 33000)
	itemList = getItems('the_forge')
	itemList = filter(itemCriteria, itemList)
	itemList = sorted(itemList, key=lambda item: item.sortCriteria(item))

	for item in itemList:
		print item

if __name__ == '__main__':
	main()
