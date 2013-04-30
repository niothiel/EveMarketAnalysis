import os
import pickle

from flask import render_template, flash, redirect, request
from web import app
from forms import MarketSelectForm
from market.priceservice import PriceService
from eos.db.gamedata.queries import getMarketGroupItems

# TODO: I'm a bad person for writing it like this.
itemcategory_map_filename = 'data/itemcategory_map.pickle'
if not os.path.exists(itemcategory_map_filename):
	itemcategories = [
		'Ammunition & Charges',
		'Blueprints',
		'Drones',
		'Implants & Boosters',
		'Manufacture & Research',
		'Ships',
		'Ship Equipment',
		'Ship Modifications',
		'Skills'
	]
	itemcategory_map = {category: getMarketGroupItems(category) for category in itemcategories}
	with open(itemcategory_map_filename, 'wb') as fout:
		pickle.dump(itemcategory_map, fout)
with open(itemcategory_map_filename, 'rb') as fin:
	itemcategory_map = pickle.load(fin)

def filter_price(price, form):
	if price.buy.max < form.minprice.data:
		return False

	if price.sell.min < form.minprice.data:
		return False

	if form.maxprice.data > 0 and price.buy.max > form.maxprice.data:
		return False

	if form.maxprice.data > 0 and price.sell.min > form.maxprice.data:
		return False

	if price.profit() < form.minprofit.data:
		return False

	if form.maxprofit.data > 0 and price.profit() > form.maxprofit.data:
		return False

	if form.maxvolume.data > 0 and price.all.volume > form.maxvolume.data:
		return False

	if price.all.volume < form.minvolume.data:
		return False

	return True

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html')

@app.route('/daytrading', methods = ['GET', 'POST'])
def daytrading():

	form = MarketSelectForm()
	prices = None
	if form.validate_on_submit():
		typeids_to_search = set()
		if form.cat_ammo.data:
			typeids_to_search.update(itemcategory_map.get('Ammunition & Charges'))
		if form.cat_blueprints.data:
			typeids_to_search.update(itemcategory_map.get('Blueprints'))
		if form.cat_drones.data:
			typeids_to_search.update(itemcategory_map.get('Drones'))
		if form.cat_implants.data:
			typeids_to_search.update(itemcategory_map.get('Implants & Boosters'))
		if form.cat_materials.data:
			typeids_to_search.update(itemcategory_map.get('Manufacture & Research'))
		if form.cat_ships.data:
			typeids_to_search.update(itemcategory_map.get('Ships'))
		if form.cat_modules.data:
			typeids_to_search.update(itemcategory_map.get('Ship Equipment'))
		if form.cat_rigs.data:
			typeids_to_search.update(itemcategory_map.get('Ship Modifications'))
		if form.cat_skillbooks.data:
			typeids_to_search.update(itemcategory_map.get('Skills'))

		form.minprofit.data /= 100.0
		form.maxprofit.data /= 100.0
		form.volume_moved.data /= 100.0
		form.investment.data *= 1000000

		# Check to make sure the data's been loaded
		if PriceService.prices:
			prices = PriceService.prices.copy()
			prices = prices[form.tradehub.data]
			prices = [prices[id] for id in typeids_to_search]

			for price in prices:
				price.img_url = '/static/img/eve/%d_32.png' % price.id
				price.investment = None

				if form.ranking.data == 'profitbyvol':
					price.rank = price.profit() * price.all.volume
				elif form.ranking.data == 'profitdivvol':
					if price.all.volume == 0:
						price.rank = 0
					else:
						price.rank = price.profit() / price.all.volume
				elif form.ranking.data == 'chrisrank':
					required_investment = price.buy.max * price.all.volume * float(form.volume_moved.data)
					profit = (price.sell.min - price.buy.max)
					if form.investment.data < price.buy.max:
						price.rank = 0
					elif required_investment > form.investment.data:
						price.rank = form.investment.data / price.buy.max * profit
					else:
						price.rank = price.all.volume * float(form.volume_moved.data) * profit
					price.rank /= 1000000

					price.investment = required_investment / form.investment.data * 100
					if price.investment > 100:
						price.investment = 100

			prices = [price for price in prices if filter_price(price, form)]
			prices = sorted(prices, key=lambda price: price.rank, reverse=True)
			prices = prices[:min(500, len(prices))]
	return render_template('daytrading.html',
		title = 'Daytrading',
		form = form,
		prices = prices,
		time_updated = PriceService.time_updated)

@app.route('/marketscan', methods=['GET', 'POST'])
def marketscan():
	igb = 'EVE-IGB' in request.user_agent.string
	trusted = igb and request.headers.get('Eve-Trusted') == 'Yes'

	print dir(request.headers)
	print request.headers
	return render_template('marketscan.html',
		igb = igb,
		trusted = trusted)