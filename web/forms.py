from flask.ext.wtf import Form, TextField, BooleanField, RadioField
from flask.ext.wtf import Required

class MarketSelectForm(Form):
	#name = TextField('name', validators = [Required()])
	sort = RadioField('sort', choices=[
		('profit', 'Profit'),
		('volume', 'Volume'),
		('pricediff', 'Price Difference')])