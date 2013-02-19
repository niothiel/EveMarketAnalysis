from datetime import date, timedelta, datetime
from pprint import pprint

import csv
import gzip
import MySQLdb
import os
import urllib
import util

class OrderHistoryImporter:
	def __init__(self, db=None, directory='.\data'):
		if db is None:
			self.db = MySQLdb.connect(host='127.0.0.1', user='root', passwd='asdf', db='eve')
		else:
			self.db = db

		# Make sure the tables are actually created.
		schemasql = self._getsql('orderhistory_schema')
		self.db.cursor().execute(schemasql)
		self.db.commit()

		self.directory = directory

	def download(self, day):
		daystr = day.isoformat()

		zipped_filename = '%s.dump.gz' % daystr
		zipped_path = os.path.join(self.directory, zipped_filename)
		if not os.path.exists(zipped_path):
			base_url = 'http://eve-central.com/dumps/'

			if day.year <> date.today().year:
				base_url += '%d/' % day.year

			base_url += daystr + '.dump.gz'

			print 'Downloading...'
			try:
				# TODO: Can use reporthook parameter to keep track of progress.
				urllib.urlretrieve(base_url, zipped_path)
			except:
				print 'Couldn\'t download the data, it probably doesn\'t exist yet.'
				return False

			with open(zipped_path, 'r') as fin:
				if '404' in fin.read():
					# File in use error.
					#os.remove(zipped_path)
					return False


		return True

	def unzip(self, day):
		daystr = day.isoformat()
		zipped_filename = '%s.dump.gz' % daystr
		zipped_path = os.path.join(self.directory, zipped_filename)

		unzipped_filename = '%s.dump' % daystr
		unzipped_path = os.path.join(self.directory, unzipped_filename)
		if not os.path.exists(unzipped_path):
			with gzip.open(zipped_path, 'rb') as fin:
				with open(unzipped_path, 'wb') as fout:
					print 'Unzipping...'

					# Do it by chunks so we don't have any memory problems.
					chunksize = 1024 * 1024 * 4
					buffer = fin.read(chunksize)

					while buffer:
						fout.write(buffer)
						buffer = fin.read(chunksize)
		# Delete the zipped file
		#os.remove(zipped_path)

	def insert_csv(self, day):
		cursor = self.db.cursor()

		cursor.execute('DROP TABLE IF EXISTS orders;')
		schemasql = self._getsql('orders_schema')
		cursor.execute(schemasql)

		daystr = day.isoformat()
		filename = '%s.dump' % daystr

		# Create and sanitize the path
		path = os.path.join(self.directory, filename)
		path = os.path.abspath(path)

		regular_path = path
		path = path.replace('\\', '\\\\')

		importsql = self._getsql('import') % path
		print 'Importing CSV...'
		cursor.execute(importsql)
		self.db.commit()

		os.remove(regular_path)

	def analyze(self, day):
		cursor = self.db.cursor()

		sql = self._getsql('holygrail') % day.isoformat()
		numrows = cursor.execute(sql)
		self.db.commit()
		print 'Imported Rows:', numrows

	def import_day(self, day):
		start_time = datetime.now()
		daystr = day.isoformat()
		print 'Processing', daystr

		if self.day_exists(day):
			print 'Day is already in the order history! Nothing imported'
			return

		if not self.download(day):
			return False

		self.unzip(day)
		self.insert_csv(day)
		self.analyze(day)

		total_time = datetime.now() - start_time
		print 'Importing took:', total_time

	def day_exists(self, day):
		sql = 'SELECT COUNT(*) FROM orderhistory WHERE dateposted=\'%s\'' % day.isoformat()
		cursor = self.db.cursor()
		cursor.execute(sql)

		return cursor.fetchone()[0] > 0

	def _getsql(self, name):
		filename = '%s.sql' % name
		path = os.path.join('sql', filename)
		with open(path, 'r') as fin:
			return fin.read()

def main():
	#with open('data\\2013-01-22.dump', 'r') as fin:
	#	for x in range(10):
	#		print fin.readline()

	dl = OrderHistoryImporter()
	lookback_days = 90

	for day_delta in range(0, lookback_days + 1):
		td = timedelta(days=day_delta)
		day = date.today() - td
		dl.import_day(day)

if __name__ == '__main__':
	main()
