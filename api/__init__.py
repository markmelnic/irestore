from os import getenv
from flask import Flask
from .init_amo import client
from .envars import *
from .init_amo import client

app = Flask(__name__)

AMO = client()
PIPELINE = 3944278

from api import routes
