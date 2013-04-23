from flask import Flask
from market.priceservice import PriceService
from momentjs import momentjs

PriceService.start()

app = Flask(__name__)
app.config.from_object('config')
app.jinja_env.globals['momentjs'] = momentjs

from web import views