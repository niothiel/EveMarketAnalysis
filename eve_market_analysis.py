from eve_central import EVECentral
from eve_marketdata import EVEMarketData
from pprint import pprint

def main():
	eveCentral = EVECentral()
	eveMarketData = EVEMarketData('asdf')

	#asdf = eveMarketData.item_prices([34])
	#pprint(asdf)
	asdf = eveMarketData.item_orders([34])
	pprint(asdf)
	asdf = eveMarketData.item_price_history([34], [10000002])
	pprint(asdf)


if __name__ == '__main__':
	main()