from datetime import datetime, time, timedelta
import gzip
import os
import urllib2

try:
    import MySQLdb
except:
    print 'Failed to import MySQL Library!'

class Order:
	def __init__(self):
		self.orderid = -1
		self.regionid = -1
		self.systemid = -1
		self.stationid = -1
		self.typeid = -1
		self.bid = -1
		self.price = -1
		self.minvolume = -1
		self.volremain = -1
		self.volenter = -1
		self.issued = -1
		self.duration = -1
		self.range = -1
		self.reportedby = -1
		self.reportedtime = -1
	
	def __repr__(self):
		s = ''
		s += str(self.orderid)			+ ','
		s += str(self.regionid)			+ ','
		s += str(self.systemid)			+ ','
		s += str(self.stationid)		+ ','
		s += str(self.typeid)			+ ','
		s += str(self.bid)				+ ','
		s += str(self.price)			+ ','
		s += str(self.minvolume)		+ ','
		s += str(self.volremain)		+ ','
		s += str(self.volenter)			+ ','
		s += '\'' + str(self.issued)	+ '\','
		s += '\'' + str(self.duration)	+ '\','
		s += str(self.range)			+ ','
		s += str(self.reportedby)		+ ','
		s += '\'' + str(self.reportedtime) + '\''
		return s

	def __str__(self):
		return self.__repr__()
	
	def getTags(self):
		return 'orderid,regionid,systemid,stationid,typeid,bid,price,minvolume,volremain,volenter,issued,duration,rng,reportedby,reportedtime'

class OrdersTable:
	def __init__(self):
		self.conn = MySQLdb.connect(host = '10.10.10.250', user = 'root', passwd = '', db = 'eve')
		
		self.daysKept = 3
		
		self.create()
		#self.prune()
		self.update()
		
	def getCursor(self):
		return self.conn.cursor()
	
	def create(self):
		cursor = self.getCursor()
		cursor.execute('''CREATE TABLE IF NOT EXISTS orders(orderid BIGINT, regionid INTEGER, systemid INTEGER, stationid INTEGER, typeid INTEGER, bid REAL, price REAL, minvolume INTEGER, volremain INTEGER, volenter INTEGER, issued DATETIME, duration TEXT, rng INTEGER, reportedby INTEGER, reportedtime DATETIME, INDEX reportedtime (reportedtime));''')
	
	def delete(self):
		cursor = self.getCursor()
		cursor.execute('''DROP TABLE IF EXISTS orders;''')
		
	def show(self):
		cursor = self.getCursor()
		orderList = cursor.execute('SELECT * FROM orders;')
		
		print 'The orders table looks as follows:'
		for order in orderList:
			print order
	
	def prune(self):
		print 'Pruning database... ',
		utcTime = datetime.utcnow()
		cullDate = utcTime - timedelta(days=self.daysKept)
		cursor = self.getCursor()
		sql = '''DELETE FROM orders WHERE reportedtime < \'%d-%02d-%02d\';''' % (cullDate.year, cullDate.month, cullDate.day)
		cursor.execute(sql)
		print 'Done!'
		
	def hasDate(self, date):
		cursor = self.getCursor()
		dateStr = '%d-%02d-%02d' % (date.year, date.month, date.day)
		
		sql = '''SELECT EXISTS (SELECT 1 FROM orders WHERE reportedtime BETWEEN '{0}' AND '{0} 23:59:59');'''.format(dateStr)
		cursor.execute(sql)
		result = cursor.fetchone()[0]
		return result <> 0
	
	def importData(self, dayDate):
		dateStr = '%d-%02d-%02d' % (dayDate.year, dayDate.month, dayDate.day)
		unzippedFilename = '%s.dump' % dateStr
		zippedFilename = unzippedFilename + '.gz'
		csvFilename = '%s.csv' % dateStr
		
		url = 'http://eve-central.com/dumps/' + zippedFilename
		
		if not os.path.exists('data/' + unzippedFilename):
			if not os.path.exists('data/' + zippedFilename):
				print 'Downloading:', url
				zippedDump = urllib2.urlopen(url).read()
				
				if '<html>' in zippedDump:
					print 'Failed to download data!'
					return
				
				f = open('data/' + zippedFilename, 'wb')
				f.write(zippedDump)
				f.close()
			
			print 'Unzipping...'
			unzippedDump = gzip.open('data/' + zippedFilename)
			f = open('data/' + unzippedFilename, 'w')
			
			chunkData = unzippedDump.read(4 * 1024)
			while chunkData <> '':
				f.write(chunkData)
				chunkData = unzippedDump.read(4 * 1024)
			
			f.close()
			unzippedDump.close()
		
		if not os.path.exists('data/' + csvFilename):
			print 'Writing out proper csv file.'
			with open('data/' + unzippedFilename, 'r') as fin, open('data/' + csvFilename, 'w') as fout:
				header = fin.readline().strip().replace('"', '')
				#fout.write(header + '\n') #Not sure if we want the header, I'll say that we don't.
				
				for line in fin:
					line = line.replace(',', '').strip()
					line = [x for x in line.split('"') if x]
					line[-1] = line[-1].split('.')[0]			# Get rid of the fractional seconds from the reportedtime
					
					line = ','.join(line)
					fout.write(line)
					fout.write('\n')
		
		self.importCsv('data/' + csvFilename)
		
	def importCsv(self, fileName):
		print 'Importing: ', fileName
		
		startTime = datetime.now()
		cur = self.getCursor();
		sql = 'LOAD DATA LOCAL INFILE \'%s\' INTO TABLE orders FIELDS TERMINATED BY \',\' LINES TERMINATED BY \'\\n\';' % fileName
		cur.execute(sql)
		
		print 'Done importing.'
		print 'Elapsed: ', (datetime.now() - startTime)
	
	def update(self):
		# Check if we have the last [self.daysKept] records in the database
		for x in range(1, self.daysKept + 1):
			day = datetime.utcnow() - timedelta(days=x)
			day = day - timedelta(hours=4)		# Give them more time to upload the data by going back further on the day
			if not self.hasDate(day):
				print 'We need', day
				self.importData(day)
				
	def getJitaVolumesLastDay(self):
		cur = self.getCursor()
		
		date = datetime.utcnow() - timedelta(days=1)
		
		while not self.hasDate(date):
			date -= timedelta(days=1)
		
		dateStr = '%d-%02d-%02d' % (date.year, date.month, date.day)
		sql = '''SELECT typeid,bid,SUM(numsold) FROM (SELECT typeid,orderid,bid,MAX(volremain)-MIN(volremain) AS numsold FROM orders WHERE reportedtime BETWEEN '{0}' AND '{0} 23:59:59' AND regionid=10000002 GROUP BY typeid,orderid,bid) AS t WHERE numsold<>0 GROUP BY typeid,bid;'''.format(dateStr)
		cur.execute(sql)
		
		volumesDict = {}
		
		for entry in cur:
			typeId = entry[0]
			
			if typeId not in volumesDict.keys():
				volumesDict[typeId] = {}
			
			volume = int(entry[2])
			if entry[1] == 1:
				volumesDict[typeId]['buy'] = volume
			else:
				volumesDict[typeId]['sell'] = volume
				
		return volumesDict