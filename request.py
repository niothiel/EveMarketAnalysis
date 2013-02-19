#/usr/bin/python

import json
import xml.etree.ElementTree as ET
import urllib2

from datetime import datetime, time, timedelta
from cache import ShelfCache
from itemdb import ItemDb
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

itemdb = ItemDb()
volumeHistory = None

class MarketItem:
	def __init__(self):
		self.typeId = -1
		self.name = None
		self.numBuyOrders = -1
		self.buyPrice = -1
		self.numSellOrders = -1
		self.sellPrice = -1
		self.totalOrders = -1
		self.priceDifference = -1
		self.soldOrderHistory = []
		self.soldOrders = -1

	def __repr__(self):
		s = self.name + '\n'
		s += 'Buy:\t' + str(self.numBuyOrders) + '\t@ ' + formatNum(self.buyPrice) + '\n'
		s += 'Sell:\t' + str(self.numSellOrders) + '\t@ ' + formatNum(self.sellPrice) + '\n'
		s += 'Orders Filled: \t' + str(self.soldOrders) + '\n'
		s += 'Order history: ' + str(self.soldOrderHistory) + '\n'

		s += 'Price Difference: %0.2f\n' % self.priceDifference
		return s

	def __str__(self):
		return self.__repr__()

	def fromEveMarketData(self, orderDict):
		# Getting the stuff from eve-marketdata.com. Effin messy.
		sumOrders = 0
		numDataPoints = 0
		for entry in orderDict:
			if entry['row']['typeID'] == str(self.typeId):
				#numOrders = int(entry['row']['orders'])
				numOrders = int(entry['row']['volume'])
				sumOrders += numOrders
				numDataPoints += 1

		if numDataPoints <> 0:
			self.soldOrders = float(sumOrders) / numDataPoints

		self.ranking = (self.sellPrice - self.buyPrice) * self.soldOrders / 100

	def fromEveCentral(self, itemNode):
		self.typeId = int(itemNode.attrib['id'])
		self.name = itemdb.get_name(self.typeId)

		if self.name is None:
			return

		buyNode = itemNode.find('buy')
		sellNode = itemNode.find('sell')
		allNode = itemNode.find('all')

		self.numBuyOrders = int(buyNode.find('volume').text)
		self.buyPrice = float(buyNode.find('max').text)
		self.numSellOrders = int(sellNode.find('volume').text)
		self.sellPrice = float(sellNode.find('min').text)
		self.totalOrders = int(allNode.find('volume').text)

		if self.numBuyOrders <> 0 and self.buyPrice <> 0 and self.numSellOrders <> 0 and self.sellPrice <> 0:
			self.priceDifference = abs(self.buyPrice - self.sellPrice) / self.buyPrice * 100

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

cache = ShelfCache('data/items.shelf')
def _getItems(typeIds, region, volumeHistory):
	if len(typeIds) == 0:
		return []

	# Eliminate the invalid ids
	typeIds = [type_id for type_id in typeIds if itemdb.get_name(type_id)]

	items = []
	needed_ids = []
	for type_id in typeIds:
		item = cache.get(str(type_id))
		if item:
			items.append(item)
		else:
			needed_ids.append(type_id)

	typeIds = needed_ids

	if len(typeIds) == 0:
		return items

	# Generate the url to use for the query
	urlCentral = evecMarketstat
	urlData = evemPriceHistory

	if region is not None:				# Set the region if we have one
		urlCentral += 'regionlimit=%d&' % regions[region]
		urlData += 'region_ids=%d&' % regions[region]

	urlData += 'type_ids='

	for typeId in typeIds:				# Add all the typeids
		#if getItemName(typeId) is not None:	# Check to make sure the thing actually exists.
		urlCentral += 'typeid=%d&' % typeId
		urlData += '%d,' % typeId

	urlCentral = urlCentral[:-1]		# Strip the ending &
	urlData = urlData[:-1]

	#print 'Getting items:', min(typeIds), 'to', max(typeIds)

	htmlReply = urllib2.urlopen(urlCentral).read()
	try:
		root = ET.fromstring(htmlReply)[0]
	except:
		print htmlReply

	eveMarketDataReply = urllib2.urlopen(urlData).read()
	try:
		eveMarketDataDict = json.loads(eveMarketDataReply)
	except:
		print 'Got bad data from Eve-MarketData:', eveMarketDataReply
		exit(1)
	eveMarketDataDict = eveMarketDataDict['emd']['result']

	for typeNode in root:
		item = MarketItem()
		item.fromEveCentral(typeNode)
		item.fromEveMarketData(eveMarketDataDict)
		#item.fromVolumeDb(volumeHistory)
		items.append(item)
		cache.set(str(item.typeId), item)

	return items

def getItems(typeIds=None, region='the_forge', callbackFunc=None):
	if typeIds is None:
		typeIds = itemdb.get_typeids()

	#orders = OrdersTable()
	#vH = orders.getJitaVolumesLastDay()

	totalItems = []
	numProcessed = 0
	totalOrders = len(typeIds)
	chunk_size = 150

	for chunk in chunks(typeIds, chunk_size):
		#print 'Getting:', len(chunk)
		totalItems += _getItems(chunk, region, None)

		numProcessed += chunk_size

		# Update the application to show status.
		if callbackFunc is not None:
			callbackFunc(numProcessed / float(totalOrders))

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

def sortCriteria(item):
	return item.soldOrders

def main():
	itemList = getItems()
	itemList = filter(itemCriteria, itemList)
	itemList = sorted(itemList, key=lambda item: sortCriteria(item))

	for item in itemList:
		print item

if __name__ == '__main__':
	main()
