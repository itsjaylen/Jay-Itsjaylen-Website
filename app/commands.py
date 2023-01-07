from app.extensions import db
from os import system


def configure_cli(app):

    @app.cli.command()
    def initdb():
        db.drop_all()
        db.create_all()
        
    @app.cli.command()
    def build():
        system("pip install -r requirements.txt")
        
    @app.cli.command()
    def deploy():
        print("deploy")