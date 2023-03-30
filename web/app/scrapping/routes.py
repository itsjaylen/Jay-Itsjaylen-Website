from app.models.TwitchScrapper import TwitchMessages
from app.scrapping import bp
from flask import render_template, request

from app.scrapping.tools.YoutubeScrapping import get_videos
from app.scrapping.tools.TwitchScrapping import generate_top_users_graph

#TODO ADD THE SCRAPER UNDER HERE
@bp.route('/')
async def scrap():
    return render_template('ScrapMain.html')

@bp.route("/video/<path:filename>")
def videos(filename):
    return render_template('videos.html', video_file=filename)

from flask import render_template

@bp.route('/top_users')
def top_users():
    # Generate the graph and save it as an image file
    generate_top_users_graph()

    # Render an HTML template that includes the image
    return render_template('top_users.html')

