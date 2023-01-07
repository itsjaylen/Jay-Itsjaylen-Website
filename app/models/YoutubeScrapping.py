from app.extensions import db 


class YoutubeChannels(db.Model):
    youtube_channel_id = db.Column(
        db.String(255), unique=True, primary_key=True)


class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    publish_date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text, nullable=False)
    views = db.Column(db.Integer, nullable=False)
    length = db.Column(db.Integer, nullable=False)
