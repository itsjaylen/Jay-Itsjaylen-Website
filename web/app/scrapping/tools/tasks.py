from app.scrapping import bp
from app.extensions import scheduler, db
import asyncio


def configure_tasks(app):
    @scheduler.task('interval', id='scrape_videos', minutes=5,)
    def scrape_channels():
       pass
    
    

