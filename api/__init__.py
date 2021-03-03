from os import getenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from api import envars

app = Flask(__name__)
app.config["SECRET_KEY"] = getenv('SECRET_KEY')
app.config["SQLALCHEMY_DATABASE_URI"] = getenv('SQLALCHEMY_DATABASE_URI')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

db.create_all()
db.session.commit()

from .init_amo import client

AMO = client()
PIPELINE = 3944278

from api import routes
