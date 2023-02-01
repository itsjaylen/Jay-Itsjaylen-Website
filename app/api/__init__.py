from flask import Blueprint

api = Blueprint('api', __name__, url_prefix='/api', template_folder="./templates/")

from app.api import routes

