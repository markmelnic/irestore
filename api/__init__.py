from api.telegram_api import TelegramBot
from os import getenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from api import envars
from .shopify_api import Shopify

app = Flask(__name__)
app.config["SECRET_KEY"] = getenv('SECRET_KEY')
app.config["SQLALCHEMY_DATABASE_URI"] = getenv('SQLALCHEMY_DATABASE_URI')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

from .models import *

db.create_all()
db.session.commit()

if not Tokens.query.first():
    db.session.add(Tokens())

from .init_amo import client

AMO = client()
PIPELINE = 3944278

SPF = Shopify(
        getenv('SPF_USER'),
        getenv('SPF_PASS'),
        getenv('SPF_SITE'),
        getenv('SPF_HEAD')
    )

TELEGRAM = TelegramBot(getenv('TELEGRAM_TOKEN'))

from api import routes
