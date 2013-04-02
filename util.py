from urllib import urlencode
import datetime
import urllib2

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