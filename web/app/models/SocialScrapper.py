from app.extensions import db

#TODO get a base on this
class SocialMedia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    twitter = db.Column(db.String(255), unique=True, nullable=True)
    instagram = db.Column(db.String(255), unique=True, nullable=True)
    tiktok = db.Column(db.String(255), unique=True, nullable=True)
    YouTube = db.Column(db.String(255), unique=True, nullable=True)
    Twitch = db.Column(db.String(255), unique=True, nullable=True)