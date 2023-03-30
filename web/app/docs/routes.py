from flask import render_template
from app.docs import bp

@bp.route('/')
async def docs():
    return render_template('docs.html')

