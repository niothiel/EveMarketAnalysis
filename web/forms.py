from flask.ext.wtf import Form, IntegerField, TextField, BooleanField, RadioField, SelectField
from market.priceservice import trade_hubs
from flask.ext.wtf import Required

class MarketSelectForm(Form):
	ranking = SelectField('Rank Algorithm', choices=[
		('profitbyvol', 'Profit * Volume'),
	    ('profitdivvol', 'Profit / Volume'),
	    ('chrisrank', 'Chris\'s Ranking')
	])
	tradehub = SelectField('Trade Hub', choices=zip(trade_hubs, trade_hubs))
	#tradehub = SelectField('Trade Hub', choices=[
	#	('Jita', 'Jita')
	#])
	investment = IntegerField('Investment (Millions)', default=50)
	volume_moved = IntegerField('Volume Moved (%)', default=10)
	minprice = IntegerField('Minimum Price', default=1)
	maxprice = IntegerField('Maximum Price', default=8000000000)
	minprofit = IntegerField('Minimum Profit', default=0)
	maxprofit = IntegerField('Maximum Profit', default=1000)
	minvolume = IntegerField('Minimum Volume', default=0)
	maxvolume = IntegerField('Maximum Volume', default=0)
	#exclude_bogus = BooleanField('Exclude Bogus Entries (Price < 1 or Profit > 1000%)', default=True)
	cat_ammo = BooleanField('Ammo and Charges', default=True)
	cat_blueprints = BooleanField('Blueprints')
	cat_drones = BooleanField('Drones', default=True)
	cat_implants = BooleanField('Implants and Boosters', default=True)
	cat_materials = BooleanField('Materials / PI', default=True)
	cat_ships = BooleanField('Ships', default=True)
	cat_modules = BooleanField('Modules', default=True)
	cat_rigs = BooleanField('Rigs', default=True)
	cat_skillbooks = BooleanField('Skillbooks', default=True)
