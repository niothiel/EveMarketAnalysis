from flask import render_template, flash, redirect
from web import app
from forms import MarketSelectForm

from market.evecentral import EveCentral

@app.route('/', methods = ['GET', 'POST'])
@app.route('/index', methods = ['GET', 'POST'])
def index():
	form = MarketSelectForm()
	prices = None
	if form.validate_on_submit():
		prices = EveCentral.getPrices(range(1, 2000)).values()
		prices = sorted(prices, key=lambda item: item.profit(), reverse=True)
		print prices[:10]


	return render_template('index.html',
		title = 'Home',
		form = form,
		prices = prices)