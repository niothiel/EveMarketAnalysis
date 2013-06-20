from flask import Flask
from momentjs import momentjs

app = Flask(__name__)
app.config.from_object('config')
app.jinja_env.globals['momentjs'] = momentjs

from web import views