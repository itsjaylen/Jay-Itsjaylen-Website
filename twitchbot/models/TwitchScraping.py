import sqlalchemy as db
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class TwitchMessages(Base):
    __tablename__ = 'twitchmessages'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String(20), nullable=False)
    channel = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    message = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return f"TwitchMessages('{self.timestamp}', '{self.channel}', '{self.username}', '{self.message}')"
    
class TwitchMessagesLegacy(Base):
    __tablename__ = 'twitchmessageslegacy'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String(20), nullable=False)
    channel = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    hashed_message = db.Column(db.String(64), nullable=False)

class TwitchUsers(Base):
    __tablename__ = 'twitchusers'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    message_count = db.Column(db.Integer, default=0, nullable=False)
    average_message_length = db.Column(db.Integer, default=0, nullable=False)
    role = db.Column(db.String(50), default='user', nullable=False)
    daily_average_message_count = db.Column(db.Integer, default=0, nullable=False)


class TwitchChannels(Base):
    __tablename__ = 'twitchchannels'

    id = db.Column(db.Integer, primary_key=True)
    channel = db.Column(db.String(50), nullable=False)
    message_count = db.Column(db.Integer, default=0, nullable=False)

