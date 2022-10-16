from flask import Flask, flash, redirect, render_template, url_for
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_bcrypt import Bcrypt
from flask_login import (LoginManager, UserMixin, current_user, login_required,
                         login_user, logout_user)
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError

from util.FlaskDev import GetToDoList
from util.scraper import get_subs_from_tracker, is_live, scrap_twitch

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = "secret"
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
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


@app.route("/")
@app.route("/home/")
def index():
    return render_template("index.html")


@app.route("/dev/dev/")
def dev():
    return render_template("dev.html")


@app.route("/dev/dev-A/")
def dev_():
    subs = get_subs_from_tracker("adinross")
    return render_template("dev1.html", subs=subs)


@app.route("/dashboard/", methods=["GET", "POST"])
@login_required
def dashboard():
    return render_template("dashboard.html")


@app.route("/logout/", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", category="info")
    return redirect(url_for("index"))


@app.route("/login/", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
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

    return render_template("login.html", form=form)


@app.route("/register/", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))

    return render_template("register.html", form=form)


@app.route("/misc/pocket-watch/")
def pocket_watch():
    kai_subs = get_subs_from_tracker("KaiCenat")
    rage_subs = get_subs_from_tracker("yourragegaming")
    return render_template("Pocket-Watch.html", kai_subs=(format(int(kai_subs), ',d')), rage_subs=rage_subs)


@app.route("/dev/todo/")
def todo():
    GetToDoList()
    return render_template("todo.html", todo_list=GetToDoList())


@app.route("/dynamic_page/<channel>")
def dynamic_page(channel):
    return get_subs_from_tracker(channel)


@app.route("/dynamic_page2/")
def dynamic_page2():
    return scrap_twitch()
