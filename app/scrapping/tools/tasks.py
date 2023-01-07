from app.scrapping.tools.youtube import video_function
from extensions import scheduler
import asyncio

@scheduler.task('interval', id='do_async_task', minutes=45)
def async_task():
    asyncio.run(video_function())