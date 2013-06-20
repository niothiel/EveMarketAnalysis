from web import app
from market.priceservice import PriceService

# Kick off the price service.
PriceService.start()
from threading import Thread
from market.emdr import emdr_service
thread = Thread(target=emdr_service)

# Dummy call for strptime due to a bug in python regarding threading.
# The error: failed to import _strptime because the import lock is held by another thread
import datetime
datetime.datetime.strptime('2013-01-01', '%Y-%m-%d')
thread.start()

app.run(host='0.0.0.0', debug = True, use_reloader=False)