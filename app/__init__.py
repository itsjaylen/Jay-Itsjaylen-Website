from flask import Flask
from app.commands import configure_cli
from app.extensions import admin, bcrypt, db, login_manager, scheduler
from app.models.account import Controller, User
from config import Config


#TDDO automate creating database
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask extensions here
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'

    admin.init_app(app)

    scheduler.init_app(app)
    scheduler.start()

    # Register blueprints here
    from app.main import bp as main_bp
    app.register_blueprint(main_bp, url_prefix='/')

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.scrapping import bp as scrapping_bp
    app.register_blueprint(scrapping_bp, url_prefix='/scrapping')

    admin.add_view(Controller(User, db.session,
                   name='Users', endpoint='users'))
    
    
    
    # Register custom commands here
    configure_cli(app)
    
    return app


