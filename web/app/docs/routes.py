from flask import render_template, jsonify
from app.docs import bp
import time
import datetime

@bp.route('/')
async def docs():
    return render_template('docs.html')


@bp.route('/time')
def get_time():
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return jsonify({'time': current_time})