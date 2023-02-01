"""Account management models."""
from flask import abort
from flask_admin.contrib.sqla import ModelView
from flask_login import UserMixin, current_user
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from datetime import datetime

from app.extensions import db, login_manager


#TODO add more roles
class User(db.Model, UserMixin):
    """
    User account model.
    This class represents the User object and its attributes, which are mapped to columns in a database table using SQLAlchemy.

    Args:
        db.Model: base class for all models.
        UserMixin: provides basic user authentication methods.
    Attributes:
        id (db.Integer): primary key, unique identifier for each user.
        email (db.String): unique email address of the user.
        username (db.String): unique username of the user.
        password (db.String): hashed password of the user.
        active (db.Boolean): status of the user, whether the user is active or not. default is True.
        api_key (db.String): unique api key of the user.
        request_count (db.Integer): number of requests made by the user. default is 0.
        last_request_time (db.DateTime): timestamp of the last request made by the user.
        is_admin (db.Boolean): status of the user, whether the user is admin or not. default is False.
    """

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(255))
    is_admin = db.Column(db.Boolean(), default=False)
    role = db.Column(db.String(20), default="Normal")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    active = db.Column(db.Boolean(), default=True)
    api_key = db.Column(db.String(255), unique=True)
    request_count = db.Column(db.Integer, default=0)
    total_request_count = db.Column(db.Integer, default=0)
    last_request_time = db.Column(db.DateTime)


class RegisterForm(FlaskForm):
    username = StringField(
        label="Username",
        validators=[DataRequired(), Length(min=4, max=20)],
        render_kw={"placeholder": "Username"},
    )
    password = PasswordField(
        label="Password",
        validators=[DataRequired(), Length(min=4, max=20)],
        render_kw={"placeholder": "Password"},
    )
    submit = SubmitField(label="Register")

    def validate_username(self, username):
        existing_user_name = User.query.filter_by(username=username.data).first()
        if existing_user_name:
            raise ValidationError(
                "Username already exists. Please choose a different one."
            )


class LoginForm(FlaskForm):
    username = StringField(
        label="Username",
        validators=[DataRequired(), Length(min=4, max=20)],
        render_kw={"placeholder": "Username"},
    )
    password = PasswordField(
        label="Password",
        validators=[DataRequired(), Length(min=4, max=20)],
        render_kw={"placeholder": "Password"},
    )
    submit = SubmitField(label="Login")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class Controller(ModelView):
    """The admin controller"""

    def is_accessible(self):
        if current_user.is_authenticated:
            if current_user.is_admin is True:
                return current_user.is_authenticated
            else:
                return abort(404)
            # return current_user.is_authenticated
        else:
            return abort(404)

    def not_auth(self):
        return "You are not authorized to view this page."
