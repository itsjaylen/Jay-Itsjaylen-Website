from app.extensions import db
from os import system


def configure_cli(app):

    @app.cli.command()
    def initdb():
        db.drop_all()
        db.create_all()