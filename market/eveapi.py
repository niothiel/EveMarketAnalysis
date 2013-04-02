import xml.etree.ElementTree as ET
from cache import GenericCache
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
				child[key] = util.smart_parse(value)

			result.append(child)

		return result

	def getChar(self, url, params = {}):
		params['characterID'] = self.charId
		return self.get(url, params)

	def getAssets(self):
		allAssets = self.getChar(EveApiUrl.ASSETS)
		for asset in allAssets:
			asset['quantity'] = int(asset['quantity'])
			asset['name'] = ItemDb().get_name(asset['typeID'])
			del asset['flag']
			del asset['singleton']

		return allAssets

	def getOrders(self):
		return self.getChar(EveApiUrl.MARKET_ORDERS)

	def getTransactions(self):
		return self.getChar(EveApiUrl.WALLET_TRANSACTIONS)