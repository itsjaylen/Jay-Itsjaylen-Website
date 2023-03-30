import asyncio
import concurrent.futures
import threading
import multiprocessing

from apscheduler.triggers.cron import CronTrigger
from flask import Flask

from app.api import api as api_bp
from app.docs import bp as docs_bp
from app.api.tools.apitool import update_user_stats
from app.auth import bp as auth_bp
from app.commands import configure_cli
from app.extensions import admin, bcrypt, cache, db, login_manager, migrate, scheduler
from app.main import bp as main_bp
from app.models.account import Controller, User
from app.models.YoutubeScrapping import Video, YoutubeChannels
from app.scrapping import bp as scrapping_bp
from app.scrapping.tools.tasks import configure_tasks
from app.scrapping.tools.YoutubeScrapping import YoutubeScraper
from config import Config


# TDDO automate creating database
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.app_context().push()

    # Define a filter function
    def level_filter(record):
        return app.debug and record["level"].name in ["DEBUG", "INFO", "ERROR"]

    # Initialize Flask extensions here
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    admin.init_app(app)
    configure_tasks(app)
    scheduler.init_app(app)
    cache.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = "login"
    login_manager.login_message = "Please log in to access this page."

    scraper = YoutubeScraper()
    # Threaded scheduler TODO add better configs
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # scheduler.add_job(deactivate_inactive_accounts, "interval", seconds=604800)

            if Config.SCRAPPING_ENABLED == True:
                executor.submit(
                    scheduler.add_job,
                    id="video_function",
                    func=scraper.video_function,
                    trigger=CronTrigger(hour="*", minute="0", second="0"),
                    args=[app, db],
                )

                executor.submit(scheduler.start)

    except Exception as e:
        print(e)



    # Register blueprints here
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(scrapping_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(docs_bp)

    # TODO COMPLETELY REDO THE ADMIN PANEL
    admin.add_view(Controller(User, db.session, name="Users", endpoint="users"))
    admin.add_view(
        Controller(
            YoutubeChannels,
            db.session,
            name="Youtube Channels",
            endpoint="youtube_channels",
        )
    )
    admin.add_view(Controller(Video, db.session, name="Videos", endpoint="videos"))

    # Register custom commands here
    configure_cli(app)

    return app