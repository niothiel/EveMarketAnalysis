from urllib import urlencode
import datetime
import urllib2

def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def formatNum(price):
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

def smart_parse(value):
	try:
		return int(value)
	except:
		pass

	try:
		return float(value)
	except:
		pass
	try:
		return datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
	except:
		pass
	try:
		return datetime.datetime.strptime(value, '%Y-%m-%d').date()
	except:
		pass
	return value