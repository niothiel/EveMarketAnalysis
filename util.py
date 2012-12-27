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