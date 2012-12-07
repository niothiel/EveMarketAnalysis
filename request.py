#/usr/bin/python
import urllib2
import xml.etree.ElementTree as ET

statStr = 'http://api.eve-central.com/api/marketstat?typeid=%d&usesystem=30002510'
nameStr = 'http://api.eve-central.com/api/quicklook?typeid=%d'

typeToName = {}

class MarketItem:
	def __init__(self):
		self.name = None
		self.buyVolume = 0
		self.buyPrice = 0
		self.sellVolume = 0
		self.sellPrice = 0
		self.totalVolume = 0
		self.priceDifference = 0
		self.volumeDifference = 0

	def __repr__(self):
		s = self.name + '\n'
		s += 'Buy: ' + str(self.buyVolume) + ' @ ' + str(self.buyPrice) + '\n'
		s += 'Sell: ' + str(self.sellVolume) + ' @ ' + str(self.sellPrice) + '\n'
		s += 'Price Difference: ' + str(self.priceDifference) + '\n'
		s += 'Volume Difference: ' + str(self.volumeDifference)
		return s

	def __str__(self):
		return self.__repr__()

def initTypeToNameDB():
	f = open('typeid.txt', 'r')
	for line in f:
		splitString = line.split('     ', 1)
		typeId = splitString[0].strip()
		name = splitString[1].strip()
		typeToName[typeId] = name

def getItemName(typeId):
	if str(typeId) in typeToName:
		return typeToName[str(typeId)]
	else:
		return None

def getItemName2(typeId):
	nameUrl = nameStr % typeId
	try:
		nameHtml = urllib2.urlopen(nameUrl).read()
	except:
		print 'Invalid typeid:', typeId
		return

	return ET.fromstring(nameHtml)[0].find('itemname').text

def getItem(typeId=34):
	print "Getting item id... ", typeId
	if getItemName(typeId) == None:
		return

	statUrl = statStr % typeId

	try:
		statHtml = urllib2.urlopen(statUrl).read()
	except:
		print 'Invalid typeid:', typeId
		return

	root = ET.fromstring(statHtml)[0][0]

	buyNode = root.find('buy')
	sellNode = root.find('sell')
	allNode = root.find('all')

	m = MarketItem()
	m.name = getItemName(typeId)
	m.buyVolume = int(buyNode.find('volume').text)
	m.buyPrice = float(buyNode.find('max').text)
	m.sellVolume = int(sellNode.find('volume').text)
	m.sellPrice = float(sellNode.find('min').text)
	m.totalVolume = int(allNode.find('volume').text)

	if m.buyVolume == 0 or m.buyPrice == 0 or m.sellVolume == 0 or m.sellPrice == 0:
		m.priceDifference = 0
		m.volumeDifference = 0
	else:
		m.priceDifference = abs(m.buyPrice - m.sellPrice) / m.buyPrice * 100
		m.volumeDifference = abs(m.buyVolume - m.sellVolume) / float(m.buyVolume) * 100

	return m

initTypeToNameDB()

itemList = []
for id in range(34, 41) + range(178, 202):
	item = getItem(id)
	itemList.append(item)
#	print item

def itemCriteria(item):
	# Criteria for getting rid of items you don't like.
	if item.priceDifference > 20:
		return True
	else:
		return False

culledList = filter(itemCriteria, itemList)
sortedList = sorted(culledList, key=lambda item: item.priceDifference)

for item in sortedList:
	print item

exit(1)
