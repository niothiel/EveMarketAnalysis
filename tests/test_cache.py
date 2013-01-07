from datetime import datetime, timedelta
import unittest
import cache

class TestCache(unittest.TestCase):
	def setUp(self):
		self.c = []
		self.c.append(cache.GenericCache())
		self.c.append(cache.ShelfCache('test_shelfcache.db'))

	def test(self):
		for cache in self.c:
			cache.set('a', 5)
			self.assertEqual(cache.get('a'), 5)
			self.assertIsNone(cache.get('b'))

			hold_time = timedelta(seconds=3)
			cache.set('asdf', 15, hold_time)
			self.assertEqual(cache.get('asdf'), 15)

			end_time = datetime.now() + hold_time + timedelta(seconds=1)
			while datetime.now() < end_time:
				pass

			self.assertIsNone(cache.get('asdf'))
