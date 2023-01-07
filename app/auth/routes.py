from flask import flash, redirect, render_template, url_for, request
from flask_admin import BaseView, expose
from flask_login import current_user, login_required, login_user, logout_user

from app.auth import bp
from app.extensions import bcrypt, db
from app.models.account import LoginForm, RegisterForm, User


@bp.route("/login/", methods=["GET", "POST"])
async def login():
    if current_user.is_authenticated:  # type: ignore
        return redirect(url_for("auth.dashboard"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        email = request.form.get('email')
        password = request.form.get('password')
        
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for("auth.dashboard"))
        else:
            flash("Login Unsuccessful. Please check username and password", "danger")

    return render_template("login.html", form=form)




@bp.route("/register/", methods=["GET", "POST"])
async def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('auth.login'))

    return render_template("/register.html", form=form)


@bp.route("/logout/", methods=["GET", "POST"])
@login_required
async def logout():
    logout_user()
    flash("You have been logged out.", category="info")
    return redirect(url_for("main.home"))


@bp.route("/dashboard/", methods=["GET", "POST"])
@login_required
async def dashboard():
    return render_template("dashboard.html", id=current_user.id)


class CustomAdmin(BaseView):
    @expose('/')
    def index(self):
        return self.render('/admin/CustomAdmin.html')
    