from flask import render_template
from app.main import bp

#TDOD MAKE THESE UNIVERSAL
@bp.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404


@bp.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403


@bp.errorhandler(413)
def request_entity_too_large(e):
    return render_template('errors/413.html'), 413


@bp.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500


@bp.route('/')
def home():
    return render_template('index.html')


@bp.route('/about')
def about():
    return render_template('about.html')
