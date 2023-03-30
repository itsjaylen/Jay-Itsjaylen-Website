from flask import Blueprint

bp = Blueprint('docs', __name__, url_prefix='/docs', template_folder="./templates/", static_folder="./static/")


from app.docs import routes
