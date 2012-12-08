import sys
# 0: "orderid",
# 1: "regionid",
# 2: "systemid",
# 3: "stationid",
# 4: "typeid",
# 5: "bid",
# 6: "price",
# 7: "minvolume",
# 8: "volremain",
# 9: "volenter",
# 10: "issued",
# 11: "duration",
# 12: "range",
# 13: "reportedby",
# 14: "reportedtime"

# Returns a dict with all the data of the order.
def parseLine(line, lookup):
	line = line.replace('"', '').strip()
	splitLine = line.split(',')
	
	# Remove the weird ass element that probably shouldn't be there.
	splitLine.pop(12)

	order = {}
	for i, elem in enumerate(splitLine):
		order[lookup[i]] = elem
	
	return order

def getLookup(firstLine):
	firstLine = firstLine.replace('"', '').strip()
	lookup = firstLine.split(',')
	return lookup
	
def processDumpFile(fileName):
	f = open(fileName, 'r')

	line = f.readline()
	lookup = getLookup(line)
	
	orderIds = []
	orderDict = {}
	for line in f:
		order = parseLine(line, lookup)
		
		# Do fun stuff with the order here
		if order['orderid'] not in orderDict:
			orderDict[order['orderid']] = []
		
		orderDict[order['orderid']].append(order)
	
	totalSold = 0
	for k, orders in orderDict.items():
		orders = sorted(orders, key=lambda order: order['reportedtime'])
		numberSold = int(orders[0]['volremain']) - int(orders[-1]['volremain'])
		totalSold += numberSold
		print k, numberSold
	
	print 'Total Sold: ', totalSold
	
def cullDb(inFile, outFile, cullFunc):
	f = open(inFile, 'r')
	o = open(outFile, 'w')
	
	header = f.readline()
	o.write(header)
	
	for line in f:
		if cullFunc(line):
			o.write(line)
			
	f.close()
	o.flush()
	o.close()

def cullJitaTrit(line):
	splitLine = line.split(',')
	
	if splitLine[4] <> '"34"':
		return False
	if splitLine[1] <> '"10000002"':
		return False
	
	return True
		
def main():
	processDumpFile('2012-12-07JitaCull.dump')
	#cullDb('2012-12-07.dump', '2012-12-07JitaCull.dump', cullJitaTrit)
	
if __name__ == '__main__':
	main()