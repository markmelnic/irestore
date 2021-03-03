from api import db

class Tokens(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    access_token = db.Column(db.String, default="")
    refresh_token = db.Column(db.String, default="")
