import datetime
import decimal
import urllib2
from urllib import urlencode

def chunks(l, n):
	""" Yield successive n-sized chunks from l.
	"""
	for i in xrange(0, len(l), n):
		yield l[i:i+n]

def formatIsk(price):
	if price < 1000:
		return str(price)
	if price < 1000000:
		return '%.1fk' % (price / 1000)

	return '%.1fM' % (price / 1000000)

def htmlFromUrl(url, params = {}):
	if params <> {}:
		if url[-1] <> '?':
			url += '?'

		params = urlencode(params)
		url += params

	html = urllib2.urlopen(url).read()
	return html

def parse_isodate(date_str):
	# u'2013-03-29T18:00:07+00:00'
	# Parse the date minus UTC offset.
	dt = datetime.datetime.strptime(date_str[:-6], '%Y-%m-%dT%H:%M:%S')

	# Parse UTC offset
	hours, mins = date_str[-5:].split(':')
	td = datetime.timedelta(hours=int(hours), minutes=int(mins))

	# Correct for offset
	if date_str[-6] == '+':
		dt += td
	else:
		dt -= td

	return dt

def smart_parse(value, int=True, float=True, isoTime=True, isoDate=True):
	if int:
		try:
			return int(value)
		except:
			pass
	if float:
		try:
			return float(value)
		except:
			pass
	if isoTime:
		try:
			return datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
		except:
			pass
	if isoDate:
		try:
			return datetime.datetime.strptime(value, '%Y-%m-%d').date()
		except:
			pass

	# If we get here, we don't know what the type is, so we just return what we were given.
	return value

def floorFloat(value):
	"""Round float down to integer"""
	# We have to convert float to str to keep compatibility with
	# decimal module in python 2.6
	value = str(value)
	# Do the conversions for proper rounding down, avoiding float
	# representation errors
	result = int(decimal.Decimal(value).to_integral_value(rounding=decimal.ROUND_DOWN))
	return result