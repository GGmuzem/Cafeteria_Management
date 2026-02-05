from flask import render_template, request, redirect, url_for
from flask_login import login_required, current_user, logout_user
from . import auth_bp
from .services import login_user_db, register_user

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_data = request.form.get("login")
        password_data = request.form.get("password")

        if login_user_db(login_data, password_data):
            return redirect(url_for("auth.account"))

        return "Неверный логин или пароль"

    return render_template("auth/login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        login_data = request.form.get("login")
        password_data = request.form.get("password")
        password_repeat = request.form.get("confirm_password")

        user = register_user(login_data, password_data, password_repeat)
        if user:
            return redirect(url_for("auth.account"))
        return "Ошибка регистрации"
    return render_template("auth/register.html")

@auth_bp.route("/account", methods=["GET", "POST"])
@login_required
def account():
    if request.method == "POST":
        if "email" in request.form:
            current_user.email = request.form.get("email")
        if "allergen" in request.form:
            current_user.allergen = request.form.get("allergen")
        if "preferences" in request.form:
            current_user.preferences = request.form.get("preferences")
        
        from config import db
        db.session.commit()
        return redirect(url_for("auth.account"))

    return render_template(
        "auth/account.html",
        user=current_user,
        wallet=current_user.get_wallet()
    )

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
