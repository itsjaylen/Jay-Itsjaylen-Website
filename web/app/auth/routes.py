from flask import flash, redirect, render_template, url_for, request
from flask_admin import BaseView, expose
from flask_login import current_user, login_required, login_user, logout_user
import hashlib

from app.auth import bp
from app.extensions import bcrypt, db
from app.models.account import LoginForm, RegisterForm, User


@bp.route("/login/", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:  # type: ignore
        return redirect(url_for("auth.dashboard"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        email = request.form.get("email")
        password = request.form.get("password")

        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for("auth.dashboard"))
        else:
            flash("Login Unsuccessful. Please check username and password", "danger")

    return render_template("login.html", form=form)


#TODO make one invisible hash method
@bp.route("/register/", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        hash_object = hashlib.sha256()
        hash_object.update(form.username.data.encode())
        hash_object.update(form.password.data.encode())
        api_key = hash_object.hexdigest()
        new_user = User(
            username=form.username.data, password=hashed_password, api_key=api_key
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Your account has been created! You are now able to log in", "success")
        return redirect(url_for("auth.login"))

    return render_template("/register.html", form=form)


@bp.route("/logout/", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", category="info")
    return redirect(url_for("main.home"))


@bp.route("/dashboard/", methods=["GET", "POST"])
@login_required
def dashboard():
    if current_user.is_authenticated:
        return render_template("dashboard.html", id=current_user.id)

    else:
        return "Not logged in"


@bp.route("/dashboard/settings/", methods=["GET", "POST"])
@login_required
def settings():
    return render_template("settings.html", id=current_user.id)


@bp.route("/dashboard/stats/", methods=["GET", "POST"])
@login_required
def stats():
    return render_template("stats.html", id=current_user.id)


class CustomAdmin(BaseView):
    @expose("/")
    def index(self):
        return self.render("/admin/CustomAdmin.html")
