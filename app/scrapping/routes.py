from app.scrapping import bp
from flask import render_template

from app.scrapping.tools.YoutubeScrapping import get_videos

#TODO ADD THE SCRAPER UNDER HERE
@bp.route('/')
async def scrap():
    return render_template('ScrapMain.html')

@bp.route("/video/<path:filename>")
def videos(filename):
    return render_template('videos.html', video_file=filename)
