from app.extensions import db


class TwitchMessages(db.Model):
    __tablename__ = 'twitchmessages'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String(20), nullable=False)
    channel = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    message = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return f"Message('{self.timestamp}', '{self.channel}', '{self.username}', '{self.message}', '{self.hashed_message}')"


class TwitchUsers(db.Model):
    __tablename__ = 'twitchusers'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    message_count = db.Column(db.Integer, default=0, nullable=False)
    average_message_length = db.Column(db.Integer, default=0, nullable=False)
    daily_average_message_count = db.Column(db.Integer, default=0, nullable=False)


class TwitchChannels(db.Model):
    __tablename__ = 'twitchchannels'
    id = db.Column(db.Integer, primary_key=True)
    channel = db.Column(db.String(50), nullable=False)
    message_count = db.Column(db.Integer, default=0, nullable=False)
