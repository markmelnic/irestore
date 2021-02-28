import time

from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello():
    count = 0
    return 'Hello World! I have been seen {} times.\n'.format(count)



