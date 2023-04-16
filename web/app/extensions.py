from flask_admin import Admin
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
from flask_caching import Cache
#from flask_migrate import Migrate


db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
admin = Admin()
scheduler = APScheduler()
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})
#migrate = Migrate()