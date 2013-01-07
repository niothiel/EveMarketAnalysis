from datetime import datetime, timedelta
import shelve

class GenericCache:
	def __init__(self):
		self.cache = {}

	def get(self, key):
		if key not in self.cache:
			return None

		expiration_time, value = self.cache[key]
		if expiration_time < datetime.now():
			del self.cache[key]
			return None

		return value

	def set(self, key, value, hold_time=timedelta(minutes=15)):
		expiration_time = datetime.now() + hold_time
		self.cache[key] = (expiration_time, value)

class ShelfCache(GenericCache):
	def __init__(self, filename):
		self.cache = shelve.open(filename)