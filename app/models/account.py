from flask import abort
from flask_admin.contrib.sqla import ModelView
from flask_login import UserMixin, current_user
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError

from app.extensions import db, login_manager


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean(), default=True)
    is_admin = db.Column(db.Boolean(), default=False)

    def __repr__(self):
        return f'<Post "{self.username}">'


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


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class Controller(ModelView):
    def is_accessible(self):
        if current_user.is_admin is True:
            return current_user.is_authenticated
        else:
            return abort(404)
        # return current_user.is_authenticated

    def not_auth(self):
        return "You are not authorized to view this page."
