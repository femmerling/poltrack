from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

from app import main, models

app.secret_key = "xdexedq1xa0RIxf0xff-HWx86Bx94xbfZSDxcaxf7xc7fff"
