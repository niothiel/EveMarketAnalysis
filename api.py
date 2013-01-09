import xml.etree.ElementTree as ET
from request import getItemName
from cache import GenericCache
from request import getItems
import util

keyId = 1483700
vCode = 'tKvQgldcNC5XjFYCFy4IV7W5tliQVKAmkyPSl2xw7kqF6Rx9bUM4PrmmD8CtxrhW'

class EveApiUrl:
	ASSETS = 'https://api.eveonline.com/char/AssetList.xml.aspx'
	CHARACTERS = 'https://api.eveonline.com/account/Characters.xml.aspx'
	MARKET_ORDERS = 'https://api.eveonline.com/char/MarketOrders.xml.aspx'
	WALLET_TRANSACTIONS = 'https://api.eveonline.com/char/WalletTransactions.xml.aspx'
	WALLET_JOURNAL = 'https://api.eveonline.com/char/WalletJournal.xml.aspx'

class CharacterApiReader:
	def __init__(self, keyId, vCode, charName):
		self.keyId = keyId
		self.vCode = vCode
		self.charName = charName
		self.cache = GenericCache()

		# Store the character id.
		self.charId = self.getCharacterId(charName)

	def getCharacterId(self, name):
		result = self.get(EveApiUrl.CHARACTERS)
		for child in result:
			if child['name'] == name:
				return child['characterID']

		raise Exception('Invalid Character name for API key!')

	def get(self, url, params = {}):
		params['keyId'] = keyId
		params['vCode'] = vCode

		cacheKey = (url, str(params))
		html = self.cache.get(cacheKey)
		if html is None:
			html = util.htmlFromUrl(url, params)
			self.cache.set(cacheKey, html)

		root = ET.fromstring(html)
		root = root.find('result').find('rowset')

		result = []
		for child in root:
			child = child.attrib
			for key, value in child.iteritems():
				child[key] = util.smartParse(value)

			result.append(child)

		return result

	def getChar(self, url, params = {}):
		params['characterID'] = self.charId
		return self.get(url, params)

	def getAssets(self):
		allAssets = self.getChar(EveApiUrl.ASSETS)
		for asset in allAssets:
			asset['quantity'] = int(asset['quantity'])
			asset['name'] = getItemName(asset['typeID'])
			del asset['flag']
			del asset['singleton']

		return allAssets

	def getOrders(self):
		return self.getChar(EveApiUrl.MARKET_ORDERS)

	def getTransactions(self):
		return self.getChar(EveApiUrl.WALLET_TRANSACTIONS)

def getItemPaidPrice(apiAdapter, typeId, quantity):
	transactions = apiAdapter.getTransactions()

	typeId = int(typeId)
	quantity = int(quantity)

	totalPaid = 0
	totalQuantity = 0
	for transaction in transactions:
		if totalQuantity == quantity:
			break

		if int(transaction['typeID']) == typeId and transaction['transactionType'] == 'buy':
			price = float(transaction['price'])
			transQuantity = int(transaction['quantity'])

			quantityTaken = min(quantity, transQuantity)
			totalQuantity += quantityTaken
			totalPaid += price * quantityTaken

	if totalQuantity <> quantity:
		return None

	if totalQuantity <> 0:
		return (totalPaid / totalQuantity)
	else:
		return None

def main():
	apiAdapter = CharacterApiReader(keyId, vCode, 'Lotheril Oramar')
	itemPrices = getItems()

	itemDict = {}
	for item in itemPrices:
		itemDict[item.typeId] = item

	assets = apiAdapter.getAssets()
	print 'Assets List:'
	for asset in assets:
		print asset['quantity'], 'x\t', asset['name']

	for asset in assets:
		typeId = int(asset['typeID'])
		quantity = int(asset['quantity'])
		buyAmt = getItemPaidPrice(apiAdapter, typeId, quantity)
		if typeId not in itemDict.keys() or buyAmt is None:
			continue

		sellAmt = itemDict[int(asset['typeID'])].sellPrice
		#if sellAmt > buyAmt:
		print asset['name'], 'buy:', buyAmt, 'sell:', sellAmt

if __name__ == '__main__':
	main()
