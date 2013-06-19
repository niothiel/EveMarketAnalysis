import datetime
import decimal
import urllib2
from urllib import urlencode
from datetime import datetime

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

def downloadFile(url, destination):
	import urllib2
	u = urllib2.urlopen(url)
	with open(destination, 'wb') as f:
		meta = u.info()
		file_size = int(meta.getheaders("Content-Length")[0])
		print "Downloading: %s, %.1f MB" % (url.split('/')[-1], file_size / 1024.0 / 1024.0)

		file_size_dl = 0
		block_sz = 8192

		print_time = datetime.now()
		while True:
			buffer = u.read(block_sz)
			if not buffer:
				break

			file_size_dl += len(buffer)
			f.write(buffer)

			if (datetime.now() - print_time).total_seconds() > 1:
				status = "[%3.2f%%]\r" % (file_size_dl * 100. / file_size)
				print status
				print_time = datetime.now()