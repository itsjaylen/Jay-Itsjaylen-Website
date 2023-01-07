from flask import Blueprint

bp = Blueprint('scrapping', __name__, template_folder="./templates/", static_folder="./static/")


from app.scrapping import routes
