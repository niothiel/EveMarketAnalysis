import datetime
import time
import threading
from evecentral import EveCentral

class PriceService:
	prices = None
	thread = None
	time_updated = None

	@classmethod
	def start(cls, time_interval=15 * 60):
		if PriceService.thread is None:
			PriceService.thread = PriceService.PriceThread(time_interval)

		if not PriceService.thread.is_alive():
			PriceService.thread.start()

	@classmethod
	def stop(cls):
		pass # Any point in having this? Dunno.

	class PriceThread(threading.Thread):
		def __init__(self, time_interval):
			super(PriceService.PriceThread, self).__init__()
			self.time_interval = time_interval

		def run(self):
			print 'Thread Started!'
			while True:
				try:
					temp_prices = EveCentral.getPrices()
				except:
					time.sleep(2 * 60)
					continue
				PriceService.prices = temp_prices   # Atomic, thread-safe update... hopefully.
				PriceService.time_updated = datetime.datetime.utcnow()
				time.sleep(self.time_interval)
