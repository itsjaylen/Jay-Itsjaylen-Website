from flask import Blueprint

api = Blueprint('api', __name__, url_prefix='/api', template_folder="./templates/", static_folder="./static/")

from app.api import routes

