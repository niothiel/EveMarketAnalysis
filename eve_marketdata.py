
import json
import urllib
from util import smart_parse

try:
	import urllib2
except ImportError:
	urllib2 = None

class EVEMarketData(object):
	BUY = 'b'
	SELL = 's'
	BUYSELL = 'a'

	def __init__(self, char_name, url_fetch_func=None,
	             api_base='http://api.eve-marketdata.com/api'):
		super(EVEMarketData, self).__init__()

		self.api_base = api_base
		self.char_name = char_name

		if url_fetch_func is not None:
			self.url_fetch = url_fetch_func
		elif urllib2 is not None:
			self.url_fetch = self._default_fetch_func
		else:
			raise ValueError("urllib2 not available - specify url_fetch_func")

	def _default_fetch_func(self, url):
		"""Fetches a given URL using GET and returns the response."""
		return urllib2.urlopen(url).read()

	def _get_html(self, api_string, params):
		query = urllib.urlencode(params)
		url = '%s/%s?%s' % (self.api_base, api_string, query)
		return self.url_fetch(url)

	def item_prices(self, type_ids, order_type=None, marketgroups=None, regions=None, systems=None, stations=None,
	                 min_values=None):
		"""Returns the 'best guess' for item prices

		Optional filters:
			ordertype (BUY, SELL, BUYSELL) - Type of information to return.
			marketgroups (int) - Market group for selecting specific items.
			regions (list of ints) - Region id(s) for which to compute stats.
			systems (list of ints) - System id for which to compute stats.
			stations (list of ints) - Stations for which to get prices.
			min_values (True, False) - Whether to include min/max values for the computation.
		"""

		order_type = order_type or EVEMarketData.BUYSELL

		params = {
			'char_name': self.char_name,
			'buysell': order_type,
			'type_ids': ','.join(str(x) for x in type_ids)}
		if marketgroups:
			params['marketgroup_ids'] = ','.join(str(x) for x in marketgroups)
		if regions:
			params['region_ids'] = ','.join(str(x) for x in regions)
		if systems:
			params['solarsystem_ids'] = ','.join(str(x) for x in systems)
		if stations:
			params['station_ids'] = ','.join(str(x) for x in stations)
		if min_values:
			params['minmax'] = 'min' if min_values else 'max'

		response = self._get_html('item_prices2.json', params)
		api_result = json.loads(response)['emd']

		results = {}
		for row in api_result['result']:
			row = row['row']

			for key, value in row.iteritems():
				row[key] = smart_parse(value)

			results[row['typeID']] = row
		return results

	def item_market_stats(self, type_id, *args, **kwargs):
		"""Fetch market statistics for a single item.

		(Convenience wrapper for item_prices.)
		"""
		return self.item_prices([type_id], *args, **kwargs)[int(type_id)]

	def item_orders(self, type_ids, order_type=None, marketgroups=None, regions=None, systems=None, stations=None):
		"""Fetches market orders for a given item.

		Optional filters:
			ordertype (BUY, SELL, BUYSELL) - Type of information to return.
			marketgroups (int) - Market group for selecting specific items.
			regions (list of ints) - Region id(s) for which to compute stats.
			systems (list of ints) - System id for which to compute stats.
			stations (list of ints) - Stations for which to get prices.
		"""

		order_type = order_type or EVEMarketData.BUYSELL

		params = {
			'char_name': self.char_name,
			'buysell': order_type,
			'type_ids': ','.join(str(x) for x in type_ids)
		}
		if marketgroups:
			params['marketgroup_ids'] = ','.join(str(x) for x in marketgroups)
		if regions:
			params['region_ids'] = ','.join(str(x) for x in regions)
		if systems:
			params['solarsystem_ids'] = ','.join(str(x) for x in systems)
		if stations:
			params['station_ids'] = ','.join(str(x) for x in stations)

		response = self._get_html('item_orders2.json', params)
		api_result = json.loads(response)['emd']

		results = {}
		for row in api_result['result']:
			row = row['row']

			for key, value in row.iteritems():
				row[key] = smart_parse(value)

			type_id = row['typeID']
			itemList = results.setdefault(type_id, [])
			itemList.append(row)
		return results

	def item_price_history(self, type_ids, regions, days=30):
		"""Gets the price history for items, same as the 'Show Table' tab in game.

		Optional filters:
			days (int) - Number of days to show price history for.
			stations (list of ints) - Stations for which to get prices.
			min_values (True, False) - Whether to include min/max values for the computation.
		"""

		params = {
			'char_name': self.char_name,
			'type_ids': ','.join(str(x) for x in type_ids),
		    'region_ids': ','.join(str(x) for x in regions)
		}
		if days:
			params['days'] = days

		response = self._get_html('item_history2.json', params)
		api_result = json.loads(response)['emd']

		results = {}
		for row in api_result['result']:
			row = row['row']

			for key, value in row.iteritems():
				row[key] = smart_parse(value)

			type_id = row['typeID']
			typeDict = results.setdefault(type_id, {})
			typeDict[row['date']] = row
		return results

		# vim: set et ts=4 sts=4 sw=4: