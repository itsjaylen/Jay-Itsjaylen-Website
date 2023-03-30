import sqlalchemy
from sqlalchemy import orm


DATABASE_URL = "postgresql://postgres:password@192.168.240.2:5432/flaskappmain"


engine = sqlalchemy.create_engine(DATABASE_URL)
Session = sqlalchemy.orm.sessionmaker(bind=engine)

def get_session():
    return Session()
