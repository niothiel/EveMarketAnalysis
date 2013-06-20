import datetime
import time
import threading
from evecentral import EveCentral

trade_hubs = [
	'Jita'
    #'Amarr',
    #'Rens',
    #'Dodixie',
    #'Hek'
]

class PriceService:
	prices = None
	thread = None
	time_updated = None

	@classmethod
	def start(cls, time_interval=7 * 60):
		PriceService.thread = PriceService.PriceThread(time_interval)
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
					#temp_prices = EveCentral.getPrices()
					temp_prices = {}
					for hub in trade_hubs:
						print 'Getting prices in:', hub
						start = datetime.datetime.now()
						temp_prices[hub] = EveCentral.getPrices(system=hub)
						print 'Finished in:', (datetime.datetime.now() - start)

				except Exception as e:
					print 'Error getting data from prices...', e
					exit(1)
					time.sleep(2 * 60)
					continue
				PriceService.prices = temp_prices   # Atomic, thread-safe update... hopefully.
				PriceService.time_updated = datetime.datetime.utcnow()
				time.sleep(self.time_interval)
