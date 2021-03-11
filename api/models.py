from api import db

class Tokens(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    access_token = db.Column(db.String(255), default="")
    refresh_token = db.Column(db.String(255), default="")

class TelegramUsers(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer)
    status = db.Column(db.Boolean, default=True)
