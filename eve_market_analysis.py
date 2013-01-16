from eve_central import EVECentral
from eve_marketdata import EVEMarketData
from pprint import pprint
from util import chunks, formatNum
from request import getItemName, getItems
import datetime
from cache import ShelfCache

def avg(l):
	if l is None:
		return 0.0

	total = 0.0
	n = 0
	for item in l:
		total += item
		n += 1

	if n == 0:
		return 0.0

	return total / n

def check_item(type_id, history, f):
	total_average = 0.0
	total_volume = 0.0

	# Grab the average volume and price
	average_price_per_day = avg(statistic['avgPrice'] for statistic in history.itervalues())
	average_volume_per_day = avg(statistic['volume'] for statistic in history.itervalues())

	percent_price_cutoff = 0.7
	n_lookback_days = 6

	lookback_average = avg([statistic['avgPrice'] for date, statistic in history.iteritems() if (datetime.date.today() - date).days < n_lookback_days])

	if lookback_average == 0:
		return

	price_cutoff = average_price_per_day * percent_price_cutoff
	item_name = getItemName(type_id) or ''

	if lookback_average < price_cutoff and 'Blueprint' not in item_name and average_price_per_day > 30000 and average_volume_per_day > 5:
		print type_id, ':', item_name
		print 'Average Price:', formatNum(average_price_per_day)
		print 'Average Volume Per Day:', average_volume_per_day
		print 'Last 5 days average:', formatNum(lookback_average)
		print ''

		f.write(str(type_id))
		f.write('\t')
		f.write(item_name)
		f.write('\t')
		f.write(str(average_price_per_day))
		f.write('\t')
		f.write(str(average_volume_per_day))
		f.write('\t')
		f.write(str(lookback_average))
		f.write('\n')
		f.flush()

def main():
	eveCentral = EVECentral()
	eveMarketData = EVEMarketData('asdf')

	days = 90
	chunk_size = 10000 / days
	print 'Using chunk size:', chunk_size

	f = open('lti.csv', 'w')
	f.write('type_id\taverage_90d_price_per_day\taverage_90d_volume_per_day\t5d_lookback_average_price\n')
	for chunk in chunks(range(1, 34000), chunk_size):
		chunk_of_hist = eveMarketData.item_price_history(chunk, [10000002], days)

		for type_id, history in chunk_of_hist.iteritems():
			check_item(type_id, history, f)

		#print chunk[0], chunk[-1]

	#asdf = eveMarketData.item_price_history([34], [10000002], 90)
	#pprint(asdf)

if __name__ == '__main__':
	main()