from flask import Flask
from momentjs import momentjs
import util

app = Flask(__name__)
app.config.from_object('config')
app.jinja_env.globals['momentjs'] = momentjs
app.jinja_env.globals['numFormat'] = util.numFormat

from web import views