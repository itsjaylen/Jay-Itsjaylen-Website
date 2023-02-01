from flask import Blueprint

bp = Blueprint('scrapping', __name__, url_prefix='/scrapping', template_folder="./templates/", static_folder="./static/")


from app.scrapping import routes
