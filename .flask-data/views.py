import asyncio
import sys
import time

from flask import (Flask, Response, flash, redirect, render_template, request,
                   url_for)
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_apscheduler import APScheduler
from flask_bcrypt import Bcrypt
from flask_login import (LoginManager, UserMixin, current_user, login_required,
                         login_user, logout_user)
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from loguru import logger
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError

from util.FlaskDev import GetToDoList
from util.scraper import get_subs_from_tracker, get_tweets, scrap_twitch
from util.youtube_video_download import get_videos, video_function

logger.add(sys.stderr,
           format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
           filter="my_module",
           level="INFO",
           enqueue=True,
           backtrace=True,
           diagnose=True,)
logger.add("lastest.log", rotation="500 MB", compression="zip")


app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db?check_same_thread=False'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = "secret"
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # type: ignore


class Config:
    """App configuration."""

    SCHEDULER_API_ENABLED = True


scheduler = APScheduler()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):  # type: ignore
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)


admin = Admin(app, name='Jaylen Site', template_mode='bootstrap4')
admin.add_view(ModelView(User, db.session))


class RegisterForm(FlaskForm):
    username = StringField(label="Username", validators=[DataRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(label="Password", validators=[DataRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField(label="Register")

    def validate_username(self, username):
        existing_user_name = User.query.filter_by(
            username=username.data).first()
        if existing_user_name:
            raise ValidationError(
                "Username already exists. Please choose a different one.")


class LoginForm(FlaskForm):
    username = StringField(label="Username", validators=[DataRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(label="Password", validators=[DataRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField(label="Login")


@logger.catch
@scheduler.task("interval", id="do_job_1", minutes=45)
def job1():
    """Sample job 1."""
    #get_videos()
    video_function()


@app.route("/")
@app.route("/home/")
async def index():
    return render_template("index.html")


@app.route("/dev/dev/")
async def dev():
    return render_template("/dev/dev.html")


@app.route("/dev/dev-A/")
async def dev_():
    tweets = await get_tweets()
    return render_template("/dev/dev1.html", tweets=tweets)


@app.route("/dashboard/", methods=["GET", "POST"])
@login_required
async def dashboard():
    return render_template("/account/dashboard.html")


@app.route("/logout/", methods=["GET", "POST"])
@login_required
async def logout():
    logout_user()
    flash("You have been logged out.", category="info")
    return redirect(url_for("index"))


@app.route("/login/", methods=["GET", "POST"])
async def login():
    if current_user.is_authenticated:  # type: ignore
        return redirect(url_for("dashboard"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for("dashboard"))
        else:
            flash("Login Unsuccessful. Please check username and password", "danger")

    return render_template("/account/login.html", form=form)


@app.route("/register/", methods=["GET", "POST"])
async def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))

    return render_template("/account/register.html", form=form)


@app.route("/misc/pocket-watch/")
async def pocket_watch():
    kai_subs = get_subs_from_tracker("KaiCenat")
    rage_subs = get_subs_from_tracker("yourragegaming")
    return render_template("/misc/Pocket-Watch.html", kai_subs=(format(int(kai_subs), ',d')), rage_subs=rage_subs)


@app.route("/dev/todo/")
async def todo():
    GetToDoList()
    return render_template("todo.html", todo_list=GetToDoList())


@app.route("/dynamic_page/<channel>")
async def dynamic_page(channel):
    return get_subs_from_tracker(channel)


@app.route("/dynamic_page2/")
async def dynamic_page2():
    return scrap_twitch()


@app.errorhandler(404)
async def not_found(e):
    return render_template("404.html")


@app.route("/projects/")
async def projects():
    return render_template("projects.html")


@app.route("/about/")
async def about():
    return render_template("about.html")


@app.route('/webhook', methods=['POST'])  # type: ignore
async def return_response():
    print(request.json)
    return Response(status=200)


@app.route("/misc/video-scraping/")
async def video_scraping():
    return render_template("/misc/video-scraping.html", videos=get_videos())


app.config.from_object(Config())

# it is also possible to enable the API directly
# scheduler.api_enabled = True  # noqa: E800
scheduler.init_app(app)
scheduler.start()
