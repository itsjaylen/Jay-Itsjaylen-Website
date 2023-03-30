from app.extensions import db


class YoutubeChannels(db.Model):
    """Youtube Channels to scrape."""
    __tablename__ = 'youtubechannels'
    id = db.Column(
        db.Integer, unique=True, primary_key=True)
    youtube_channel_id = db.Column(
        db.String(255), unique=True, nullable=False)


class Video(db.Model):
    """Model for youtube video data."""
    __tablename__ = 'video'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.Text, nullable=False)
    title = db.Column(db.Text, nullable=False)
    author = db.Column(db.Text, nullable=False)
    publish_date = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    views = db.Column(db.Integer, nullable=False)
    length = db.Column(db.Float, nullable=False)