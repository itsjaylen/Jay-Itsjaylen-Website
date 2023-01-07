from app.scrapping import bp
from flask import render_template

@bp.route('/')
async def thug():
    return render_template('scrap.html')