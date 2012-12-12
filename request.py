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

evecMarketstat =	'http://api.eve-central.com/api/marketstat?'
evemPriceHistory =	'http://api.eve-marketdata.com/api/item_history2.json?char_name=asdf&days=5&'

typeToName = {}

def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def formatNum(price):
	if price < 1000:
		return str(price)
	if price < 1000000:
		return '%.1fk' % (price / 1000)
	
	return '%.1fM' % (price / 1000000)

class MarketItem:
	def __init__(self):
		self.typeId = None
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
		
	def fromEveMarketData(self, orderDict):
		# Getting the stuff from eve-marketdata.com. Effin messy.
		orderDict = orderDict['emd']['result']
		
		# Again, bit awkward, adding the total order history
		self.soldOrderHistory = []
		sumOrders = 0
		numDataPoints = 0
		for entry in orderDict:
			if entry['row']['typeID'] == str(self.typeId):
				numOrders = int(entry['row']['orders'])
				sumOrders += numOrders
				numDataPoints += 1
		
		if numDataPoints <> 0:
			self.soldOrders = float(sumOrders) / numDataPoints
		
	def fromEveMarketDataPerItem(self, orderDict):
		if self.typeId == None:
			return
	
		url = evemPriceHistory
		url += 'region_ids=%d&type_ids=%d' % (regions['the_forge'], self.typeId)
		print url
		
		data = urllib2.urlopen(url).read()
		orderDict = json.loads(data)
		
		self.fromEveMarketData2(orderDict)
	
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

def _getItems(typeIds, region):
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

	print 'Using URL:', urlCentral
	print 'Using URL:', urlData

	htmlReply = urllib2.urlopen(urlCentral).read()
	root = ET.fromstring(htmlReply)[0]
	
	eveMarketDataReply = urllib2.urlopen(urlData).read()
	eveMarketDataDict = json.loads(eveMarketDataReply)
	
	items = []
	for typeNode in root:
		item = MarketItem()
		item.fromEveCentral(typeNode)
		item.fromEveMarketData(eveMarketDataDict)
		items.append(item)

	return items
	
def getItems(typeIds, region):
	totalItems = []
	for chunk in chunks(typeIds, 1000):
		totalItems += _getItems(chunk, region)
		
	return totalItems

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
	itemList = getItems(typeIds, 'the_forge')
	itemList = filter(itemCriteria, itemList)
	itemList = sorted(itemList, key=sortCriteria)

	for item in itemList:
		print item, '\n'

if __name__ == '__main__':
	main()
