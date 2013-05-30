import urllib2
import xml.etree.ElementTree as ET

import database
from database.db.staticdata.queries import getSystem, getRegion, getItem
from cache import GenericCache
from util import formatIsk

from pprint import pprint

# TODO: This takes a long time on startup, need to fix.
def _get_valid_ids():
	session = database.db.gamedata_session
	valid_ids = []
	for item in session.query(database.gamedata.Item).all():
		if item.marketGroupID:
			valid_ids.append(int(item.typeID))

	return set(valid_ids)

class PriceInfo:
	def __init__(self):
		self.volume = 0
		self.avg = 0
		self.max = 0
		self.min = 0
		self.stddev = 0
		self.median = 0
		self.percent = 0

	def fromNode(self, node):
		self.volume = int(node.find('volume').text)
		self.avg = float(node.find('avg').text)
		self.max = float(node.find('max').text)
		self.min = float(node.find('min').text)
		self.stddev = float(node.find('stddev').text)
		self.median = float(node.find('median').text)
		self.percent = float(node.find('percentile').text)

	def __str__(self):
		return '[vol: %d][max: %s][min: %s][avg: %s][pct: %s]' % \
		       (self.volume, formatIsk(self.max), formatIsk(self.min), formatIsk(self.avg), formatIsk(self.percent))

class Price:
	def __init__(self):
		self.id = None
		self.name = 'Unavailable'
		self.buy = PriceInfo()
		self.sell = PriceInfo()
		self.all = PriceInfo()

	def __repr__(self):
		return 'id: %d buy: %s, sell: %s, all: %s' % (self.id, str(self.buy), str(self.sell), str(self.all))

	def profit(self):
		if self.buy.max <> 0:
			return abs(self.buy.max - self.sell.min) / float(self.buy.max)
		return 0

class EveCentral:
	URL = 'http://api.eve-central.com/api/marketstat?'

	validids = _get_valid_ids()
	cache = GenericCache()

	@classmethod
	def getPrices(cls, typeIDs=None, region=None, system='Jita'):
		basequeryurl = EveCentral.URL
		if typeIDs is None:
			typeIDs = EveCentral.validids
		toRequest = set(typeIDs)
		requested = set()
		priceMap = {}

		if region:
			basequeryurl += 'regionlimit=%s&' % getRegion(region).ID

		if system:
			basequeryurl += 'usesystem=%s&' % getSystem(system).ID

		# Eliminate all items that don't have a market group as Eve Central doesn't track those items.
		culledRequest = []
		for typeID in toRequest:
			if typeID in EveCentral.validids:
				culledRequest.append(typeID)
		toRequest = set(culledRequest)

		# Hit the cache for some fish and see if we can get any yummmm.
		# Disable the cache for now.
		"""
		for id in toRequest:
			price = EveCentral.cache.get(id)
			if price:
				priceMap[price.id] = price
				requested.add(id)
		toRequest = toRequest.difference(requested)
		"""

		while len(toRequest):
			requrl = basequeryurl
			for typeID in toRequest:
				newurl = requrl
				newurl += 'typeid=%d&' % typeID

				if len(newurl) < 2048:
					requrl = newurl
					requested.add(typeID)
				else:
					break

			requrl = requrl[:-1]
			#print len(requrl), requrl
			toRequest = toRequest.difference(requested)

			# Finally request the stuff we need
			htmlReply = urllib2.urlopen(requrl).read()
			rootnode = None
			try:
				rootnode = ET.fromstring(htmlReply)[0]
			except:
				print htmlReply
				return

			for typenode in rootnode:
				buyNode = typenode.find('buy')
				sellNode = typenode.find('sell')
				allNode = typenode.find('all')

				price = Price()
				price.id = int(typenode.attrib['id'])
				price.name = getItem(price.id).name
				price.buy.fromNode(buyNode)
				price.sell.fromNode(sellNode)
				price.all.fromNode(allNode)

				priceMap[price.id] = price
				EveCentral.cache.set(price.id, price)

		return priceMap

def generate_valid_typeids():
	session = database.db.gamedata_session
	with open('data/valid_typeids.txt', 'w') as fout:
		for item in session.query(database.types.Item).all():
			if item.marketGroupID:
				fout.write(str(item.ID))
				fout.write('\n')

if __name__ == '__main__':
	generate_valid_typeids()
	prices = EveCentral.getPrices(range(1,2000))
	pprint(prices)
